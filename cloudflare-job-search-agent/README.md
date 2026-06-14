# Cloudflare Job Search Agent

A weekly cron agent that scrapes Greenhouse / Ashby / Lever job boards, deduplicates against history, and emails you only the new matching roles. Built on Cloudflare Workers + Agents SDK (Durable Objects with SQLite).

**No LLM** — pure fetch / filter / dedup / email. Zero token cost.

## How it works

1. **Weekly cron** (`0 6 * * 1`) fires `runWeeklyScan()`
2. Agent chunks through your company list (40 at a time, respecting Workers subrequest limits)
3. Applies title + location keyword filters
4. Deduplicates against `seen_jobs` SQLite table in the Durable Object
5. Emails new roles via [Resend](https://resend.com) — silent weeks send nothing
6. First run sends a seed email ("tracking N open roles") instead of a blast

## Stack

- **Runtime:** Cloudflare Workers
- **Agent SDK:** [`agents`](https://developers.cloudflare.com/agents/) (Durable Objects + SQLite)
- **ATS support:** Greenhouse, Ashby, Lever (auto-detected from careers URL)
- **Email:** Resend API

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure environment

Copy `.env.example` to `.dev.vars` for local dev (Wrangler reads `.dev.vars`):

```bash
cp .env.example .dev.vars
```

Fill in `RESEND_API_KEY` and `JOB_ALERT_TO`.

For production, set secrets via Wrangler:

```bash
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put JOB_ALERT_TO
npx wrangler secret put JOB_ALERT_FROM   # optional
```

### 3. Configure your company list

Edit `src/agents/job-search.portals.json` directly, or maintain a `portals.yml` and run:

```bash
node scripts/build-portals.mjs            # reads portals.yml in project root
node scripts/build-portals.mjs /path/to/portals.yml
```

**portals.yml format:**

```yaml
tracked_companies:
  - name: Acme Corp
    careers_url: https://jobs.ashbyhq.com/acme
  - name: Example Inc
    api: https://boards-api.greenhouse.io/v1/boards/example/jobs
  - name: Disabled Co
    careers_url: https://jobs.lever.co/disabled
    enabled: false

title_filter:
  positive: ["engineer", "developer", "fullstack", "backend"]
  negative: ["senior staff", "principal", "intern"]

location_filter:
  positive: ["remote", "berlin", "munich"]
  negative: []
```

Supported ATS types (auto-detected from `careers_url`):
- **Ashby** — `jobs.ashbyhq.com/<slug>`
- **Lever** — `jobs.lever.co/<slug>`
- **Greenhouse** — `job-boards.greenhouse.io/<slug>` or explicit `api` URL

### 4. Run locally

```bash
npm run dev
curl -X POST http://localhost:8787/job-search/local1/run
```

Each unique name is a fresh Durable Object with no history → triggers the seed email path.

### 5. Deploy

```bash
npm run deploy
```

Trigger a manual run in production:

```bash
curl -X POST https://<your-worker>.workers.dev/job-search/main/run
```

## Subrequest limits

The Workers free plan allows 50 subrequests per invocation. The agent processes 40 companies per chunk, scheduling itself across as many invocations as needed. If your list grows past ~120 companies with detectable APIs, lower `CHUNK_SIZE` in `src/agents/job-search.ts` or upgrade to the $5/mo Workers paid plan (1000 calls/invocation).

## State (per Durable Object)

| Table | Purpose |
|---|---|
| `seen_jobs` | Permanent dedup history (url, first_seen, title, company) |
| `pending_offers` | Cross-chunk accumulator for the current run; cleared on entry and after finalize |

Agent state: `{ lastRunAt: string | null, lastRunNewCount: number }`
