from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.agents.base_agent import BaseAgent


class AutomationAgent(BaseAgent):

    name = "automation"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:

        request.asset_type = "text"

        request.metadata.update(
            {
                "pipeline": "automation",
                "agent": self.name,
            }
        )

        return await self.generate(request)