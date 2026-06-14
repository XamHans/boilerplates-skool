# LiveKit City Voice Agent

> **Note:** This is an imaginary use case built as a boilerplate. The "Hansestadt Lüneburg" city administration scenario is fictional and used purely as a realistic example to demonstrate how to build a voice AI agent for municipal/government services. Swap in your own city, brand, and knowledge base to make it your own.

A voice AI assistant with RAG-powered knowledge base retrieval, built with LiveKit Agents. Demonstrates a complete production setup: STT → LLM → Tools → TTS pipeline with Docker Compose.

## Overview

This is an **auto-turn voicebot** for an imaginary city administration. Citizens can speak naturally to get information about city services, opening hours, and administrative procedures.

**Key Features:**
- Continuous voice interaction (no push-to-talk required)
- German-optimized speech pipeline (Whisper STT, ElevenLabs TTS)
- RAG-powered knowledge base with 568 city service documents
- Intent-based tool selection: opening hours and service information

**Technology:** LiveKit Agents (Python), Next.js frontend, PostgreSQL with pgvector for semantic search.

## How It Works

```
User speaks in German
    ↓
[STT] OpenAI Whisper → Transcribed text
    ↓
[LLM] GPT-4o-mini → Recognizes intent, selects tool
    ↓
[Tool] getOpeningHours OR queryKnowledgeBase → Retrieves data
    ↓
[LLM] Generates natural German response with context
    ↓
[TTS] ElevenLabs → German audio
    ↓
User hears response
```

**Two Tools:**
1. **`getOpeningHours`** - Returns all department opening hours with current date and holiday information
2. **`queryKnowledgeBase`** - Semantic RAG search across 568 city service documents, returns complete markdown files (not fragments) for comprehensive answers

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- `OPENAI_API_KEY` - Required for LLM and embeddings
- `ELEVEN_API_KEY` - Required for German TTS

### 2. Start Services

```bash
docker-compose up --build
```

**First startup:** 2-4 minutes (downloads ML models, ingests 568 documents into PostgreSQL)
**Subsequent startups:** 1-2 seconds

### 3. Use the Agent

1. Open http://localhost:3000
2. Click "Start Call" and allow microphone access
3. Ask in German: "Wann hat das Standesamt geöffnet?" or "Wie beantrage ich einen Personalausweis?"

### Verify Setup

```bash
# Check all services are healthy
docker-compose ps

# Check knowledge base ingestion (expect ~7260 chunks from 568 files)
docker-compose exec postgres psql -U rag_user -d rag_db -c "SELECT COUNT(*) FROM knowledge_chunks;"
```

## Architecture

### System Components

Four Docker services orchestrated by docker-compose:

```
┌─────────────┐      WebRTC      ┌──────────────┐
│   Browser   │ ←──────────────→ │   LiveKit    │
│  (Next.js)  │   Audio Stream   │    Server    │
└─────────────┘                  └──────┬───────┘
                                        │
                                 ┌──────▼───────┐
                                 │    Agent     │
                                 │  (Python)    │
                                 │ STT/LLM/TTS  │
                                 └──────┬───────┘
                              ┌─────────┴──────────┐
                       ┌──────▼──────┐     ┌──────▼──────┐
                       │ PostgreSQL  │     │   OpenAI    │
                       │ (pgvector)  │     │ ElevenLabs  │
                       └─────────────┘     └─────────────┘
```

**Service Roles:**
- **Browser:** User interface with WebRTC audio I/O
- **LiveKit Server:** WebRTC media routing
- **Agent:** Orchestrates voice pipeline (STT → LLM → Tools → TTS)
- **PostgreSQL:** Vector storage for semantic search (7260 chunks from 568 files)
- **OpenAI/ElevenLabs:** Cloud AI models (Whisper STT, GPT-4o-mini LLM, ElevenLabs TTS, embeddings)

### RAG Knowledge Base Design

**Why complete documents instead of fragments?**

Traditional RAG returns small text chunks that lack context. We return **entire markdown files** (top 2 matches) so the LLM can answer complex questions in one response.

