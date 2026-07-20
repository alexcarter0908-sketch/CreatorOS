from __future__ import annotations

from app.services.providers.registry.model import AIModel


PIKA_MODELS = [

    AIModel(
        id="pika-2.2",
        provider="pika",
        model="pika-2.2",
        category="video",
        display_name="Pika 2.2",
        description="Latest Pika video generation model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="medium",
        supports_video=True,
        max_video_seconds=20,
        fallback=(
            "pika-2.1",
        ),
    ),

    AIModel(
        id="pika-2.1",
        provider="pika",
        model="pika-2.1",
        category="video",
        display_name="Pika 2.1",
        description="Fast Pika video model",
        priority=2,
        quality="high",
        speed="ultra",
        cost="low",
        supports_video=True,
        max_video_seconds=15,
    ),

]