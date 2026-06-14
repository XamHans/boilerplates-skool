"""Session metrics collection and logging.

This module handles all metrics collection for agent sessions, keeping
the main agent.py clean and focused on core logic.
"""

import logging
import time
from typing import Optional

from livekit.agents import AgentSession, metrics
from livekit.agents.voice import MetricsCollectedEvent

from .json_logger import json_logger

logger = logging.getLogger("session-metrics")


class SessionMetricsHandler:
    """Handles metrics collection for an agent session."""

    def __init__(self, room_name: str, session_id: str):
        """Initialize metrics handler.

        Args:
            room_name: Name of the room
            session_id: Session/job ID
        """
        self.room_name = room_name
        self.session_id = session_id
        self.start_time = time.time()
        self.usage_collector = metrics.UsageCollector()

        # Log session start
        json_logger.log_session_start(
            room=room_name,
            session_id=session_id
        )

    def on_metrics_collected(self, event: MetricsCollectedEvent) -> None:
        """Callback for metrics collected events.

        Args:
            event: Metrics event from LLM/TTS/STT
        """
        self.usage_collector.collect(event.metrics)

    def attach_to_session(self, session: AgentSession) -> None:
        """Attach metrics collection to a session.

        Args:
            session: The agent session to monitor
        """
        # Store handler reference on session for cleanup
        session._metrics_handler = self

        # Subscribe to metrics events
        @session.on("metrics_collected")
        def _on_metrics(event: MetricsCollectedEvent):
            self.on_metrics_collected(event)

    def log_session_end(self) -> None:
        """Log session end with collected metrics."""
        duration_s = time.time() - self.start_time
        summary = self.usage_collector.get_summary()

        # Aggregate LLM usage
        llm_prompt_tokens = sum(u.prompt_tokens for u in summary.llm_usage)
        llm_completion_tokens = sum(u.completion_tokens for u in summary.llm_usage)

        # Aggregate TTS usage
        tts_characters = sum(u.characters_count for u in summary.tts_usage)
        tts_audio_duration_s = sum(u.audio_duration for u in summary.tts_usage)

        # Aggregate STT usage
        stt_audio_duration_s = sum(u.audio_duration for u in summary.stt_usage)

        json_logger.log_session_end(
            duration_s=duration_s,
            llm_prompt_tokens=llm_prompt_tokens,
            llm_completion_tokens=llm_completion_tokens,
            tts_characters=tts_characters,
            tts_audio_duration_s=tts_audio_duration_s,
            stt_audio_duration_s=stt_audio_duration_s,
        )


async def on_session_end_callback(session: AgentSession) -> None:
    """Callback invoked when session ends.

    This is the callback function to pass to @server.rtc_session(on_session_end=...).

    Args:
        session: The agent session that ended
    """
    handler: Optional[SessionMetricsHandler] = getattr(session, "_metrics_handler", None)
    if handler:
        handler.log_session_end()
