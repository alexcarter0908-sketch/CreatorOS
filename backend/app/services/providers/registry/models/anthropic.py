from __future__ import annotations

from app.services.providers.registry.model import AIModel


ANTHROPIC_MODELS = [

    AIModel(
        id="claude-opus-4",
        provider="anthropic",
        model="claude-opus-4",
        category="text",
        display_name="Claude Opus 4",
        description="Anthropic flagship model",
        priority=1,
        quality="ultra",
        speed="medium",
        cost="high",
        max_context=200000,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "claude-sonnet-4",
        ),
    ),

    AIModel(
        id="claude-sonnet-4",
        provider="anthropic",
        model="claude-sonnet-4",
        category="text",
        display_name="Claude Sonnet 4",
        description="Balanced Claude model",
        priority=2,
        quality="ultra",
        speed="high",
        cost="medium",
        max_context=200000,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "claude-haiku-4",
        ),
    ),

    AIModel(
        id="claude-haiku-4",
        provider="anthropic",
        model="claude-haiku-4",
        category="text",
        display_name="Claude Haiku 4",
        description="Fast Claude model",
        priority=3,
        quality="high",
        speed="ultra",
        cost="low",
        max_context=200000,
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        fallback=(
            "claude-sonnet-4",
        ),
    ),
]