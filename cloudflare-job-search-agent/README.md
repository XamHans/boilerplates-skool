# Cloudflare Job Search Agent

A weekly cron agent that scrapes Greenhouse / Ashby / Lever job boards, deduplicates against history, and emails you only the **new** matching roles. Built on Cloudflare Workers + Agents SDK (Durable Objects with built-in SQLite).

**No LLM — zero token cost.** Pure fetch / filter / dedup / email.

---

## How it works

### The flow

```
Monday 06:00 UTC — cron fires
        │
        ▼
runWeeklyScan()
  ├─ clears pending_offers table
  ├─ checks if this is the first ever run (lastRunAt === null)
  └─ schedules runScanChunk({ cursor: 0 })
        │
        ▼
runScanChunk() — runs once per 40 companies (one Workers invocation each)
  ├─ fetches job board APIs for companies [cursor … cursor+40]
  ├─ parses each ATS format (Greenhouse / Ashby / Lever)
  ├─ applies title + location keyword filters
  ├─ deduplicates against seen_jobs + pending_offers (SQLite)
  ├─ inserts new matches into pending_offers
  └─ if more companies remain → schedule next chunk
     else → finalizeRun()
        │
        ▼
finalizeRun()
  ├─ reads all pending_offers
  ├─ sends email via Resend (BEFORE updating seen_jobs — so a Resend failure retries next week)
  │    ├─ first run → "Job agent activated, tracking N open roles" (no blast)
  │    └─ subsequent runs → HTML email grouped by company (silent if nothing new)
  ├─ promotes pending_offers → seen_jobs
  ├─ updates agent state (lastRunAt, lastRunNewCount)
  └─ clears pending_offers
```

### Why chunks?

The Cloudflare Workers **free plan** caps outbound HTTP calls at 50 per invocation. Scanning 80+ company portals needs more than that. The agent self-schedules in chunks of 40 companies — each chunk is a separate invocation with its own 50-call budget. The Durable Object's SQLite `pending_offers` table acts as the accumulator between chunks.

### ATS detection

The agent auto-detects which job board API to call based on the `careers_url`:

| ATS | URL pattern | API called |
|-----|-------------|-----------|
| Ashby | `jobs.ashbyhq.com/<slug>` | `api.ashbyhq.com/posting-api/job-board/<slug>` |
| Lever | `jobs.lever.co/<slug>` | `api.lever.co/v0/postings/<slug>` |
| Greenhouse | `job-boards.greenhouse.io/<slug>` | `boards-api.greenhouse.io/v1/boards/<slug>/jobs` |
| Greenhouse (explicit) | — | set `api:` field directly in portals config |

### State (per Durable Object)

Each named agent instance (`main`, `test1`, etc.) is a separate Durable Object with independent SQLite state:

| Table | Columns | Purpose |
|---|---|---|
| `seen_jobs` | `url PK, first_seen, title, company` | Permanent dedup history — a URL here is never emailed again |
| `pending_offers` | `url PK, title, company, location` | Cross-chunk accumulator for the current run |

Agent state object: `{ lastRunAt: string | null, lastRunNewCount: number }`

---

## Prerequisites

- **Node.js** 18+
- **Cloudflare account** — free tier is enough
- **Resend account** — free tier is enough (100 emails/day)
- `wrangler` CLI (installed as a dev dependency, no global install needed)

---

## Step-by-step setup

### Step 1 — Install dependencies

```bash
npm install
```

### Step 2 — Authenticate with Cloudflare

```bash
npx wrangler login
```

This opens a browser to connect your Cloudflare account. Only needed once per machine.

### Step 3 — Configure your company list

Edit `src/agents/job-search.portals.json` directly. The structure:

```json
{
  "tracked_companies": [
    { "name": "Acme Corp", "careers_url": "https://jobs.ashbyhq.com/acme" },
    { "name": "Example Inc", "careers_url": "https://jobs.lever.co/example" },
    { "name": "Big Co", "api": "https://boards-api.greenhouse.io/v1/boards/bigco/jobs" },
    { "name": "Paused Co", "careers_url": "https://jobs.ashbyhq.com/paused", "enabled": false }
  ],
  "title_filter": {
    "positive": ["engineer", "developer", "fullstack", "backend"],
    "negative": ["staff", "principal", "intern", "manager"]
  },
  "location_filter": {
    "positive": ["remote", "berlin", "munich"],
    "negative": []
  }
}
```

**Keyword matching rules:**
- `positive` — job must match at least one positive keyword (leave empty `[]` to allow all)
- `negative` — job is excluded if it matches any negative keyword
- Matching is word-boundary aware and case-insensitive

