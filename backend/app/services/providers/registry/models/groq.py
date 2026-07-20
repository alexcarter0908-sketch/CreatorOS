from __future__ import annotations

from app.services.providers.registry.model import AIModel

GROQ_MODELS = [

    AIModel(
        id="llama-4-scout",
        provider="groq",
        model="llama-3.3-70b-versatile",
        category="text",
        priority=1,
        display_name="Llama 4 Scout",
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        fallback=(
            "llama-3.3-70b",
            "llama-3.1-8b",
            "qwen3-32b",
        ),
    ),

    AIModel(
        id="llama-3.3-70b",
        provider="groq",
        model="llama-3.3-70b-versatile",
        category="text",
        priority=2,
        display_name="Llama 3.3",
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        fallback=(
            "llama-3.1-8b",
            "qwen3-32b",
        ),
    ),

    AIModel(
        id="llama-3.1-8b",
        provider="groq",
        model="llama-3.1-8b-instant",
        category="text",
        priority=3,
        display_name="Llama 3.1 Instant",
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        fallback=(
            "qwen3-32b",
        ),
    ),

    AIModel(
        id="qwen3-32b",
        provider="groq",
        model="qwen/qwen3-32b",
        category="text",
        priority=4,
        display_name="Qwen3 32B",
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
    ),
]