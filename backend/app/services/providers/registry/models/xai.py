from __future__ import annotations

from app.services.providers.registry.model import AIModel


XAI_MODELS = [

    AIModel(
        id="grok-4",
        provider="xai",
        model="grok-4",
        category="text",
        display_name="Grok 4",
        description="xAI flagship reasoning model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="high",
        max_context=256000,
        supports_text=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_tools=True,
        fallback=(
            "grok-3",
        ),
    ),

    AIModel(
        id="grok-3",
        provider="xai",
        model="grok-3",
        category="text",
        display_name="Grok 3",
        description="Balanced xAI model",
        priority=2,
        quality="ultra",
        speed="high",
        cost="medium",
        max_context=131072,
        supports_text=True,
        supports_reasoning=True,
        supports_vision=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "grok-3-mini",
        ),
    ),

    AIModel(
        id="grok-3-mini",
        provider="xai",
        model="grok-3-mini",
        category="text",
        display_name="Grok 3 Mini",
        description="Fast and economical Grok model",
        priority=3,
        quality="high",
        speed="ultra",
        cost="low",
        max_context=131072,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
    ),

]