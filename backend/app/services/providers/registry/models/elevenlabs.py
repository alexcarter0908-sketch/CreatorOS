from __future__ import annotations

from app.services.providers.registry.model import AIModel


ELEVENLABS_MODELS = [

            AIModel(
        id="eleven-multilingual-v2",
        provider="elevenlabs",
        model="eleven_multilingual_v2",
        category="audio",
        display_name="Eleven Multilingual v2",
        description="High-quality multilingual text-to-speech",
        priority=1,
        quality="ultra",
        speed="high",
        cost="medium",
        supports_audio=True,
        max_audio_minutes=60,
        fallback=(
            "eleven-turbo-v2",
            "llama-4-scout",
        ),
    ),
    
    AIModel(
        id="eleven-turbo-v2",
        provider="elevenlabs",
        model="eleven_turbo_v2",
        category="audio",
        display_name="Eleven Turbo v2",
        description="Fast text-to-speech generation",
        priority=2,
        quality="high",
        speed="ultra",
        cost="low",
        supports_audio=True,
        max_audio_minutes=60,
    ),

    AIModel(
        id="eleven-scribe-v1",
        provider="elevenlabs",
        model="scribe_v1",
        category="audio",
        display_name="Eleven Scribe",
        description="Speech-to-text transcription",
        priority=3,
        quality="ultra",
        speed="high",
        cost="medium",
        supports_audio=True,
        max_audio_minutes=180,
    ),

]