"""Transport profile configuration for different connection types.

This module provides transport-specific configurations (TTS models, noise cancellation)
that can be easily swapped based on the TRANSPORT_PROFILE environment variable.
"""

import os
from typing import Any

from livekit import rtc
from livekit.plugins import elevenlabs, noise_cancellation, openai, silero


def get_transport_profile() -> dict[str, Any]:
    """Get transport profile configuration.

    Returns a dictionary of initialized plugins based on the TRANSPORT_PROFILE
    environment variable. Profiles optimize settings for different connection types.

    Profiles:
        - "web" (default): WebRTC with 48kHz audio, eleven_turbo_v2_5 TTS
        - "telephony": SIP with 8kHz audio, eleven_turbo_v2 TTS (optimized for phone lines)

    Returns:
        dict with keys: stt, llm, tts, vad, noise_cancellation

    Environment Variables:
        TRANSPORT_PROFILE: Profile name (case-insensitive, defaults to "web")
        ELEVEN_VOICE_ID: ElevenLabs voice ID (defaults to German voice)
    """
    profile_name = os.getenv("TRANSPORT_PROFILE", "web").lower()
    eleven_voice_id = os.getenv("ELEVEN_VOICE_ID", "hpp4J3VqNfWAUOO0d1Us")

    if profile_name == "telephony":
        return {
            "stt": openai.STT(),
            "llm": openai.responses.LLM(model="gpt-4o-mini"),
            "tts": elevenlabs.TTS(
                model="eleven_turbo_v2",  # Optimized for 8kHz phone lines
                voice_id=eleven_voice_id,
                language="de",  # Force German pronunciation for numbers/enumerations
            ),
            "vad": silero.VAD.load(),
            "noise_cancellation": lambda params: noise_cancellation.BVCTelephony(),
        }
    else:  # "web" profile (default)
        return {
            "stt": openai.STT(),
            "llm": openai.responses.LLM(model="gpt-4o-mini"),
            "tts": elevenlabs.TTS(
                model="eleven_turbo_v2_5",  # Higher quality for WebRTC
                voice_id=eleven_voice_id,
                language="de",  # Force German pronunciation for numbers/enumerations
            ),
            "vad": silero.VAD.load(),
            "noise_cancellation": lambda params: noise_cancellation.BVCTelephony()
            if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
            else noise_cancellation.BVC(),
        }
