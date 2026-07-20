from app.services.providers.registry.model import AIModel


KLING_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Kling 2.1
    # ==========================================================

    "kling-v2.1-master": AIModel(
        id="kling-v2.1-master",
        provider="kling",
        model="kling-v2.1-master",
        category="video",

        priority=1,

        quality="ultra",
        speed="medium",
        cost="high",

        supports_video=True,

        fallback=(
            "kling-v2",
            "runway-gen4",
        ),
    ),

    # ==========================================================
    # Kling 2.0
    # ==========================================================

    "kling-v2": AIModel(
        id="kling-v2",
        provider="kling",
        model="kling-v2",
        category="video",

        priority=2,

        quality="ultra",
        speed="medium",
        cost="medium",

        supports_video=True,

        fallback=(
            "runway-gen4",
        ),
    ),

    # ==========================================================
    # Image to Video
    # ==========================================================

    "kling-image-video": AIModel(
        id="kling-image-video",
        provider="kling",
        model="kling-image-to-video",
        category="video",

        priority=3,

        quality="high",
        speed="high",
        cost="medium",

        supports_video=True,
        supports_image=True,
    ),

}