"""
Compatibility layer.

Deprecated:
    New code should use AIOrchestrator directly.

This class exists only so older imports continue to work
until the migration is fully complete.
"""

from app.schemas.ai_request import AIRequest
from app.services.orchestrator.ai_orchestrator import AIOrchestrator


class AIRouter:

    def __init__(self):
        self.orchestrator = AIOrchestrator()

    async def execute(
        self,
        prompt: str,
        agent: str = "chat",
    ):

        request = AIRequest(
            prompt=prompt,
            asset_type="text",
        )

        response = await self.orchestrator.execute(
            agent=agent,
            request=request,
        )

        return response.model_dump()