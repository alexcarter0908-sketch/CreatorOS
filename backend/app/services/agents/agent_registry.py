from typing import Type

from app.services.agents.base_agent import BaseAgent

from app.services.agents.chat_agent import ChatAgent
from app.services.agents.thumbnail_agent import ThumbnailAgent
from app.services.agents.image_agent import ImageAgent
from app.services.agents.video_agent import VideoAgent
from app.services.agents.voice_agent import VoiceAgent
from app.services.agents.script_agent import ScriptAgent
from app.services.agents.seo_agent import SEOAgent
from app.services.agents.document_agent import DocumentAgent
from app.services.agents.research_agent import ResearchAgent
from app.services.agents.website_agent import WebsiteAgent
from app.services.agents.app_agent import AppAgent
from app.services.agents.marketing_agent import MarketingAgent
from app.services.agents.automation_agent import AutomationAgent
from app.services.agents.dubbing_agent import DubbingAgent


class AgentRegistry:
    """
    CreatorOS Agent Registry
    """

    _agents: dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent,
        "thumbnail": ThumbnailAgent,
        "image": ImageAgent,
        "video": VideoAgent,

        # Voice / Audio
        "voice": VoiceAgent,
        "audio": VoiceAgent,

        "script": ScriptAgent,
        "seo": SEOAgent,
        "document": DocumentAgent,
        "research": ResearchAgent,
        "website": WebsiteAgent,
        "app": AppAgent,
        "marketing": MarketingAgent,
        "automation": AutomationAgent,
        "dub": DubbingAgent,
    }

    @classmethod
    def register(
        cls,
        name: str,
        agent_class: Type[BaseAgent],
    ) -> None:
        cls._agents[name.lower()] = agent_class

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> None:
        cls._agents.pop(name.lower(), None)

    @classmethod
    def exists(
        cls,
        name: str,
    ) -> bool:
        return name.lower() in cls._agents

    @classmethod
    def get(
        cls,
        name: str,
    ) -> BaseAgent:
        agent_class = cls._agents.get(
            name.lower(),
            ChatAgent,
        )
        return agent_class()

    @classmethod
    def available_agents(
        cls,
    ) -> list[str]:
        return sorted(cls._agents.keys())