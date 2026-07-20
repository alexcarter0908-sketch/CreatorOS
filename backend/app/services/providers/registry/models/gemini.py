from __future__ import annotations

from app.services.providers.registry.model import AIModel


GEMINI_MODELS = [

    AIModel(
        id="gemini-2.5-pro",
        provider="gemini",
        model="gemini-2.5-pro",
        category="text",
        display_name="Gemini 2.5 Pro",
        description="Google flagship multimodal model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="medium",
        max_context=1000000,
        supports_text=True,
        supports_vision=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_tools=True,
        fallback=(
            "gemini-2.5-flash",
            "gpt-5.5",
        ),
    ),

    AIModel(
        id="gemini-2.5-flash",
        provider="gemini",
        model="gemini-2.5-flash",
        category="text",
        display_name="Gemini 2.5 Flash",
        description="Fast Gemini model",
        priority=2,
        quality="high",
        speed="ultra",
        cost="low",
        max_context=1000000,
        supports_text=True,
        supports_vision=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_tools=True,
        fallback=(
            "gpt-5.5",
        ),
    ),

    AIModel(
        id="imagen-4",
        provider="gemini",
        model="imagen-4",
        category="image",
        display_name="Imagen 4",
        description="Google image generation",
        priority=15,
        quality="ultra",
        speed="medium",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "gpt-image-1",
        ),
    ),

    AIModel(
        id="veo-3",
        provider="gemini",
        model="veo-3",
        category="video",
        display_name="Veo 3",
        description="Google video generation",
        priority=1,
        quality="ultra",
        speed="medium",
        cost="high",
        supports_video=True,
    ),

]