**Example:**
- Query: "Wie beantrage ich einen Personalausweis?"
- Traditional RAG: 3-4 text fragments about ID application
- Our approach: Complete "Personalausweis_beantragen.md" with ALL details (requirements, costs, processing time, required documents)
- Result: Comprehensive answer without follow-up questions

**Retrieval Process:**
1. Query → OpenAI embedding (1536-dim vector)
2. PostgreSQL pgvector → Cosine similarity search across 7260 chunks
3. Top 2 matching filenames identified
4. Complete markdown files loaded from disk
5. Full documents injected into LLM context

**Trade-off:** Higher token costs vs complete context quality. We chose quality.

### Technology Stack

**Voice Pipeline:**
- **STT:** OpenAI Whisper (German optimized)
- **LLM:** GPT-4o-mini (intent recognition, response generation)
- **TTS:** ElevenLabs (eleven_turbo_v2_5 for web, eleven_turbo_v2 for telephony)
- **VAD:** Silero VAD + LiveKit Turn Detector (auto-turn detection)
- **Embeddings:** OpenAI text-embedding-3-small (1536 dimensions)

**Infrastructure:**
- **Backend:** Python with LiveKit Agents SDK
- **Frontend:** Next.js with LiveKit Components React
- **Database:** PostgreSQL with pgvector extension
- **Deployment:** Docker Compose with health checks
- **Transport Profiles:** Optimized for web (48kHz) vs telephony (8kHz)

### Code Structure

```
agent/src/
  ├── agent.py                      # Entrypoint: session setup, tool registration
  ├── transport_profiles.py         # Web vs telephony configurations
  ├── prompts/lueneburg.md          # System prompt + tool instructions
  ├── tools/
  │   ├── department_hours_tool.py  # getOpeningHours implementation
  │   └── knowledge_base_tool.py    # queryKnowledgeBase with RAG
  └── utils/
      ├── json_logger.py            # Structured tool call logging
      └── session_metrics.py        # Performance metrics collection

agent/data/
  ├── opening_hours.json            # 5 departments with hours
  └── knowledge_base_raw_files/     # 568 markdown city service docs

agent/scripts/
  ├── init_db.sql                   # PostgreSQL schema with pgvector
  └── ingest_knowledge_base.py      # Vector ingestion (auto-runs on first startup)
```

**First Startup:** Agent automatically downloads ML models (Silero VAD, Turn Detector) and ingests knowledge base if database is empty. Subsequent startups skip this and start in < 2 seconds.

## Development

### Testing

```bash
# Run all tests
docker-compose exec agent uv run pytest

# Verbose output
docker-compose exec agent uv run pytest -v

# Run specific test file
docker-compose exec agent uv run pytest tests/test_agent.py -v

# With coverage
docker-compose exec agent uv run pytest --cov
```

Tests use the LiveKit Agents testing framework with 79 comprehensive test cases:
- `tests/test_agent.py` - Basic agent behavior tests (grounding, safety)
- `tests/test_rag_pipeline.py` - RAG pipeline, opening hours, knowledge base, and edge cases

**Note:** Some tests may fail due to LLM response variability. A 50-60% pass rate is expected for comprehensive test suites with strict LLM judgment criteria.

### Logging & Monitoring

**View Logs:**
```bash
# All services
docker-compose logs -f

# Knowledge retrieval logs (query matching, file selection, context size)
tail -f logs/knowledge_retrieval.log

# Inside Docker
docker-compose exec agent tail -f /app/logs/knowledge_retrieval.log
```

**Metrics Collected:**
- Session duration, tool calls, latency
- Logged on session end
- Structured JSON logs for tool calls (name, parameters, execution time)

### Manual Operations

```bash
# Force re-ingestion of knowledge base
docker-compose exec agent uv run python scripts/ingest_knowledge_base.py --force

# Download ML models manually
docker-compose exec agent uv run src/agent.py download-files
```

## Troubleshooting

### Knowledge Base Empty

If `SELECT COUNT(*) FROM knowledge_chunks` returns 0:

1. Verify `OPENAI_API_KEY` is set in `.env`
2. Run: `docker-compose exec agent uv run python scripts/ingest_knowledge_base.py`

### Reset Everything

```bash
docker-compose down -v
docker-compose up --build
```

This removes all Docker volumes (database, logs) and starts fresh.
