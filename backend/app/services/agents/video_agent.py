from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse

from app.services.agents.base_agent import BaseAgent


class VideoAgent(BaseAgent):
    """
    CreatorOS Video Agent

    Responsibilities
    ----------------
    - Convert user request into an optimized video generation prompt
    - Select video asset type
    - Forward request to ProviderManager

    Future
    ------
    - Storyboard generation
    - Scene planning
    - Camera movement
    - Character consistency
    - Subtitle generation
    - Voice synchronization
    - Background music
    - Auto publishing
    """

    name = "video"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:

        request.asset_type = "video"

        request.prompt = f"""
You are an expert AI Video Director.

Generate a production-ready AI video.

Requirements:

- Ultra high quality
- Cinematic lighting
- Professional composition
- Smooth camera movement
- Consistent characters
- Realistic animation
- Detailed environment
- Suitable for social media
- Maximum visual quality

User Request:

{request.prompt}
"""

        request.metadata.update(
            {
                "pipeline": "video_generation",
                "agent": self.name,
                "optimize_prompt": True,
            }
        )

        return await self.generate(request)