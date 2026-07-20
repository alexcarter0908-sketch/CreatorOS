from app.services.providers.registry.model import AIModel


GEMINI_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Gemini 2.5
    # ==========================================================

    "gemini-2.5-pro": AIModel(
        id="gemini-2.5-pro",
        provider="gemini",
        model="gemini-2.5-pro",
        category="text",

        priority=1,

        quality="ultra",
        speed="high",
        cost="medium",

        max_context=1000000,

        supports_text=True,
        supports_vision=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_json_mode=True,

        fallback=(
            "gemini-2.5-flash",
            "gpt-5.5",
        ),
    ),

    "gemini-2.5-flash": AIModel(
        id="gemini-2.5-flash",
        provider="gemini",
        model="gemini-2.5-flash",
        category="text",

        priority=2,

        quality="high",
        speed="ultra",
        cost="low",

        max_context=1000000,

        supports_text=True,
        supports_vision=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_json_mode=True,

        fallback=(
            "gpt-5-mini",
        ),
    ),

    "gemini-2.5-flash-lite": AIModel(
        id="gemini-2.5-flash-lite",
        provider="gemini",
        model="gemini-2.5-flash-lite",
        category="text",

        priority=3,

        quality="medium",
        speed="ultra",
        cost="very_low",

        max_context=1000000,

        supports_text=True,
        supports_streaming=True,
    ),

    # ==========================================================
    # Embeddings
    # ==========================================================

    "gemini-embedding": AIModel(
        id="gemini-embedding",
        provider="gemini",
        model="gemini-embedding",
        category="embedding",

        supports_embeddings=True,
    ),

}