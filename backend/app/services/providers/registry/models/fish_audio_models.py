from app.services.providers.registry.model import AIModel


FISH_AUDIO_MODELS: dict[str, AIModel] = {

    "fish-s2.1-pro": AIModel(
        id="fish-s2.1-pro",
        provider="fish_audio",
        model="s2.1-pro-free",
        category="audio",

        priority=50,

        quality="high",
        speed="high",
        cost="very_low",

        supports_audio=True,
    ),

}
