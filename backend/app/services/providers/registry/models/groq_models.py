from app.services.providers.registry.model import AIModel


GROQ_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # Llama 4
    # ==========================================================

    "llama-4-scout": AIModel(
        id="llama-4-scout",
        provider="groq",
        model="llama-3.3-70b-versatile",
        category="text",

        priority=1,

        quality="ultra",
        speed="ultra",
        cost="low",

        max_context=131072,

        supports_text=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,

        fallback=(
            "llama-3.3-70b",
        ),
    ),

    # ==========================================================
    # Llama 3.3
    # ==========================================================

    "llama-3.3-70b": AIModel(
        id="llama-3.3-70b",
        provider="groq",
        model="llama-3.3-70b-versatile",
        category="text",

        priority=2,

        quality="ultra",
        speed="ultra",
        cost="low",

        max_context=131072,

        supports_text=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_function_calling=True,
    ),

    # ==========================================================
    # Llama 3.1
    # ==========================================================

    "llama-3.1-8b": AIModel(
        id="llama-3.1-8b",
        provider="groq",
        model="llama-3.1-8b-instant",
        category="text",

        priority=3,

        quality="high",
        speed="ultra",
        cost="very_low",

        max_context=131072,

        supports_text=True,
        supports_streaming=True,
    ),

    # ==========================================================
    # DeepSeek R1
    # ==========================================================

    "deepseek-r1-groq": AIModel(
        id="deepseek-r1-groq",
        provider="groq",
        model="deepseek-r1-distill-llama-70b",
        category="reasoning",

        priority=2,

        quality="ultra",
        speed="ultra",
        cost="low",

        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
    ),

    # ==========================================================
    # Qwen
    # ==========================================================

    "qwen-qwq-32b": AIModel(
        id="qwen-qwq-32b",
        provider="groq",
        model="qwen-qwq-32b",
        category="reasoning",

        priority=3,

        quality="high",
        speed="ultra",
        cost="low",

        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
    ),
}