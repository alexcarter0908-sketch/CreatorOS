from __future__ import annotations

from app.services.providers.registry.model import AIModel


RUNWAY_MODELS = [

    AIModel(
        id="runway-gen4",
        provider="runway",
        model="gen4.5",
        category="video",
        display_name="Runway Gen-4",
        description="Runway flagship video generation model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="high",
        supports_video=True,
        supports_image=True,
        max_video_seconds=30,
        fallback=(
            "runway-gen3-alpha",
        ),
    ),

    AIModel(
        id="runway-gen3-alpha",
        provider="runway",
        model="gen3a_turbo",
        category="video",
        display_name="Runway Gen-3 Alpha Turbo",
        description="Fast Runway video model",
        priority=2,
        quality="high",
        speed="ultra",
        cost="medium",
        supports_video=True,
        max_video_seconds=20,
    ),

]