**Alternative — maintain a YAML file and generate the JSON:**

```bash
node scripts/build-portals.mjs portals.yml
```

See `scripts/build-portals.mjs` for the expected YAML shape.

### Step 4 — Set up local environment

Wrangler reads secrets from `.dev.vars` (not `.env`) during local dev. Create it from the example:

```bash
cp .env.example .dev.vars
```

Then edit `.dev.vars` and fill in your values:

```bash
RESEND_API_KEY=re_your_key_here
JOB_ALERT_TO=you@example.com
JOB_ALERT_FROM=onboarding@resend.dev   # use your own domain once verified in Resend
```

`.dev.vars` is gitignored — never commit it.

### Step 5 — Run locally

```bash
npm run dev
```

In another terminal, trigger a scan against a fresh test instance:

```bash
curl -X POST http://localhost:8787/job-search/test1/run
```

Any unique name (`test1`, `test2`, …) creates a fresh Durable Object with no history → triggers the seed email path so you can confirm Resend is wired up correctly. Watch the Wrangler console for `[JobSearchAgent] chunk N/M` progress logs.

### Step 6 — Deploy to Cloudflare

```bash
npm run deploy
```

Wrangler creates the Worker and registers the Durable Object classes and cron trigger automatically.

### Step 7 — Set production secrets

After deploying, push your secrets (they are **not** read from `.dev.vars` in production):

```bash
npx wrangler secret put RESEND_API_KEY
npx wrangler secret put JOB_ALERT_TO
npx wrangler secret put JOB_ALERT_FROM   # optional
```

Each command prompts you to paste the value.

### Step 8 — Verify end-to-end

Trigger a manual production run:

```bash
curl -X POST https://<your-worker>.workers.dev/job-search/smoketest1/run
```

Expected within ~30 seconds:
1. Response: `{ "status": "scan_scheduled", "companies": N, "chunkSize": 40 }`
2. Cloudflare dashboard → **Workers → agents → Observability → Logs** shows `chunk 1/2 …`, `chunk 2/2 …`, `run complete: seeded N offers`
3. Your inbox receives the *"Job agent activated"* seed email

---

## Configuration reference

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `RESEND_API_KEY` | Yes | Resend API key — get from [resend.com/api-keys](https://resend.com/api-keys) |
| `JOB_ALERT_TO` | Yes | Recipient email address for job alerts |
| `JOB_ALERT_FROM` | No | Sender address. Defaults to `onboarding@resend.dev`. Set a custom address once you verify your domain in Resend |

### Cron schedule

Defined in `wrangler.jsonc`:

```jsonc
"triggers": {
  "crons": ["0 6 * * 1"]   // Every Monday at 06:00 UTC
}
```

Change to any valid cron expression. Redeploy after changing.

### Chunk size

In `src/agents/job-search.ts`:

```ts
const CHUNK_SIZE = 40;
```

Lower this if you hit subrequest errors. Raise it (up to ~48) if you're on the Workers paid plan ($5/mo → 1000 calls/invocation).

---

## Operations

### Manually trigger a production scan

```bash
curl -X POST https://<your-worker>.workers.dev/job-search/main/run
```

### Test without affecting main history

Use any name other than `main` — each name is an isolated Durable Object:

```bash
curl -X POST https://<your-worker>.workers.dev/job-search/dryrun1/run
```

### Update the company list

Edit `src/agents/job-search.portals.json` (or regenerate from YAML), then redeploy:

```bash
npm run build-portals   # if using portals.yml
npm run deploy
```

The JSON is bundled into the Worker at deploy time — no runtime file reads.

### Typecheck before deploying

```bash
npm run typecheck
```

---

## Troubleshooting

**No email received after a run**
- Check Resend dashboard for send attempts and errors
- Confirm `RESEND_API_KEY` and `JOB_ALERT_TO` are set as Wrangler secrets (`npx wrangler secret list`)
- On first run, the seed email is sent even if 0 new jobs were found — check spam

**HTTP 404 errors for some companies in logs**
- The company changed their ATS slug. Update the `careers_url` or `api` field in the portals config and redeploy.

**"scan_scheduled" but no chunk logs appear**
- The Durable Object scheduler fires asynchronously. Wait 5–10 seconds then refresh the Observability logs tab.

**Want to reset a Durable Object's seen history**
- Use a new name for a clean slate: `curl -X POST .../job-search/fresh1/run`
- To reset `main`, delete the Durable Object from the Cloudflare dashboard (Workers → Durable Objects) — this clears all SQLite state for that instance.
