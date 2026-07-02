from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.providers.selector.provider_selector import ProviderSelector
from app.services.providers.factory.provider_factory import ProviderFactory
from app.services.providers.executor.provider_executor import ProviderExecutor


class ProviderManager:
    """
    Facade for the Provider Layer.

    Flow:
        AIRequest
            ↓
        ProviderSelector
            ↓
        ProviderFactory
            ↓
        ProviderExecutor
            ↓
        AIResponse
    """

    def __init__(self):

        self.selector = ProviderSelector()
        self.factory = ProviderFactory()
        self.executor = ProviderExecutor()

    async def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:

        model = self.selector.select(
            asset_type=request.asset_type,
            quality=request.quality,
            speed=request.speed,
        )

        provider = self.factory.create(
            model.provider,
        )

        result = await self.executor.execute(
            provider=provider,
            prompt=request.prompt,
            model=model.name,
            **request.metadata,
        )

        return AIResponse(
            success=result.get("success", True),
            provider=result.get("provider", model.provider),
            model=result.get("model", model.name),
            result=result.get("result"),
            language=request.language,
            metadata=result.get("metadata", {}),
        )