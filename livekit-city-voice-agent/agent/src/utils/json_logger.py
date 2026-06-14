"""
Simple JSON logger for writing structured logs to files.

Writes events (session lifecycle, tool calls, DB queries, etc.) to
/app/logs/agent_metrics.log in JSON lines format.

Usage:
    from utils.json_logger import json_logger, Timer

    # Log events
    json_logger.log("session_start", {"room": room_name, "session_id": session_id})
    json_logger.log_session_end(duration_s, usage_summary)

    # Time operations
    with Timer() as timer:
        # ... operation ...
    json_logger.log_tool_call("tool_name", timer.duration_ms)
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class Timer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: float = 0.0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # noqa: ANN001
        self.end_time = time.time()
        if self.start_time is not None:
            self.duration_ms = (self.end_time - self.start_time) * 1000
        return False  # Don't suppress exceptions


class JSONLogger:
    """Simple JSON file logger with enable/disable toggle."""

    def __init__(self, log_file: Optional[str] = None):
        if log_file is None:
            if Path("/app").exists():
                log_file = "/app/logs/agent_metrics.log"
            else:
                log_file = str(Path(__file__).resolve().parent.parent.parent / "logs" / "agent_metrics.log")

        self.enabled = os.getenv("ENABLE_LOGGING", "true").lower() == "true"
        self.log_file = Path(log_file)
        self.logger: Optional[logging.Logger] = None

        if self.enabled:
            self._setup_logger()

    def _setup_logger(self):
        """Set up file logger."""
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Create logger
        self.logger = logging.getLogger("agent_metrics")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Don't propagate to root logger

        # Remove existing handlers
        self.logger.handlers.clear()

        # Add file handler
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def log(self, event: str, data: Dict[str, Any]):
        """Write an event as a JSON line."""
        if not self.enabled or self.logger is None:
            return

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **data
        }

        try:
            self.logger.info(json.dumps(entry))
        except Exception as e:
            # Don't let logging break the agent
            print(f"Failed to log: {e}")

    def log_session_start(self, room: str, session_id: str):
        """Log session start event."""
        self.log("session_start", {
            "room": room,
            "session_id": session_id
        })

    def log_session_end(
        self,
        duration_s: float,
        llm_prompt_tokens: int = 0,
        llm_completion_tokens: int = 0,
        tts_characters: int = 0,
        tts_audio_duration_s: float = 0.0,
        stt_audio_duration_s: float = 0.0
    ):
        """Log session end event with usage summary."""
        self.log("session_end", {
            "duration_s": round(duration_s, 2),
            "llm_prompt_tokens": llm_prompt_tokens,
            "llm_completion_tokens": llm_completion_tokens,
            "tts_characters": tts_characters,
            "tts_audio_duration_s": round(tts_audio_duration_s, 2),
            "stt_audio_duration_s": round(stt_audio_duration_s, 2)
        })

    def log_tool_call(self, tool: str, duration_ms: float, query_length: Optional[int] = None):
        """Log tool call event."""
        data = {
            "tool": tool,
            "duration_ms": round(duration_ms, 2)
        }
        if query_length is not None:
            data["query_length"] = query_length

        self.log("tool_call", data)

    def log_db_query(self, query_type: str, duration_ms: float, results_count: int):
        """Log database query event."""
        self.log("db_query", {
            "query_type": query_type,
            "duration_ms": round(duration_ms, 2),
            "results_count": results_count
        })

    def log_llm_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        duration_s: float,
        ttft_s: Optional[float] = None
    ):
        """Log LLM completion event."""
        data = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "duration_s": round(duration_s, 2)
        }
        if ttft_s is not None:
            data["ttft_s"] = round(ttft_s, 2)

        self.log("llm_completion", data)

    def log_tts_metrics(self, characters: int, audio_duration_s: float):
        """Log TTS generation event."""
        self.log("tts_generation", {
            "characters": characters,
            "audio_duration_s": round(audio_duration_s, 2)
        })


# Global instance for easy import
json_logger = JSONLogger()
