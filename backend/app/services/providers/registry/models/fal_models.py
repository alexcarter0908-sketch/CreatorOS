from app.services.providers.registry.model import AIModel


FAL_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # FLUX PRO
    # ==========================================================

    "flux-pro": AIModel(
        id="flux-pro",
        provider="fal",
        model="fal-ai/flux-pro",
        category="image",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        supports_image=True,

        fallback=(
            "flux-dev",
        ),
    ),

    # ==========================================================
    # FLUX DEV
    # ==========================================================

    "flux-dev": AIModel(
        id="flux-dev",
        provider="fal",
        model="fal-ai/flux/dev",
        category="image",

        priority=2,

        quality="high",
        speed="very_high",
        cost="low",

        supports_image=True,
    ),

    # ==========================================================
    # FLUX SCHNELL
    # ==========================================================

    "flux-schnell": AIModel(
        id="flux-schnell",
        provider="fal",
        model="fal-ai/flux/schnell",
        category="image",

        priority=3,

        quality="medium",
        speed="ultra",
        cost="very_low",

        supports_image=True,
    ),

    # ==========================================================
    # FLUX KONTEXT
    # ==========================================================

    "flux-kontext": AIModel(
        id="flux-kontext",
        provider="fal",
        model="fal-ai/flux-pro/kontext",
        category="image_edit",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        supports_image=True,
    ),

}