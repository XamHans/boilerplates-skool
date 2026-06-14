#!/usr/bin/env python3
"""
RAG Setup Verification Script

Checks that all components of the RAG system are properly configured and working.

Usage:
    uv run python scripts/verify_rag_setup.py
"""

import os
import sys
from pathlib import Path

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def check_env_var(var_name: str) -> bool:
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value and value != "your_key_here":
        print(f"{GREEN}✓{RESET} {var_name} is set")
        return True
    else:
        print(f"{RED}✗{RESET} {var_name} is not set or has placeholder value")
        return False


def check_database_connection() -> bool:
    """Check if database is accessible."""
    try:
        import psycopg2

        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print(f"{RED}✗{RESET} DATABASE_URL not set")
            return False

        conn = psycopg2.connect(db_url)
        conn.close()
        print(f"{GREEN}✓{RESET} Database connection successful")
        return True
    except ImportError:
        print(f"{RED}✗{RESET} psycopg2 not installed (run: uv sync)")
        return False
    except Exception as e:
        print(f"{RED}✗{RESET} Database connection failed: {e}")
        return False


def check_database_schema() -> bool:
    """Check if the knowledge_chunks table exists with proper schema."""
    try:
        import psycopg2

        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)

        with conn.cursor() as cur:
            # Check if table exists
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'knowledge_chunks'
                )
                """
            )
            table_exists = cur.fetchone()[0]

            if not table_exists:
                print(f"{RED}✗{RESET} knowledge_chunks table does not exist")
                conn.close()
                return False

            # Check for required columns
            cur.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'knowledge_chunks'
                ORDER BY ordinal_position
                """
            )
            columns = cur.fetchall()

            required_columns = {
                "id",
                "filename",
                "title",
                "source_url",
                "chunk_text",
                "heading",
                "chunk_index",
                "embedding",
                "created_at",
            }
            found_columns = {col[0] for col in columns}

            if required_columns.issubset(found_columns):
                print(f"{GREEN}✓{RESET} Database schema is correct")
                conn.close()
                return True
            else:
                missing = required_columns - found_columns
                print(f"{RED}✗{RESET} Missing columns: {missing}")
                conn.close()
                return False

    except Exception as e:
        print(f"{RED}✗{RESET} Schema check failed: {e}")
        return False


def check_data_ingested() -> bool:
    """Check if knowledge base data has been ingested."""
    try:
        import psycopg2

        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM knowledge_chunks")
            count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT filename) FROM knowledge_chunks")
            file_count = cur.fetchone()[0]

        conn.close()

        if count > 0:
            print(
                f"{GREEN}✓{RESET} Data ingested: {count} chunks from {file_count} files"
            )
            return True
        else:
            print(
                f"{YELLOW}⚠{RESET} No data ingested yet (run: uv run python scripts/ingest_knowledge_base.py)"
            )
            return False

    except Exception as e:
        print(f"{RED}✗{RESET} Data check failed: {e}")
        return False


def check_openai_connection() -> bool:
    """Check if OpenAI API is accessible."""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_key_here":
            print(f"{RED}✗{RESET} OPENAI_API_KEY not set")
            return False

        client = OpenAI(api_key=api_key)

        # Test embeddings API
        response = client.embeddings.create(
            model="text-embedding-3-small", input="test"
        )

        if len(response.data[0].embedding) == 1536:
            print(f"{GREEN}✓{RESET} OpenAI API connection successful")
            return True
        else:
            print(f"{RED}✗{RESET} Unexpected embedding dimension")
            return False

    except ImportError:
        print(f"{RED}✗{RESET} openai package not installed (run: uv sync)")
        return False
    except Exception as e:
        print(f"{RED}✗{RESET} OpenAI API check failed: {e}")
        return False


def check_knowledge_base_files() -> bool:
    """Check if knowledge base files exist."""
    kb_path = (
        Path(__file__).resolve().parent.parent / "data" / "knowledge_base_raw_files"
    )

    if not kb_path.exists():
        print(f"{RED}✗{RESET} Knowledge base directory not found: {kb_path}")
        return False

    md_files = list(kb_path.glob("*.md"))

    if len(md_files) > 0:
        print(f"{GREEN}✓{RESET} Knowledge base files found: {len(md_files)} files")
        return True
    else:
        print(f"{RED}✗{RESET} No markdown files found in {kb_path}")
        return False


def test_vector_search() -> bool:
    """Test vector search functionality."""
    try:
        # Import the vector search function
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
        from tools.knowledge_base_tool import vector_search

        result = vector_search("Test query", top_k=1)

        if result and not result.startswith("Keine relevanten"):
            print(f"{GREEN}✓{RESET} Vector search working")
            return True
        elif result.startswith("Keine relevanten"):
            print(f"{YELLOW}⚠{RESET} Vector search returned no results (database may be empty)")
            return False
        else:
            print(f"{RED}✗{RESET} Vector search failed")
            return False

    except Exception as e:
        print(f"{RED}✗{RESET} Vector search test failed: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("RAG System Verification")
    print("=" * 60 + "\n")

    checks = [
        ("Environment Variables", [
            lambda: check_env_var("DATABASE_URL"),
            lambda: check_env_var("OPENAI_API_KEY"),
        ]),
        ("Database", [
            check_database_connection,
            check_database_schema,
            check_data_ingested,
        ]),
        ("External Services", [
            check_openai_connection,
        ]),
        ("Knowledge Base", [
            check_knowledge_base_files,
        ]),
        ("Integration", [
            test_vector_search,
        ]),
    ]

    all_passed = True

    for section_name, section_checks in checks:
        print(f"\n{section_name}:")
        print("-" * 60)

        for check in section_checks:
            if not check():
                all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print(f"{GREEN}✓ All checks passed!{RESET}")
        print("\nYour RAG system is ready to use.")
    else:
        print(f"{RED}✗ Some checks failed{RESET}")
        print("\nPlease review the errors above and consult RAG_SETUP.md for troubleshooting.")
    print("=" * 60 + "\n")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
