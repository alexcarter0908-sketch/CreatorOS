from __future__ import annotations

from app.schemas.ai_request import AIRequest
from app.services.agents.base_agent import BaseAgent


class VoiceAgent(BaseAgent):
    """
    Voice / Audio generation agent.
    """

    name = "voice"

    async def execute(
        self,
        request: AIRequest,
    ) -> dict:

        optimized_prompt = f"""
Generate high quality speech.

User Request:

{request.prompt}
"""

        request.prompt = optimized_prompt
        request.asset_type = "audio"

        return await self.generate(request)