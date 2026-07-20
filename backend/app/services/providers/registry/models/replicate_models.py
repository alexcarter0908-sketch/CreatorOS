from app.services.providers.registry.model import AIModel


REPLICATE_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # FLUX DEV
    # ==========================================================

    "replicate-flux-dev": AIModel(
        id="replicate-flux-dev",
        provider="replicate",
        model="black-forest-labs/flux-dev",
        category="image",

        priority=2,

        quality="high",
        speed="high",
        cost="medium",

        supports_image=True,

        fallback=(
            "flux-pro",
        ),
    ),

    # ==========================================================
    # FLUX SCHNELL
    # ==========================================================

    "replicate-flux-schnell": AIModel(
        id="replicate-flux-schnell",
        provider="replicate",
        model="black-forest-labs/flux-schnell",
        category="image",

        priority=3,

        quality="medium",
        speed="ultra",
        cost="low",

        supports_image=True,
    ),

    # ==========================================================
    # SDXL
    # ==========================================================

    "sdxl": AIModel(
        id="sdxl",
        provider="replicate",
        model="stability-ai/sdxl",
        category="image",

        priority=4,

        quality="high",
        speed="medium",
        cost="low",

        supports_image=True,
    ),

    # ==========================================================
    # REAL-ESRGAN
    # ==========================================================

    "real-esrgan": AIModel(
        id="real-esrgan",
        provider="replicate",
        model="nightmareai/real-esrgan",
        category="upscaler",

        priority=1,

        quality="ultra",
        speed="high",
        cost="low",

        supports_image=True,
    ),

    # ==========================================================
    # REMOVE BACKGROUND
    # ==========================================================

    "remove-background": AIModel(
        id="remove-background",
        provider="replicate",
        model="remove-background",
        category="image_edit",

        priority=1,

        quality="ultra",
        speed="high",
        cost="low",

        supports_image=True,
    ),

}