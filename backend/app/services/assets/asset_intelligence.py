from __future__ import annotations

from app.schemas.ai_request import AIRequest

from app.services.providers.manager.provider_manager import (
    ProviderManager,
)


class AssetIntelligence:
    """
    Central AI execution layer.

    Every agent communicates with AI providers through this class.

    Flow
    ----
    Agent
        ↓
    AssetIntelligence
        ↓
    ProviderManager
        ↓
    ProviderExecutor
        ↓
    AI Provider
    """

    def __init__(self):

        self.provider_manager = ProviderManager()

    # ---------------------------------------------------------

    async def generate(
        self,
        request: AIRequest,
    ) -> dict:

        return await self.provider_manager.generate(
            request,
        )

    # ---------------------------------------------------------

    async def health_report(
        self,
    ) -> dict[str, bool]:

        return await self.provider_manager.health_report()

    # ---------------------------------------------------------

    def available_providers(
        self,
    ) -> list[str]:

        return self.provider_manager.available_providers()