from __future__ import annotations

from app.services.providers.registry.model import AIModel


MISTRAL_MODELS = [

    AIModel(
        id="mistral-large",
        provider="mistral",
        model="mistral-large-latest",
        category="text",
        display_name="Mistral Large",
        description="Flagship Mistral model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="medium",
        max_context=128000,
        supports_text=True,
        supports_streaming=True,
        supports_reasoning=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "mistral-medium",
        ),
    ),

    AIModel(
        id="mistral-medium",
        provider="mistral",
        model="mistral-medium-latest",
        category="text",
        display_name="Mistral Medium",
        description="Balanced Mistral model",
        priority=2,
        quality="high",
        speed="high",
        cost="low",
        max_context=128000,
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "ministral-8b",
        ),
    ),

    AIModel(
        id="ministral-8b",
        provider="mistral",
        model="ministral-8b-latest",
        category="text",
        display_name="Ministral 8B",
        description="Lightweight Mistral model",
        priority=3,
        quality="medium",
        speed="ultra",
        cost="very_low",
        max_context=128000,
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        fallback=(
            "mistral-medium",
        ),
    ),

]