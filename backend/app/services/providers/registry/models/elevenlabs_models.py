from app.services.providers.registry.model import AIModel


ELEVENLABS_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Eleven Multilingual V2
    # ==========================================================

    "eleven-multilingual-v2": AIModel(
        id="eleven-multilingual-v2",
        provider="elevenlabs",
        model="eleven_multilingual_v2",
        category="audio",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        supports_audio=True,

        fallback=(
            "eleven-turbo-v2",
        ),
    ),

    # ==========================================================
    # Eleven Turbo V2
    # ==========================================================

    "eleven-turbo-v2": AIModel(
        id="eleven-turbo-v2",
        provider="elevenlabs",
        model="eleven_turbo_v2",
        category="audio",

        priority=2,

        quality="high",
        speed="ultra",
        cost="low",

        supports_audio=True,
    ),

    # ==========================================================
    # Eleven Flash V2.5
    # ==========================================================

    "eleven-flash-v2.5": AIModel(
        id="eleven-flash-v2.5",
        provider="elevenlabs",
        model="eleven_flash_v2_5",
        category="audio",

        priority=3,

        quality="high",
        speed="ultra",
        cost="very_low",

        supports_audio=True,
    ),

    # ==========================================================
    # Speech To Text
    # ==========================================================

    "eleven-speech-to-text": AIModel(
        id="eleven-speech-to-text",
        provider="elevenlabs",
        model="scribe_v1",
        category="speech_to_text",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        supports_audio=True,
    ),

}