from app.services.providers.registry.model import AIModel


RUNWAY_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Runway Gen-4
    # ==========================================================

    "runway-gen4": AIModel(
        id="runway-gen4",
        provider="runway",
        model="gen4.5",
        category="video",

        priority=1,

        quality="ultra",
        speed="high",
        cost="high",

        supports_video=True,

        fallback=(
            "runway-gen3",
            "kling-v2",
        ),
    ),

    # ==========================================================
    # Runway Gen-3 Turbo
    # ==========================================================

    "runway-gen3": AIModel(
        id="runway-gen3",
        provider="runway",
        model="gen3a_turbo",
        category="video",

        priority=2,

        quality="high",
        speed="very_high",
        cost="medium",

        supports_video=True,

        fallback=(
            "kling-v2",
        ),
    ),

    # ==========================================================
    # Image â†’ Video
    # ==========================================================

    "runway-image-video": AIModel(
        id="runway-image-video",
        provider="runway",
        model="image_to_video",
        category="video",

        priority=1,

        quality="ultra",
        speed="medium",
        cost="high",

        supports_video=True,
        supports_image=True,
    ),

}
