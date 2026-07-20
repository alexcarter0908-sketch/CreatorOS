from __future__ import annotations

from app.services.providers.registry.model import AIModel


KLING_MODELS = [

    AIModel(
        id="kling-v2",
        provider="kling",
        model="kling-v2",
        category="video",
        display_name="Kling v2",
        description="Flagship Kling video generation model",
        priority=1,
        quality="ultra",
        speed="medium",
        cost="high",
        supports_video=True,
        max_video_seconds=30,
        fallback=(
            "kling-v1.6",
        ),
    ),

    AIModel(
        id="kling-v1.6",
        provider="kling",
        model="kling-v1.6",
        category="video",
        display_name="Kling v1.6",
        description="Balanced Kling video model",
        priority=2,
        quality="high",
        speed="high",
        cost="medium",
        supports_video=True,
        max_video_seconds=20,
    ),

]