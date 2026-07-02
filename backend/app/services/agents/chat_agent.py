from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.agents.base_agent import BaseAgent


class ChatAgent(BaseAgent):

    name = "chat"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:

        return await self.provider_manager.generate(
            request,
        )