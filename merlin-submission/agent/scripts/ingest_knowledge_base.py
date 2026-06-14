#!/usr/bin/env python3
"""
Knowledge Base Ingestion Script

Ingests markdown files from the knowledge base into PostgreSQL with pgvector embeddings.
Uses LlamaIndex for markdown parsing and OpenAI for embeddings.

Usage:
    uv run python scripts/ingest_knowledge_base.py [--force] [--file PATTERN]

Options:
    --force: Re-ingest files even if they already exist in the database
    --file PATTERN: Only ingest files matching the pattern (e.g., "Gewerbe*.md")
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from llama_index.core.node_parser import MarkdownNodeParser
from llama_index.core.schema import Document
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables from .env.local (preferred) or .env
agent_dir = Path(__file__).resolve().parent.parent
env_local = agent_dir / ".env.local"
env_file = agent_dir.parent / ".env"

if env_local.exists():
    load_dotenv(env_local)
    logger.info(f"Loaded environment from: {env_local}")
else:
    load_dotenv(env_file)
    logger.info(f"Loaded environment from: {env_file}")

# Configuration
KB_PATH = Path(__file__).resolve().parent.parent / "data" / "knowledge_base_raw_files"
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50  # Process embeddings in batches


def extract_source_url(content: str) -> str:
    """Extract source URL from first line of markdown file (format: Quelle: <url>)."""
    lines = content.split("\n")
    if lines and lines[0].startswith("Quelle: "):
        return lines[0][8:].strip()
    return ""


def extract_title(content: str) -> str:
    """Extract title from first # heading in markdown file."""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def chunk_markdown(content: str) -> list[dict[str, Any]]:
    """
    Use LlamaIndex MarkdownNodeParser to parse markdown into semantic chunks.

    Returns list of dicts with 'content' and 'heading' keys.
    """
    parser = MarkdownNodeParser()

    # Create a document
    doc = Document(text=content)

    # Parse into nodes (chunks)
    nodes = parser.get_nodes_from_documents([doc])

    # Extract text and metadata from each node
    chunks = []
    for node in nodes:
        chunks.append(
            {
                "content": node.get_content(),
                "heading": node.metadata.get("heading", ""),
            }
        )

    return chunks


def batch_embed(openai_client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts using OpenAI API."""
    response = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
    return [item.embedding for item in response.data]


def file_already_ingested(conn, filename: str) -> bool:
    """Check if a file has already been ingested."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM knowledge_chunks WHERE filename = %s", (filename,))
        count = cur.fetchone()[0]
        return count > 0


def ingest_file(conn, openai_client: OpenAI, md_file: Path, force: bool = False) -> bool:
    """
    Ingest a single markdown file into the database.

    Returns True if ingestion was successful, False otherwise.
    """
    filename = md_file.name

    # Check if already ingested
    if not force and file_already_ingested(conn, filename):
        logger.debug(f"Skipping {filename} (already ingested)")
        return True

    try:
        # Read and parse file
        content = md_file.read_text(encoding="utf-8")
        source_url = extract_source_url(content)
        title = extract_title(content)

        if not source_url:
            logger.warning(f"No source URL found in {filename}, skipping")
            return False

        # Chunk the content
        chunks = chunk_markdown(content)

        if not chunks:
            logger.warning(f"No chunks generated for {filename}, skipping")
            return False

        # Delete existing chunks if force flag is set
        if force:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM knowledge_chunks WHERE filename = %s", (filename,))
                logger.debug(f"Deleted existing chunks for {filename}")

        # Generate embeddings in batches
        chunk_texts = [chunk["content"] for chunk in chunks]
        all_embeddings = []

        for i in range(0, len(chunk_texts), BATCH_SIZE):
            batch_texts = chunk_texts[i : i + BATCH_SIZE]
            embeddings = batch_embed(openai_client, batch_texts)
            all_embeddings.extend(embeddings)
            logger.debug(
                f"Generated embeddings for chunks {i+1}-{min(i+len(batch_texts), len(chunk_texts))} of {len(chunk_texts)}"
            )

        # Insert chunks with embeddings
        with conn.cursor() as cur:
            for idx, (chunk, embedding) in enumerate(zip(chunks, all_embeddings)):
                cur.execute(
                    """
                    INSERT INTO knowledge_chunks
                        (filename, title, source_url, chunk_text, heading, chunk_index, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (filename, chunk_index) DO UPDATE SET
                        title = EXCLUDED.title,
                        source_url = EXCLUDED.source_url,
                        chunk_text = EXCLUDED.chunk_text,
                        heading = EXCLUDED.heading,
                        embedding = EXCLUDED.embedding
                    """,
                    (
                        filename,
                        title,
                        source_url,
                        chunk["content"],
                        chunk["heading"],
                        idx,
                        embedding,
                    ),
                )

        conn.commit()
        logger.info(f"Ingested {filename}: {len(chunks)} chunks")
        return True

    except Exception as e:
        logger.error(f"Error ingesting {filename}: {e}")
        conn.rollback()
        return False


def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge base files into PostgreSQL")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest files even if they already exist",
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Only ingest files matching this pattern (e.g., 'Gewerbe*.md')",
    )
    args = parser.parse_args()

    # Check environment variables
    db_url = os.getenv("DATABASE_URL")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        sys.exit(1)

    # Initialize clients
    logger.info("Connecting to database...")
    conn = psycopg2.connect(db_url)

    logger.info("Initializing OpenAI client...")
    openai_client = OpenAI(api_key=openai_api_key)

    # Get list of files to ingest
    if args.file:
        md_files = list(KB_PATH.glob(args.file))
        logger.info(f"Found {len(md_files)} files matching pattern '{args.file}'")
    else:
        md_files = list(KB_PATH.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files")

    if not md_files:
        logger.error(f"No markdown files found in {KB_PATH}")
        sys.exit(1)

    # Ingest files
    success_count = 0
    failed_count = 0

    for md_file in md_files:
        if ingest_file(conn, openai_client, md_file, force=args.force):
            success_count += 1
        else:
            failed_count += 1

    # Report summary
    logger.info("=" * 60)
    logger.info(f"Ingestion complete: {success_count} succeeded, {failed_count} failed")

    # Print database stats
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM knowledge_chunks")
        total_chunks = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT filename) FROM knowledge_chunks")
        unique_files = cur.fetchone()[0]

    logger.info(f"Database contains {total_chunks} chunks from {unique_files} unique files")

    conn.close()


if __name__ == "__main__":
    main()
