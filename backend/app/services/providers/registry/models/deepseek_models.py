from app.services.providers.registry.model import AIModel


DEEPSEEK_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # DeepSeek Chat
    # ==========================================================

    "deepseek-chat": AIModel(
        id="deepseek-chat",
        provider="deepseek",
        model="deepseek-chat",
        category="text",

        priority=1,

        quality="ultra",
        speed="high",
        cost="very_low",

        max_context=128000,

        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,

        fallback=(
            "deepseek-reasoner",
            "gpt-5-mini",
        ),
    ),

    # ==========================================================
    # DeepSeek Reasoner
    # ==========================================================

    "deepseek-reasoner": AIModel(
        id="deepseek-reasoner",
        provider="deepseek",
        model="deepseek-reasoner",
        category="reasoning",

        priority=2,

        quality="ultra",
        speed="medium",
        cost="low",

        max_context=128000,

        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,

        fallback=(
            "gpt-5.5",
        ),
    ),

}