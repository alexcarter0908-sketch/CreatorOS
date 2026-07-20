from __future__ import annotations

from app.services.providers.registry.model import AIModel

ELEVENLABS_MODELS = [
    AIModel(
        id="eleven-multilingual-v2",
        provider="elevenlabs",
        model="eleven_multilingual_v2",
        category="audio",
        display_name="Eleven Multilingual v2",
        description="ElevenLabs multilingual text-to-speech",

        enabled=True,
        priority=1,

        quality="highest",
        speed="fast",
        cost="medium",

        supports_audio=True,
        supports_text=False,
        supports_image=False,
        supports_video=False,
        supports_vision=False,
        supports_streaming=True,
    ),
]