import logging
import os
from pathlib import Path

import psycopg2
import psycopg2.pool
from livekit.agents import RunContext, ToolError, function_tool
from openai import OpenAI

from utils.json_logger import json_logger, Timer

logger = logging.getLogger(__name__)

# Setup dedicated retrieval logger
retrieval_logger = logging.getLogger("knowledge_retrieval")
retrieval_logger.setLevel(logging.INFO)

# Create logs directory - works both in Docker (/app/logs) and locally (./logs)
if Path("/app").exists():
    LOG_DIR = Path("/app/logs")
else:
    LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"

LOG_DIR.mkdir(exist_ok=True, parents=True)

# File handler for retrieval logs
retrieval_log_file = LOG_DIR / "knowledge_retrieval.log"
file_handler = logging.FileHandler(retrieval_log_file)
file_handler.setLevel(logging.INFO)

# Format: timestamp | level | message
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
file_handler.setFormatter(formatter)
retrieval_logger.addHandler(file_handler)

# Prevent propagation to root logger to avoid duplicate logs
retrieval_logger.propagate = False

# Knowledge base directory
KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base_raw_files"

# Connection pool and OpenAI client (initialized on first use)
DB_POOL = None
OPENAI_CLIENT = None


def get_db_connection():
    """Get a database connection from the pool."""
    global DB_POOL
    if DB_POOL is None:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        DB_POOL = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=5, dsn=db_url)
    return DB_POOL.getconn()


def return_db_connection(conn):
    """Return a database connection to the pool."""
    global DB_POOL
    if DB_POOL is not None:
        DB_POOL.putconn(conn)


def get_openai_client():
    """Get or initialize OpenAI client."""
    global OPENAI_CLIENT
    if OPENAI_CLIENT is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable not set")
        OPENAI_CLIENT = OpenAI(api_key=api_key)
    return OPENAI_CLIENT


