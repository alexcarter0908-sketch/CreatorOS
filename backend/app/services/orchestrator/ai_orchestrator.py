from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.agents.agent_registry import AgentRegistry


class AIOrchestrator:
    """
    Central AI execution pipeline.
    """

    async def execute(
        self,
        agent: str,
        request: AIRequest,
    ) -> AIResponse:

        selected_agent = AgentRegistry.get(agent)

        return await selected_agent.execute(
            request,
        )