from app.services.providers.registry.model import AIModel


PIXVERSE_MODELS: dict[str, AIModel] = {

    "pixverse-v4": AIModel(
        id="pixverse-v4",
        provider="pixverse",
        model="v3.5",
        category="video",

        priority=50,

        quality="medium",
        speed="high",
        cost="very_low",

        supports_video=True,
    ),

}




