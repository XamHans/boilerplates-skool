@AGENTS.md

# This project: Lüneburg city voice agent

The generic LiveKit guidance is in `@AGENTS.md` above. The rules below are specific to **this** agent — a German RAG voicebot. Reference implementation: `src/agent.py` + `src/tools/`.

## Structure (keep `src/agent.py` as the entrypoint)

```
src/
  agent.py                     # entrypoint: AgentServer, session setup, tool registration
  transport_profiles.py        # web (48kHz) vs telephony (8kHz) STT/LLM/TTS config
  prompts/lueneburg.md         # SYSTEM PROMPT — edit agent behavior HERE, not inline in agent.py
  tools/
    department_hours_tool.py   # getOpeningHours
    knowledge_base_tool.py     # queryKnowledgeBase (RAG)
  utils/                       # json_logger, session_metrics, metrics_writer
data/                          # opening_hours.json + knowledge_base_raw_files/ (568 docs)
scripts/                       # init_db.sql, ingest_knowledge_base.py, verify_rag_setup.py
```

## Rules

- **Edit the system prompt in `prompts/lueneburg.md`**, not as an inline string. `agent.py` loads it via `PROMPT_PATH.read_text()`.
- **Tools are plain functions registered in `Agent(tools=[...])`.** To add one: create `src/tools/{name}_tool.py`, import it in `agent.py`, add it to the `tools=[...]` list. Match the existing tool signature/logging style.
- **TDD is required for behavior changes** (instructions, tool descriptions, workflows): write the test in `tests/` first, then iterate until it passes. Some LLM-judged tests are flaky by design — a 50–60% pass rate on the full suite is expected.
- **RAG retrieval returns whole documents, not chunks:** query → OpenAI embedding (1536-dim) → pgvector cosine search → load the top-2 matching markdown files from disk → inject full text. Preserve this "complete document" behavior when editing `knowledge_base_tool.py`.
- **Log tool calls through the existing `utils/json_logger`** (structured JSON: name, params, timing). Don't add ad-hoc `print`s.
- Format/lint with `uv run ruff format` and `uv run ruff check` before finishing.

## Commands (`uv` only)

```bash
uv sync                                   # install deps
uv run python src/agent.py download-files # one-time: Silero VAD + turn detector
uv run python src/agent.py console        # talk to the agent in the terminal
uv run python src/agent.py dev            # run for frontend/telephony
uv run pytest                             # tests (or: docker-compose exec agent uv run pytest)
TRANSPORT_PROFILE=telephony uv run python src/agent.py dev   # telephony profile

uv run python scripts/ingest_knowledge_base.py --force       # re-ingest the knowledge base
```
