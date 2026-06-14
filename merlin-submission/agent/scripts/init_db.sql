-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Single table for all chunks with metadata
CREATE TABLE knowledge_chunks (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(512) NOT NULL,
    title TEXT NOT NULL,
    source_url TEXT NOT NULL,
    chunk_text TEXT NOT NULL,
    heading TEXT,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(filename, chunk_index)
);

-- Fast vector similarity search index
CREATE INDEX knowledge_chunks_embedding_idx ON knowledge_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Index for filename lookups (deduplication)
CREATE INDEX knowledge_chunks_filename_idx ON knowledge_chunks(filename);
