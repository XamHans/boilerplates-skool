import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
)
from livekit.plugins import silero

from tools.department_hours_tool import getOpeningHours
from tools.knowledge_base_tool import queryKnowledgeBase
from transport_profiles import get_transport_profile
from utils.session_metrics import SessionMetricsHandler, on_session_end_callback


logger = logging.getLogger("lueneburg-agent")
load_dotenv(Path(__file__).resolve().parent.parent / ".env.local")

PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "lueneburg.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")


class LueneburgAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[getOpeningHours, queryKnowledgeBase],
        )


# Alias for backwards compatibility with tests
Assistant = LueneburgAssistant

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name=os.getenv("AGENT_NAME", ""), on_session_end=on_session_end_callback)
async def entrypoint(ctx: JobContext):
    logger.info("Agent joining room: %s", ctx.room.name)

    # Get transport profile configuration
    profile = get_transport_profile()

    session = AgentSession(
        stt=profile["stt"],
        llm=profile["llm"],
        tts=profile["tts"],
        vad=profile["vad"]
    )

    # Enable session metrics collection
    metrics_handler = SessionMetricsHandler(ctx.room.name, ctx.job.id)
    metrics_handler.attach_to_session(session)

    await session.start(
        room=ctx.room,
        agent=LueneburgAssistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=profile["noise_cancellation"],
            ),
        ),
    )

    await ctx.connect()
    await session.generate_reply(
        instructions=(
          "Guten Tag! Ich bin Ihr digitaler Assistent für die Hansestadt Lüneburg. "
          "Ich kann Ihnen bei Fragen zu städtischen Dienstleistungen, Öffnungszeiten und Verwaltungsangelegenheiten in Lüneburg helfen. "
        )
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Lüneburg VoiceBot Agent...")
    cli.run_app(server)
