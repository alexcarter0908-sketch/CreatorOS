from __future__ import annotations

from app.services.providers.registry.model import AIModel


REPLICATE_MODELS = [

    AIModel(
        id="replicate-flux-pro",
        provider="replicate",
        model="black-forest-labs/flux-pro",
        category="image",
        display_name="FLUX Pro (Replicate)",
        description="Replicate hosted FLUX Pro",
        priority=10,
        quality="ultra",
        speed="medium",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "replicate-flux-dev",
        ),
    ),

    AIModel(
        id="replicate-flux-dev",
        provider="replicate",
        model="black-forest-labs/flux-dev",
        category="image",
        display_name="FLUX Dev (Replicate)",
        description="Replicate hosted FLUX Dev",
        priority=11,
        quality="high",
        speed="high",
        cost="low",
        supports_image=True,
        max_images=8,
        fallback=(
            "replicate-sdxl",
        ),
    ),

    AIModel(
        id="replicate-sdxl",
        provider="replicate",
        model="stability-ai/sdxl",
        category="image",
        display_name="SDXL",
        description="Stable Diffusion XL",
        priority=12,
        quality="high",
        speed="high",
        cost="low",
        supports_image=True,
        max_images=8,
        fallback=(
            "imagen-4",
        ),
    ),

    AIModel(
        id="cogvideox",
        provider="replicate",
        model="thudm/cogvideox-5b",
        category="video",
        display_name="CogVideoX",
        description="Open-source video generation",
        priority=1,
        quality="high",
        speed="medium",
        cost="low",
        supports_video=True,
        max_video_seconds=10,
        fallback=(
            "svd-xt",
        ),
    ),

    AIModel(
        id="svd-xt",
        provider="replicate",
        model="stability-ai/stable-video-diffusion",
        category="video",
        display_name="Stable Video Diffusion",
        description="Image to video generation",
        priority=2,
        quality="medium",
        speed="high",
        cost="low",
        supports_video=True,
        max_video_seconds=8,
    ),

]