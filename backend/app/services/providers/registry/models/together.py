from __future__ import annotations

from app.services.providers.registry.model import AIModel


TOGETHER_MODELS = [

    AIModel(
        id="together-auto",
        provider="together",
        model="auto",
        category="text",
        display_name="Together Auto",
        description="Automatically selects the best Together AI model",
        priority=1,
        quality="ultra",
        speed="high",
        cost="medium",
        max_context=131072,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        supports_tools=True,
        fallback=(
            "llama-3.3-70b-together",
            "openrouter-auto",
        ),
    ),

    AIModel(
        id="llama-3.3-70b-together",
        provider="together",
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
        category="text",
        display_name="Llama 3.3 70B Turbo",
        description="Fast Llama model on Together AI",
        priority=2,
        quality="high",
        speed="ultra",
        cost="low",
        max_context=131072,
        supports_text=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "qwen-2.5-72b-together",
            "openrouter-auto",
        ),
    ),

    AIModel(
        id="qwen-2.5-72b-together",
        provider="together",
        model="Qwen/Qwen2.5-72B-Instruct-Turbo",
        category="text",
        display_name="Qwen 2.5 72B",
        description="Qwen instruction model",
        priority=3,
        quality="ultra",
        speed="high",
        cost="low",
        max_context=131072,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "deepseek-v3-together",
            "openrouter-auto",
        ),
    ),

    AIModel(
        id="deepseek-v3-together",
        provider="together",
        model="deepseek-ai/DeepSeek-V3",
        category="reasoning",
        display_name="DeepSeek V3",
        description="DeepSeek V3 hosted on Together AI",
        priority=4,
        quality="ultra",
        speed="high",
        cost="low",
        max_context=131072,
        supports_text=True,
        supports_reasoning=True,
        supports_streaming=True,
        supports_json_mode=True,
        supports_function_calling=True,
        fallback=(
            "openrouter-auto",
        ),
    ),

    AIModel(
        id="flux-1-dev-together",
        provider="together",
        model="black-forest-labs/FLUX.1-dev",
        category="image",
        display_name="FLUX.1 Dev",
        description="Image generation via Together AI",
        priority=30,
        quality="ultra",
        speed="medium",
        cost="medium",
        supports_image=True,
        max_images=8,
        fallback=(
            "openrouter-flux",
        ),
    ),

]