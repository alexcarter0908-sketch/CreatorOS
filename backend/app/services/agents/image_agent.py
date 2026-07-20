from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.agents.base_agent import BaseAgent


class ImageAgent(BaseAgent):
    """
    CreatorOS Image Generation Agent.
    """

    name = "image"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:

        request.asset_type = "image"

        request.prompt = f"""
You are an expert AI Image Prompt Engineer.

Create an ultra realistic, professional quality image.

Requirements:

- Photorealistic
- High detail
- Cinematic lighting
- Professional composition
- Maximum quality

User Request:

{request.prompt}
"""

        request.metadata.update(
            {
                "pipeline": "image_generation",
                "agent": self.name,
            }
        )

        return await self.generate(request)
