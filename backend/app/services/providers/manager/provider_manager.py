from __future__ import annotations

from app.schemas.ai_request import AIRequest

from app.services.providers.executor.provider_executor import (
    ProviderExecutor,
)


class ProviderManager:
    """
    High-level Provider Manager
    """

    def __init__(self):

        self.executor = ProviderExecutor()

    # ---------------------------------------------------------

    async def generate(
        self,
        request: AIRequest,
    ) -> dict:

        return await self.executor.execute(
            request,
        )

    # ---------------------------------------------------------

    async def health_report(
        self,
    ) -> dict[str, bool]:

        return await self.executor.health_report()

    # ---------------------------------------------------------

    def available_providers(
        self,
    ) -> list[str]:

        return self.executor.available_providers()

    # ---------------------------------------------------------

    def reload(self) -> list[str]:

        return self.executor.reload()