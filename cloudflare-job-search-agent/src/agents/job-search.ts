import { Agent, callable } from "agents";
import portals from "./job-search.portals.json";

// ── Types ───────────────────────────────────────────────────────────

type Company = {
  name: string;
  careers_url?: string;
  api?: string;
  enabled?: boolean;
};

type KeywordFilter = {
  positive?: string[];
  negative?: string[];
};

type PortalsConfig = {
  tracked_companies: Company[];
  title_filter?: KeywordFilter;
  location_filter?: KeywordFilter;
};

type ApiType = "greenhouse" | "ashby" | "lever";

type DetectedApi = {
  type: ApiType;
  url: string;
};

type Target = {
  company: Company;
  api: DetectedApi;
};

type Offer = {
  title: string;
  url: string;
  company: string;
  location: string;
};

type ScanError = {
  company: string;
  error: string;
};

type JobSearchState = {
  lastRunAt: string | null;
  lastRunNewCount: number;
};

/** Passed between chunked scan invocations. */
type ScanProgress = {
  cursor: number;
  isFirstRun: boolean;
};

const CONFIG = portals as PortalsConfig;
const CONCURRENCY = 8;
const FETCH_TIMEOUT_MS = 10_000;

/**
 * Companies scanned per invocation. Each scan makes one fetch per company
 * (and one for the email on the final chunk), so this stays well under the
 * Workers free-plan limit of 50 subrequests per invocation. The scan
 * continues itself across as many invocations as needed.
 */
const CHUNK_SIZE = 40;

// ── Agent ───────────────────────────────────────────────────────────

export class JobSearchAgent extends Agent<Env, JobSearchState> {
  initialState: JobSearchState = {
    lastRunAt: null,
    lastRunNewCount: 0
  };

  /**
   * Entry point — invoked by the weekly cron and the manual HTTP route.
   * Resets the run accumulator and kicks off the first scan chunk. The scan
   * then continues itself chunk by chunk (see runScanChunk).
   */
  @callable()
  async runWeeklyScan(): Promise<{ status: string; companies: number; chunkSize: number }> {
    this.ensureTables();
    this.sql`DELETE FROM pending_offers`;

    const isFirstRun = this.state.lastRunAt === null;
    const companies = buildTargets().length;

    await this.schedule(2, "runScanChunk", { cursor: 0, isFirstRun });

    return { status: "scan_scheduled", companies, chunkSize: CHUNK_SIZE };
  }

  /**
   * Scans one chunk of companies into the pending_offers accumulator, then
   * either schedules the next chunk or finalizes the run. Invoked by the
   * agent scheduler — not called directly.
   */
  async runScanChunk(progress: ScanProgress): Promise<void> {
    this.ensureTables();

    const cursor = progress?.cursor ?? 0;
    const isFirstRun = progress?.isFirstRun ?? this.state.lastRunAt === null;

    const targets = buildTargets();
    const slice = targets.slice(cursor, cursor + CHUNK_SIZE);

    const titleFilter = buildTitleFilter(CONFIG.title_filter);
    const locationFilter = buildLocationFilter(CONFIG.location_filter);

    const seen = new Set<string>([
      ...this.sql<{ url: string }>`SELECT url FROM seen_jobs`.map((row) => row.url),
      ...this.sql<{ url: string }>`SELECT url FROM pending_offers`.map((row) => row.url)
    ]);

    let found = 0;
    let newCount = 0;
    const errors: ScanError[] = [];

    const tasks = slice.map((target) => async () => {
      try {
        const json = await fetchJson(target.api.url);
        const jobs = PARSERS[target.api.type](json, target.company.name);
        found += jobs.length;

        for (const job of jobs) {
          if (!titleFilter(job.title)) continue;
          if (!locationFilter(job.location, job.title)) continue;
          if (seen.has(job.url)) continue;
          seen.add(job.url);
          this.sql`INSERT OR IGNORE INTO pending_offers (url, title, company, location)
            VALUES (${job.url}, ${job.title}, ${job.company}, ${job.location})`;
          newCount++;
        }
      } catch (err) {
        errors.push({
          company: target.company.name,
          error: err instanceof Error ? err.message : String(err)
        });
      }
    });

    await parallelFetch(tasks, CONCURRENCY);

    const chunkNumber = Math.floor(cursor / CHUNK_SIZE) + 1;
    const totalChunks = Math.max(1, Math.ceil(targets.length / CHUNK_SIZE));
    console.log(
      `[JobSearchAgent] chunk ${chunkNumber}/${totalChunks}: scanned ${slice.length}, found ${found}, new ${newCount}, errors ${errors.length}` +
        (errors.length ? ` (${errors.map((e) => e.company).join(", ")})` : "")
    );

    const nextCursor = cursor + CHUNK_SIZE;
    if (nextCursor < targets.length) {
      await this.schedule(3, "runScanChunk", { cursor: nextCursor, isFirstRun });
      return;
    }

    await this.finalizeRun(isFirstRun);
  }

