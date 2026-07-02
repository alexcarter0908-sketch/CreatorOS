from app.core.enums import ProviderType

from app.services.providers.implementations.openai_provider import OpenAIProvider
from app.services.providers.implementations.anthropic_provider import AnthropicProvider
from app.services.providers.implementations.gemini_provider import GeminiProvider
from app.services.providers.mock_provider import MockProvider


class ProviderFactory:
    """
    Responsible ONLY for creating provider instances.

    It does NOT:
    - select providers
    - select models
    - execute requests
    """

    def create(self, provider_name: str):

        try:
            provider = ProviderType(provider_name)
        except ValueError:
            return MockProvider()

        factories = {
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.ANTHROPIC: AnthropicProvider,
            ProviderType.GEMINI: GeminiProvider,
        }

        provider_class = factories.get(provider)

        if provider_class is None:
            return MockProvider()

        return provider_class()