def vector_search(context: RunContext, query: str, top_k: int = 3) -> str | None:
    """
    Vector similarity search using PostgreSQL + pgvector.
    Returns complete markdown files instead of individual chunks.

    Args:
        context: The run context for interruption handling
        query: The search query
        top_k: Number of top matching files to return

    Returns:
        Complete markdown documents from the most semantically similar files,
        or None if the search was interrupted.

    Raises:
        ToolError: If database connection fails, OpenAI API fails, or no data is available
    """
    # Log the search query
    retrieval_logger.info("=" * 80)
    retrieval_logger.info(f"NEW SEARCH REQUEST")
    retrieval_logger.info(f"Query: {query}")
    retrieval_logger.info(f"Top K: {top_k}")

    try:
        openai_client = get_openai_client()
    except RuntimeError as e:
        retrieval_logger.error("Failed to get OpenAI client")
        raise ToolError(
            "Die Wissensdatenbank ist derzeit nicht verfügbar. "
            "Bitte versuchen Sie es später erneut."
        ) from e

    # Generate query embedding (check for interruption)
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small", input=query
        )
        query_embedding = response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI embedding generation failed: {e}")
        raise ToolError(
            "Die Suchanfrage konnte nicht verarbeitet werden. "
            "Bitte formulieren Sie Ihre Frage neu."
        ) from e

    # Check if interrupted before database query
    if context.speech_handle.interrupted:
        return None

    # Search for top matching files (using chunks as ranking mechanism)
    try:
        conn = get_db_connection()
    except (RuntimeError, psycopg2.Error) as e:
        logger.error(f"Database connection failed: {e}")
        raise ToolError(
            "Die Wissensdatenbank ist derzeit nicht erreichbar. "
            "Bitte versuchen Sie es in einem Moment erneut."
        ) from e

    # Time database query
    with Timer() as db_timer:
        try:
            with conn.cursor() as cur:
                # Get distinct filenames and their metadata from top matching chunks
                # We use a subquery to first find the best matching chunk for each file (DISTINCT ON filename),
                # and then sort the resulting unique files by their semantic distance (ORDER BY distance).
                cur.execute(
                    """
                    SELECT filename, title, source_url
                    FROM (
                        SELECT DISTINCT ON (filename)
                            filename,
                            title,
                            source_url,
                            embedding <=> %s::vector as distance
                        FROM knowledge_chunks
                        ORDER BY filename, distance
                    ) sub
                    ORDER BY distance ASC
                    LIMIT %s
                    """,
                    (query_embedding, top_k),
                )

                file_metadata = cur.fetchall()

            # Log database query
            json_logger.log_db_query(
                query_type="vector_search",
                duration_ms=db_timer.duration_ms,
                results_count=len(file_metadata)
            )

            # Log the matching files found
            retrieval_logger.info(f"Found {len(file_metadata)} matching files:")
            for idx, (filename, title, source_url) in enumerate(file_metadata, 1):
                retrieval_logger.info(f"  [{idx}] File: {filename}")
                retrieval_logger.info(f"      Title: {title}")
                retrieval_logger.info(f"      URL: {source_url}")

        except psycopg2.Error as e:
            logger.error(f"Database query failed: {e}")
            retrieval_logger.error(f"Database query failed: {e}")
            raise ToolError(
                "Bei der Suche ist ein Fehler aufgetreten. "
                "Bitte versuchen Sie eine andere Formulierung."
            ) from e
        finally:
            return_db_connection(conn)

    if not file_metadata:
        retrieval_logger.info("No matching files found - returning empty result")
        return "Keine relevanten Informationen im Wissensbestand gefunden."

    # Load complete markdown files from disk
    retrieval_logger.info("Loading file contents from disk...")
    results = []
    for idx, (filename, title, source_url) in enumerate(file_metadata, 1):
        file_path = KB_PATH / filename

        if not file_path.exists():
            logger.warning(f"Markdown file not found: {file_path}")
            retrieval_logger.warning(f"  [{idx}] File not found on disk: {filename}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                original_size = len(content)

                # Remove the first line (Quelle: URL) since we already have it
                lines = content.split("\n", 1)
                if len(lines) > 1 and lines[0].startswith("Quelle:"):
                    content = lines[1].strip()

                # Log file loading success with content preview
                retrieval_logger.info(f"  [{idx}] ✓ Loaded: {filename}")
                retrieval_logger.info(f"      Size: {original_size} chars ({len(content.split())} words)")
                retrieval_logger.info(f"      Preview: {content[:150]}...")

                results.append(
                    f"=== {title} ===\n{content}\n\nQuelle: {source_url}"
                )
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            retrieval_logger.error(f"  [{idx}] ✗ Failed to read {filename}: {e}")
            continue

    if not results:
        retrieval_logger.info("No files successfully loaded - returning empty result")
        return "Keine relevanten Informationen im Wissensbestand gefunden."

    # Log final result summary
    total_chars = sum(len(r) for r in results)
    retrieval_logger.info(f"RETRIEVAL COMPLETE:")
    retrieval_logger.info(f"  Files returned: {len(results)}")
    retrieval_logger.info(f"  Total context size: {total_chars} chars ({total_chars // 1000}KB)")
    retrieval_logger.info("=" * 80)

    return "\n\n---\n\n".join(results)


@function_tool()
async def queryKnowledgeBase(context: RunContext, query: str) -> str | None:
    """
    Search the city knowledge base for services, procedures, requirements, and administrative information.

    This tool uses semantic vector search to find and return COMPLETE DOCUMENTS (full markdown files)
    from the city's service portal. Each returned document contains comprehensive information about
    a specific service or procedure, including all details, requirements, costs, contact information,
    and related procedures.

    Args:
        query: The user's question about city services (in German).
               Examples: "Wie melde ich ein Gewerbe an?", "Welche Dokumente brauche ich für einen Personalausweis?"

    Returns:
        Complete markdown documents (up to 3) that are most relevant to the query. Each document
        contains the full content including all sections, procedures, requirements, costs, and
        contact details. Returns a message if no relevant information is found.

    Important:
    - This tool returns COMPLETE DOCUMENTS, not fragments or summaries
    - Extract ALL relevant information from the returned documents to answer the user's question
    - Look through all sections of the documents for comprehensive answers
    - Include specific details like document requirements, costs, deadlines, and contact information

    Use this tool when the user asks about:
    - How to perform a city service or administrative procedure
    - Required documents, forms, or prerequisites
    - Fees, costs, or payment methods
    - Processing times or deadlines
    - Contact information for city departments
    - Eligibility requirements or conditions
    - Location information for services

    Do NOT use this tool for:
    - Opening hours (use getOpeningHours instead)
    - General knowledge questions unrelated to city services
    - Questions about other cities (this is specific to Hansestadt Lüneburg)
    - Mathematical calculations or factual lookups
    """
    logger.info("Tool call: queryKnowledgeBase(query=%s)", query)

    # Time the entire tool call
    with Timer() as timer:
        # Tell user we're searching (improves UX for long-running operations)
        await context.session.say("Einen Moment, ich suche die Informationen für Sie heraus.")

        results = vector_search(context, query, top_k=2)

    # Log tool call
    json_logger.log_tool_call(
        tool="queryKnowledgeBase",
        duration_ms=timer.duration_ms,
        query_length=len(query)
    )

    return results