  /**
   * Emails the accumulated offers and commits them to the seen history.
   * Email is sent BEFORE seen_jobs is updated — if email fails the run will
   * retry cleanly next week rather than silently swallowing the notification.
   */
  private async finalizeRun(isFirstRun: boolean): Promise<void> {
    const offers = this.sql<Offer>`SELECT url, title, company, location FROM pending_offers`;

    if (isFirstRun) {
      await this.sendAlertEmail(
        `Job agent activated — tracking ${offers.length} open roles`,
        seedEmailHtml(offers.length, buildTargets().length)
      );
    } else if (offers.length > 0) {
      await this.sendAlertEmail(
        `${offers.length} new job${offers.length === 1 ? "" : "s"} this week`,
        jobsEmailHtml(offers)
      );
    }

    const date = new Date().toISOString().slice(0, 10);
    for (const offer of offers) {
      this.sql`INSERT OR IGNORE INTO seen_jobs (url, first_seen, title, company)
        VALUES (${offer.url}, ${date}, ${offer.title}, ${offer.company})`;
    }

    this.setState({
      lastRunAt: new Date().toISOString(),
      lastRunNewCount: offers.length
    });

    this.sql`DELETE FROM pending_offers`;

    console.log(
      `[JobSearchAgent] run complete: ${isFirstRun ? "seeded" : "emailed"} ${offers.length} offers`
    );
  }

  private ensureTables(): void {
    this.sql`CREATE TABLE IF NOT EXISTS seen_jobs (
      url TEXT PRIMARY KEY,
      first_seen TEXT NOT NULL,
      title TEXT,
      company TEXT
    )`;
    this.sql`CREATE TABLE IF NOT EXISTS pending_offers (
      url TEXT PRIMARY KEY,
      title TEXT,
      company TEXT,
      location TEXT
    )`;
  }

  private async sendAlertEmail(subject: string, html: string): Promise<void> {
    const apiKey = this.env.RESEND_API_KEY;
    const to = this.env.JOB_ALERT_TO;
    const from = this.env.JOB_ALERT_FROM ?? "onboarding@resend.dev";

    if (!apiKey || !to) {
      throw new Error("Missing email config. Set RESEND_API_KEY and JOB_ALERT_TO.");
    }

    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ from, to, subject, html })
    });

    if (!response.ok) {
      throw new Error(`Resend request failed: ${response.status} ${await response.text()}`);
    }
  }
}

// ── Targets ─────────────────────────────────────────────────────────

function buildTargets(): Target[] {
  return (CONFIG.tracked_companies ?? [])
    .filter((company) => company.enabled !== false)
    .map((company) => ({ company, api: detectApi(company) }))
    .filter((target): target is Target => target.api !== null);
}

// ── API detection ───────────────────────────────────────────────────

