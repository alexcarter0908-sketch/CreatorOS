from __future__ import annotations

from app.schemas.ai_request import AIRequest
from app.services.agents.agent_registry import AgentRegistry


class AIOrchestrator:
    """
    CreatorOS AI Orchestrator
    """

    def __init__(self):
        self.registry = AgentRegistry()

    async def execute(
        self,
        request: AIRequest,
    ) -> dict:

        agent = self.registry.get(
            request.asset_type,
        )

        return await agent.execute(
            request,
        )

    async def health_report(
        self,
    ) -> dict:

        report = {}

        for name in self.registry.available_agents():

            try:

                agent = self.registry.get(name)

                if hasattr(agent, "health_check"):
                    report[name] = await agent.health_check()
                else:
                    report[name] = True

            except Exception:

                report[name] = False

        return report