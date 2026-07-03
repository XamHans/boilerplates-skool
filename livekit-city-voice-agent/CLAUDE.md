# CLAUDE.md

LiveKit **voice AI assistant** for a (fictional) city administration — an auto-turn German voicebot with a RAG-powered knowledge base. Pipeline: **STT (Whisper) → LLM (GPT-4o-mini) → Tools → TTS (ElevenLabs)**, semantic search over 568 city-service docs in Postgres/pgvector.

## Monorepo layout

Two independent packages — work inside the one you're changing; its own `CLAUDE.md` loads with the project-specific rules.

| Path | Stack | Guide |
|------|-------|-------|
| `agent/` | Python · `uv` · LiveKit Agents SDK · pgvector RAG | `agent/CLAUDE.md` (+ `agent/AGENTS.md`) |
| `ui/` | Next.js (App Router) · `pnpm` · LiveKit Components React | `ui/CLAUDE.md` |

**Never mix toolchains across packages: `uv` only in `agent/`, `pnpm` only in `ui/`.**

## Run everything (docker-compose)

```bash
cp .env.example .env      # add OPENAI_API_KEY and ELEVEN_API_KEY
docker-compose up --build # agent + ui + livekit + postgres; UI on http://localhost:3000
```

First startup (2–4 min) downloads ML models and ingests the knowledge base; later startups are ~seconds. Four services: Browser (ui) ⇄ LiveKit server ⇄ Agent ⇄ Postgres(pgvector) + OpenAI/ElevenLabs.

```bash
docker-compose ps                                   # health
docker-compose exec agent uv run pytest             # run agent tests in-container
docker-compose down -v && docker-compose up --build # reset (drops db + logs)
```

## Cross-cutting notes

- Content and prompts are **German** — keep user-facing strings German.
- Secrets live in `.env` (root, for compose) / `.env.local` (agent local runs). Never hardcode keys.
- The RAG design returns **complete markdown documents** (top 2), not fragments — quality over token cost. Detail in `agent/CLAUDE.md`.
