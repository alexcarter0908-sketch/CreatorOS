from app.services.providers.registry.model import AIModel


SOGNI_MODELS: dict[str, AIModel] = {

    "sogni-z-image-turbo": AIModel(
        id="sogni-z-image-turbo",
        provider="sogni",
        model="z-image-turbo",
        category="image",

        priority=50,

        quality="medium",
        speed="ultra",
        cost="very_low",

        supports_image=True,
    ),

}
