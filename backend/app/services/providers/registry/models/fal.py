from __future__ import annotations

from app.services.providers.registry.model import AIModel


FAL_MODELS = [

    AIModel(
        id="flux-pro",
        provider="fal",
        model="fal-ai/flux-pro",
        category="image",
        display_name="FLUX Pro",
        description="Highest quality FLUX image generation",
        priority=1,
        quality="ultra",
        speed="high",
        cost="high",
        supports_image=True,
        max_images=8,
        fallback=(
            "flux-dev",
            "flux-schnell",
            "replicate-flux-pro",
        ),
    ),

    AIModel(
        id="flux-dev",
        provider="fal",
        model="fal-ai/flux/dev",
        category="image",
        display_name="FLUX Dev",
        description="Balanced FLUX model",
        priority=2,
        quality="high",
        speed="high",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "flux-schnell",
            "replicate-flux-pro",
        ),
    ),

    AIModel(
        id="flux-schnell",
        provider="fal",
        model="fal-ai/flux/schnell",
        category="image",
        display_name="FLUX Schnell",
        description="Ultra-fast FLUX model",
        priority=3,
        quality="medium",
        speed="ultra",
        cost="low",
        supports_image=True,
        max_images=8,
        fallback=(
            "replicate-flux-pro",
        ),
    ),

    AIModel(
        id="ideogram-v3",
        provider="fal",
        model="fal-ai/ideogram/v3",
        category="image",
        display_name="Ideogram v3",
        description="Typography specialist",
        priority=4,
        quality="ultra",
        speed="medium",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "replicate-flux-pro",
        ),
    ),

    AIModel(
        id="recraft-v3",
        provider="fal",
        model="fal-ai/recraft-v3",
        category="image",
        display_name="Recraft v3",
        description="Logo and branding",
        priority=5,
        quality="ultra",
        speed="high",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "replicate-flux-pro",
        ),
    ),

]