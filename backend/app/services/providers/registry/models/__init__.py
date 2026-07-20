from .openai import OPENAI_MODELS
from .anthropic import ANTHROPIC_MODELS
from .gemini import GEMINI_MODELS
from .groq import GROQ_MODELS
from .deepseek import DEEPSEEK_MODELS
from .openrouter import OPENROUTER_MODELS
from .together import TOGETHER_MODELS
from .mistral import MISTRAL_MODELS
from .xai import XAI_MODELS
from .fal import FAL_MODELS
from .replicate import REPLICATE_MODELS
from .runway import RUNWAY_MODELS
from .kling import KLING_MODELS
from .pika import PIKA_MODELS
from .elevenlabs import ELEVENLABS_MODELS
from .fish_audio_models import FISH_AUDIO_MODELS
from .pixverse_models import PIXVERSE_MODELS
from .sogni_models import SOGNI_MODELS

ALL_MODELS = (
    OPENAI_MODELS
    + ANTHROPIC_MODELS
    + GEMINI_MODELS
    + GROQ_MODELS
    + DEEPSEEK_MODELS
    + OPENROUTER_MODELS
    + TOGETHER_MODELS
    + MISTRAL_MODELS
    + XAI_MODELS
    + FAL_MODELS
    + REPLICATE_MODELS
    + RUNWAY_MODELS
    + KLING_MODELS
    + PIKA_MODELS
    + ELEVENLABS_MODELS
    + list(FISH_AUDIO_MODELS.values())
    + list(PIXVERSE_MODELS.values())
    + list(SOGNI_MODELS.values())
)