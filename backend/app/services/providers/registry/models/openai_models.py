from app.services.providers.registry.model import AIModel


OPENAI_MODELS: dict[str, AIModel] = {

    # ==========================================================
    # GPT-5 Family
    # ==========================================================

    "gpt-5.5": AIModel(
        id="gpt-5.5",
        provider="openai",
        model="gpt-5.5",
        category="text",

        priority=1,

        quality="ultra",
        speed="high",
        cost="high",

        max_context=400000,

        supports_text=True,
        supports_streaming=True,
        supports_function_calling=True,
        supports_embeddings=True,
        supports_json_mode=True,
        supports_reasoning=True,
        supports_vision=True,

        fallback=(
            "gpt-5-mini",
            "gpt-5-nano",
        ),
    ),

    "gpt-5-mini": AIModel(
        id="gpt-5-mini",
        provider="openai",
        model="gpt-5-mini",
        category="text",

        priority=2,

        quality="high",
        speed="very_high",
        cost="medium",

        max_context=400000,

        supports_text=True,
        supports_streaming=True,
        supports_function_calling=True,
        supports_embeddings=True,
        supports_json_mode=True,
        supports_reasoning=True,
        supports_vision=True,

        fallback=(
            "gpt-5-nano",
        ),
    ),

    "gpt-5-nano": AIModel(
        id="gpt-5-nano",
        provider="openai",
        model="gpt-5-nano",
        category="text",

        priority=3,

        quality="medium",
        speed="ultra",
        cost="low",

        max_context=128000,

        supports_text=True,
        supports_streaming=True,
        supports_function_calling=True,
        supports_json_mode=True,
    ),

    # ==========================================================
    # Reasoning Models
    # ==========================================================

    "o4": AIModel(
        id="o4",
        provider="openai",
        model="o4",
        category="reasoning",

        priority=1,

        quality="ultra",
        speed="medium",
        cost="high",

        supports_text=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_streaming=True,
    ),

    "o4-mini": AIModel(
        id="o4-mini",
        provider="openai",
        model="o4-mini",
        category="reasoning",

        priority=2,

        quality="high",
        speed="high",
        cost="medium",

        supports_text=True,
        supports_reasoning=True,
        supports_function_calling=True,
        supports_streaming=True,
    ),

    # ==========================================================
    # Embeddings
    # ==========================================================

    "text-embedding-3-large": AIModel(
        id="text-embedding-3-large",
        provider="openai",
        model="text-embedding-3-large",
        category="embedding",

        supports_embeddings=True,
    ),

    "text-embedding-3-small": AIModel(
        id="text-embedding-3-small",
        provider="openai",
        model="text-embedding-3-small",
        category="embedding",

        supports_embeddings=True,
    ),

    # ==========================================================
    # Future Image Models
    # ==========================================================

    "gpt-image-1": AIModel(
        id="gpt-image-1",
        provider="openai",
        model="gpt-image-1",
        category="image",

        priority=1,

        quality="ultra",
        speed="medium",
        cost="high",

        supports_image=True,
    ),

    # ==========================================================
    # Future Audio
    # ==========================================================

    "gpt-tts": AIModel(
        id="gpt-tts",
        provider="openai",
        model="gpt-tts",
        category="audio",

        supports_audio=True,
    ),

}