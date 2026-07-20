from app.schemas.ai_request import AIRequest
from app.services.orchestrator.ai_orchestrator import AIOrchestrator


class AIRouter:
    """
    CreatorOS Intelligent Router

    Responsibilities
    ----------------
    - Detect user intent
    - Select the correct AI Agent
    - Build AIRequest
    - Send request to AIOrchestrator

    This class NEVER:
    - Calls AI providers directly
    - Generates prompts
    - Executes workflows
    - Selects AI models
    """

    def __init__(self):

        self.orchestrator = AIOrchestrator()

    def detect_agent(
        self,
        command: str,
    ) -> str:

        text = command.lower()

        rules = {
            "thumbnail": ["thumbnail", "youtube thumbnail", "thumb", "cover"],
            "image": ["image", "photo", "picture", "illustration", "art", "logo", "poster", "banner"],
            "video": ["video", "short", "shorts", "reel", "movie", "animation"],
            "voice": ["voice", "speech", "audio", "tts", "voice over"],
            "script": ["script", "story", "blog", "article", "write"],
            "seo": ["seo", "keyword", "ranking", "meta title", "meta description"],
            "research": ["research", "analyze", "analysis", "compare", "study", "investigate"],
            "website": ["website", "landing page", "web page", "portfolio"],
            "app": ["app", "application", "mobile app", "android app", "ios app"],
            "marketing": ["marketing", "campaign", "facebook ads", "google ads", "promotion"],
            "automation": ["automation", "workflow", "pipeline", "auto publish", "scheduler"],
        }

        for agent, keywords in rules.items():
            if any(keyword in text for keyword in keywords):
                return agent

        return "chat"

    def detect_asset_type(
        self,
        agent: str,
    ) -> str:

        mapping = {
            "chat": "text",
            "script": "text",
            "research": "text",
            "seo": "text",
            "website": "text",
            "app": "text",
            "marketing": "text",
            "automation": "text",
            "thumbnail": "thumbnail",
            "image": "image",
            "video": "video",
            "voice": "voice",
        }

        return mapping.get(agent, "text")

    async def execute(
        self,
        command: str,
    ) -> dict:

        agent = self.detect_agent(command)

        request = AIRequest(
            prompt=command,
            asset_type=self.detect_asset_type(agent),
            workflow=agent,
            language="auto",
            quality="ultra",
            speed="balanced",
        )

        response = await self.orchestrator.execute(
            agent=agent,
            request=request,
        )

        return response.model_dump()