function detectApi(company: Company): DetectedApi | null {
  if (company.api && company.api.includes("greenhouse")) {
    return { type: "greenhouse", url: company.api };
  }

  const url = company.careers_url ?? "";

  const ashbyMatch = url.match(/jobs\.ashbyhq\.com\/([^/?#]+)/);
  if (ashbyMatch) {
    return {
      type: "ashby",
      url: `https://api.ashbyhq.com/posting-api/job-board/${ashbyMatch[1]}?includeCompensation=true`
    };
  }

  const leverMatch = url.match(/jobs\.lever\.co\/([^/?#]+)/);
  if (leverMatch) {
    return { type: "lever", url: `https://api.lever.co/v0/postings/${leverMatch[1]}` };
  }

  const ghEuMatch = url.match(/job-boards(?:\.eu)?\.greenhouse\.io\/([^/?#]+)/);
  if (ghEuMatch && !company.api) {
    return {
      type: "greenhouse",
      url: `https://boards-api.greenhouse.io/v1/boards/${ghEuMatch[1]}/jobs`
    };
  }

  return null;
}

// ── API parsers ─────────────────────────────────────────────────────

type GreenhouseJob = { title?: string; absolute_url?: string; location?: { name?: string } };
type AshbyJob = { title?: string; jobUrl?: string; location?: string };
type LeverJob = { text?: string; hostedUrl?: string; categories?: { location?: string } };

function parseGreenhouse(json: unknown, company: string): Offer[] {
  const jobs = (json as { jobs?: GreenhouseJob[] })?.jobs ?? [];
  return jobs.map((job) => ({
    title: job.title ?? "",
    url: job.absolute_url ?? "",
    company,
    location: job.location?.name ?? ""
  }));
}

function parseAshby(json: unknown, company: string): Offer[] {
  const jobs = (json as { jobs?: AshbyJob[] })?.jobs ?? [];
  return jobs.map((job) => ({
    title: job.title ?? "",
    url: job.jobUrl ?? "",
    company,
    location: job.location ?? ""
  }));
}

function parseLever(json: unknown, company: string): Offer[] {
  if (!Array.isArray(json)) return [];
  return (json as LeverJob[]).map((job) => ({
    title: job.text ?? "",
    url: job.hostedUrl ?? "",
    company,
    location: job.categories?.location ?? ""
  }));
}

const PARSERS: Record<ApiType, (json: unknown, company: string) => Offer[]> = {
  greenhouse: parseGreenhouse,
  ashby: parseAshby,
  lever: parseLever
};

// ── Fetch with timeout ──────────────────────────────────────────────

async function fetchJson(url: string): Promise<unknown> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      signal: controller.signal,
      headers: {
        "User-Agent": "JobSearchAgent/0.1 (+https://developers.cloudflare.com/agents/)"
      }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    clearTimeout(timer);
  }
}

// ── Filters (ported from career-ops/scan.mjs) ───────────────────────

function buildTitleFilter(filter: KeywordFilter | undefined): (title: string) => boolean {
  const positive = (filter?.positive ?? []).map((keyword) => keyword.toLowerCase());
  const negative = (filter?.negative ?? []).map((keyword) => keyword.toLowerCase());

  return (title) => {
    const lower = title.toLowerCase();
    const hasPositive = positive.length === 0 || positive.some((keyword) => keywordMatches(lower, keyword));
    const hasNegative = negative.some((keyword) => keywordMatches(lower, keyword));
    return hasPositive && !hasNegative;
  };
}

function buildLocationFilter(
  filter: KeywordFilter | undefined
): (location: string, title?: string) => boolean {
  const positive = (filter?.positive ?? []).map((keyword) => keyword.toLowerCase());
  const negative = (filter?.negative ?? []).map((keyword) => keyword.toLowerCase());

  return (location, title = "") => {
    const lower = `${title} ${location}`.toLowerCase();
    const hasPositive = positive.length === 0 || positive.some((keyword) => keywordMatches(lower, keyword));
    const hasNegative = negative.some((keyword) => keywordMatches(lower, keyword));
    return hasPositive && !hasNegative;
  };
}

function keywordMatches(text: string, keyword: string): boolean {
  const escaped = escapeRegExp(keyword);
  const prefix = /^[a-z0-9]/i.test(keyword) ? "(?<![a-z0-9])" : "";
  const suffix = /[a-z0-9]$/i.test(keyword) ? "(?![a-z0-9])" : "";
  return new RegExp(`${prefix}${escaped}${suffix}`, "i").test(text);
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// ── Parallel fetch with concurrency limit ───────────────────────────

async function parallelFetch(tasks: Array<() => Promise<void>>, limit: number): Promise<void> {
  let index = 0;

  async function worker(): Promise<void> {
    while (index < tasks.length) {
      const task = tasks[index++];
      await task();
    }
  }

  await Promise.all(Array.from({ length: Math.min(limit, tasks.length) }, () => worker()));
}

// ── Email rendering ─────────────────────────────────────────────────

function seedEmailHtml(roleCount: number, companyCount: number): string {
  return `<div style="font-family:system-ui,sans-serif;max-width:640px;line-height:1.5">
<p>Your weekly job-search agent is live.</p>
<p>It scanned <strong>${companyCount}</strong> company portals and is now tracking
<strong>${roleCount}</strong> open roles that match your criteria. From next week on you'll
only get an email when <em>new</em> matching roles appear.</p>
</div>`;
}

function jobsEmailHtml(offers: Offer[]): string {
  const byCompany = new Map<string, Offer[]>();
  for (const offer of offers) {
    const list = byCompany.get(offer.company) ?? [];
    list.push(offer);
    byCompany.set(offer.company, list);
  }

  const sections = [...byCompany.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([company, list]) => {
      const rows = list
        .map((offer) => {
          const location = offer.location ? ` — ${escapeHtml(offer.location)}` : "";
          return `<li><a href="${escapeHtml(offer.url)}">${escapeHtml(offer.title)}</a>${location}</li>`;
        })
        .join("");
      return `<h3 style="margin:18px 0 4px">${escapeHtml(company)}</h3><ul style="margin:0;padding-left:20px">${rows}</ul>`;
    })
    .join("");

  return `<div style="font-family:system-ui,sans-serif;max-width:640px;line-height:1.5">
<p><strong>${offers.length}</strong> new role${offers.length === 1 ? "" : "s"} matched your criteria this week.</p>
${sections}
<p style="color:#888;font-size:12px;margin-top:24px">Sent by your JobSearchAgent. Evaluate these in the career-ops pipeline.</p>
</div>`;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
