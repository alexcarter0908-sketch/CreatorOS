from __future__ import annotations

from app.services.providers.registry.model import AIModel


DEEPSEEK_MODELS = [

    AIModel(
        id="deepseek-chat",
        provider="deepseek",
        model="deepseek-chat",
        category="text",
        display_name="DeepSeek Chat",
        description="General purpose DeepSeek model",
        priority=1,
        quality="high",
        speed="high",
        cost="low",
        max_context=128000,
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "deepseek-reasoner",
        ),
    ),

    AIModel(
        id="deepseek-reasoner",
        provider="deepseek",
        model="deepseek-reasoner",
        category="reasoning",
        display_name="DeepSeek Reasoner",
        description="Advanced reasoning model",
        priority=2,
        quality="ultra",
        speed="medium",
        cost="low",
        max_context=128000,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "deepseek-chat",
        ),
    ),
]