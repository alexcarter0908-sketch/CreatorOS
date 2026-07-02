from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True, frozen=True)
class AIModel:

    id: str
    provider: str
    model: str
    category: str

    quality: str
    speed: str
    cost: str

    supports_text: bool = False
    supports_image: bool = False
    supports_video: bool = False
    supports_audio: bool = False
    supports_vision: bool = False
    supports_streaming: bool = False
    supports_function_calling: bool = False

    max_context: int = 0

    enabled: bool = True


MODEL_REGISTRY: Dict[str, AIModel] = {

    # ---------- OpenAI ----------

    "gpt-5.5": AIModel(
        id="gpt-5.5",
        provider="openai",
        model="gpt-5.5",
        category="text",
        quality="ultra",
        speed="high",
        cost="high",
        supports_text=True,
        supports_streaming=True,
        supports_function_calling=True,
        supports_vision=True,
        max_context=400000,
    ),

    # ---------- Anthropic ----------

    "claude-sonnet-4": AIModel(
        id="claude-sonnet-4",
        provider="anthropic",
        model="claude-sonnet-4",
        category="text",
        quality="ultra",
        speed="high",
        cost="high",
        supports_text=True,
        supports_streaming=True,
        max_context=200000,
    ),

    # ---------- Gemini ----------

    "gemini-2.5-pro": AIModel(
        id="gemini-2.5-pro",
        provider="gemini",
        model="gemini-2.5-pro",
        category="text",
        quality="ultra",
        speed="high",
        cost="medium",
        supports_text=True,
        supports_vision=True,
        supports_streaming=True,
        max_context=1000000,
    ),

    # ---------- Image ----------

    "flux-pro": AIModel(
        id="flux-pro",
        provider="fal",
        model="flux-pro",
        category="image",
        quality="ultra",
        speed="medium",
        cost="medium",
        supports_image=True,
    ),

    # ---------- Video ----------

    "kling-v2": AIModel(
        id="kling-v2",
        provider="kling",
        model="kling-v2",
        category="video",
        quality="ultra",
        speed="medium",
        cost="high",
        supports_video=True,
    ),

    "runway-gen4": AIModel(
        id="runway-gen4",
        provider="runway",
        model="gen4",
        category="video",
        quality="ultra",
        speed="medium",
        cost="high",
        supports_video=True,
    ),

    # ---------- Audio ----------

    "elevenlabs-v2": AIModel(
        id="elevenlabs-v2",
        provider="elevenlabs",
        model="eleven_multilingual_v2",
        category="audio",
        quality="ultra",
        speed="high",
        cost="medium",
        supports_audio=True,
    ),
}