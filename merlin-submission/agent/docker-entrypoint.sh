#!/bin/bash
set -e

echo "=== Lüneburg Agent First-Time Setup ==="

# STEP 1: Download ML models (always run, idempotent)
echo "Downloading ML models and files..."
if uv run src/agent.py download-files; then
    echo "✓ Models downloaded successfully"
else
    echo "✗ WARNING: Model download failed, continuing anyway"
fi

# STEP 2: Check DATABASE_URL and wait for postgres
if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL not set"
    exit 1
fi

echo "Waiting for PostgreSQL to be ready..."
until psql "$DATABASE_URL" -c '\q' 2>/dev/null; do
    sleep 2
done
echo "✓ PostgreSQL is ready"

# STEP 3: Check if knowledge base needs ingestion
CHUNK_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM knowledge_chunks;" 2>/dev/null | xargs)

if [ "$CHUNK_COUNT" -eq 0 ]; then
    echo "Knowledge base is empty, checking for ingestion..."

    if [ -z "$OPENAI_API_KEY" ]; then
        echo "✗ WARNING: OPENAI_API_KEY not set, skipping ingestion"
        echo "  You can run ingestion manually with:"
        echo "  docker-compose exec agent uv run python scripts/ingest_knowledge_base.py"
    else
        echo "Starting knowledge base ingestion..."
        if uv run python scripts/ingest_knowledge_base.py; then
            echo "✓ Knowledge base ingestion completed successfully"
        else
            echo "✗ WARNING: Ingestion failed, agent will start anyway"
            echo "  You can retry with:"
            echo "  docker-compose exec agent uv run python scripts/ingest_knowledge_base.py"
        fi
    fi
else
    echo "✓ Knowledge base already contains $CHUNK_COUNT chunks, skipping ingestion"
fi

# STEP 4: Start the agent
echo "=== Starting agent ==="
exec "$@"
