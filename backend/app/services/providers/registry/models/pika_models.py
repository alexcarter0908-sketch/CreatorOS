from app.services.providers.registry.model import AIModel


PIKA_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Pika 2.2
    # ==========================================================

    "pika-2.2": AIModel(
        id="pika-2.2",
        provider="pika",
        model="pika-2.2",
        category="video",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        supports_video=True,

        fallback=(
            "pika-2.1",
            "kling-v2",
        ),
    ),

    # ==========================================================
    # Pika 2.1
    # ==========================================================

    "pika-2.1": AIModel(
        id="pika-2.1",
        provider="pika",
        model="pika-2.1",
        category="video",

        priority=2,

        quality="high",
        speed="very_high",
        cost="low",

        supports_video=True,

        fallback=(
            "runway-gen4",
        ),
    ),

    # ==========================================================
    # Image → Video
    # ==========================================================

    "pika-image-video": AIModel(
        id="pika-image-video",
        provider="pika",
        model="image-to-video",
        category="video",

        priority=3,

        quality="high",
        speed="high",
        cost="medium",

        supports_video=True,
        supports_image=True,
    ),

}