from app.services.providers.registry.model import AIModel


ANTHROPIC_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Claude 4 Family
    # ==========================================================

    "claude-opus-4": AIModel(
        id="claude-opus-4",
        provider="anthropic",
        model="claude-opus-4",
        category="text",

        priority=1,

        quality="ultra",
        speed="medium",
        cost="very_high",

        max_context=200000,

        supports_text=True,
        supports_vision=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_json_mode=True,

        fallback=(
            "claude-sonnet-4",
            "gpt-5.5",
        ),
    ),

    "claude-sonnet-4": AIModel(
        id="claude-sonnet-4",
        provider="anthropic",
        model="claude-sonnet-4",
        category="text",

        priority=2,

        quality="ultra",
        speed="high",
        cost="high",

        max_context=200000,

        supports_text=True,
        supports_vision=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_json_mode=True,

        fallback=(
            "gemini-2.5-pro",
        ),
    ),

    "claude-haiku-4": AIModel(
        id="claude-haiku-4",
        provider="anthropic",
        model="claude-haiku-4",
        category="text",

        priority=3,

        quality="high",
        speed="ultra",
        cost="low",

        max_context=200000,

        supports_text=True,
        supports_streaming=True,
        supports_reasoning=True,

        fallback=(
            "gpt-5-mini",
        ),
    ),

}