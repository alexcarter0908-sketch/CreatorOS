from __future__ import annotations

from dataclasses import dataclass
from typing import Type

from app.core.config import settings

from app.services.providers.base_provider import BaseProvider

from app.services.providers.implementations.elevenlabs.elevenlabs_provider import (
    ElevenLabsProvider,
)

from app.services.providers.implementations.fish_audio.fish_audio_provider import (
    FishAudioProvider,
)

from app.services.providers.implementations.pixverse.pixverse_provider import (
    PixVerseProvider,
)

from app.services.providers.implementations.sogni.sogni_provider import (
    SogniProvider,
)

from app.services.providers.implementations.runway.runway_provider import (
    RunwayProvider,
)

from app.services.providers.implementations.pika.pika_provider import (
    PikaProvider,
)

from app.services.providers.implementations.kling.kling_provider import (
    KlingProvider,
)

from app.services.providers.implementations.openai_provider import (
    OpenAIProvider,
)

from app.services.providers.implementations.gemini_provider import (
    GeminiProvider,
)

from app.services.providers.implementations.anthropic_provider import (
    AnthropicProvider,
)

from app.services.providers.implementations.groq.groq_provider import (
    GroqProvider,
)

from app.services.providers.implementations.fal.fal_provider import (
    FalProvider,
)

from app.services.providers.implementations.replicate.replicate_provider import (
    ReplicateProvider,
)

from app.services.providers.implementations.together.together_provider import (
    TogetherProvider,
)

from app.services.providers.implementations.openrouter.openrouter_provider import (
    OpenRouterProvider,
)

from app.services.providers.implementations.deepseek.deepseek_provider import (
    DeepSeekProvider,
)

from app.services.providers.implementations.mistral.mistral_provider import (
    MistralProvider,
)

from app.services.providers.implementations.xai.xai_provider import (
    XAIProvider,
)

@dataclass(slots=True)
class ProviderDefinition:

    id: str
    name: str

    provider_class: Type[BaseProvider] | None

    api_key_env: str

    enabled: bool = True

    priority: int = 100

    supports_text: bool = False
    supports_image: bool = False
    supports_video: bool = False
    supports_audio: bool = False

    @property
    def api_key(self) -> str:

        return getattr(
            settings,
            self.api_key_env,
            "",
        ).strip()

    @property
    def available(self) -> bool:

        return (
            self.enabled
            and self.provider_class is not None
            and bool(self.api_key)
        )


PROVIDER_REGISTRY: dict[str, ProviderDefinition] = {

    # =====================================================
    # TEXT PROVIDERS
    # =====================================================

    "groq": ProviderDefinition(
        id="groq",
        name="Groq",
        provider_class=GroqProvider,
        api_key_env="GROQ_API_KEY",
        priority=1,
        supports_text=True,
    ),

    "openai": ProviderDefinition(
        id="openai",
        name="OpenAI",
        provider_class=OpenAIProvider,
        api_key_env="OPENAI_API_KEY",
        priority=2,
        supports_text=True,
        supports_image=True,
    ),

    "gemini": ProviderDefinition(
        id="gemini",
        name="Google Gemini",
        provider_class=GeminiProvider,
        api_key_env="GEMINI_API_KEY",
        priority=3,
        supports_text=True,
        supports_image=True,
    ),

    "anthropic": ProviderDefinition(
        id="anthropic",
        name="Anthropic",
        provider_class=AnthropicProvider,
        api_key_env="ANTHROPIC_API_KEY",
        priority=4,
        supports_text=True,
    ),

    "openrouter": ProviderDefinition(
        id="openrouter",
        name="OpenRouter",
        provider_class=OpenRouterProvider,
        api_key_env="OPENROUTER_API_KEY",
        priority=5,
        supports_text=True,
        supports_image=True,
    ),

    "together": ProviderDefinition(
        id="together",
        name="Together AI",
        provider_class=TogetherProvider,
        api_key_env="TOGETHER_API_KEY",
        priority=6,
        supports_text=True,
        supports_image=True,
    ),

    "deepseek": ProviderDefinition(
        id="deepseek",
        name="DeepSeek",
        provider_class=DeepSeekProvider,
        api_key_env="DEEPSEEK_API_KEY",
        priority=7,
        supports_text=True,
    ),

    "mistral": ProviderDefinition(
        id="mistral",
        name="Mistral",
        provider_class=MistralProvider,
        api_key_env="MISTRAL_API_KEY",
        priority=8,
        supports_text=True,
    ),

    "xai": ProviderDefinition(
        id="xai",
        name="xAI",
        provider_class=XAIProvider,
        api_key_env="XAI_API_KEY",
        priority=9,
        supports_text=True,
    ),

    # =====================================================
    # IMAGE PROVIDERS
    # =====================================================

    "fal": ProviderDefinition(
        id="fal",
        name="Fal AI",
        provider_class=FalProvider,
        api_key_env="FAL_API_KEY",
        priority=20,
        supports_image=True,
    ),

    "replicate": ProviderDefinition(
        id="replicate",
        name="Replicate",
        provider_class=ReplicateProvider,
        api_key_env="REPLICATE_API_TOKEN",
        priority=21,
        supports_image=True,
    ),

    # =====================================================
    # VIDEO PROVIDERS
    # =====================================================

    "runway": ProviderDefinition(
        id="runway",
        name="Runway",
        provider_class=RunwayProvider,
        api_key_env="RUNWAY_API_KEY",
        priority=30,
        supports_video=True,
    ),

    "kling": ProviderDefinition(
        id="kling",
        name="Kling",
        provider_class=KlingProvider,
        api_key_env="KLING_ACCESS_KEY",
        priority=31,
        supports_video=True,
    ),

    "pika": ProviderDefinition(
    id="pika",
    name="Pika",
    provider_class=PikaProvider,
    api_key_env="FAL_API_KEY",   # <-- changed from PIKA_API_KEY
    priority=32,
    supports_video=True,
    ),

    # =====================================================
    # AUDIO PROVIDERS
    # =====================================================

    "elevenlabs": ProviderDefinition(
        id="elevenlabs",
        name="ElevenLabs",
        provider_class=ElevenLabsProvider,
        api_key_env="ELEVENLABS_API_KEY",
        priority=40,
        supports_audio=True,
    ),
    "fish_audio": ProviderDefinition(
        id="fish_audio",
        name="Fish Audio",
        provider_class=FishAudioProvider,
        api_key_env="FISH_AUDIO_API_KEY",
        priority=50,
        supports_audio=True,
    ),

    "pixverse": ProviderDefinition(
        id="pixverse",
        name="PixVerse",
        provider_class=PixVerseProvider,
        api_key_env="PIXVERSE_API_KEY",
        priority=51,
        supports_video=True,
    ),

    "sogni": ProviderDefinition(
        id="sogni",
        name="Sogni",
        provider_class=SogniProvider,
        api_key_env="SOGNI_API_KEY",
        priority=52,
        supports_image=True,
    ),
}
