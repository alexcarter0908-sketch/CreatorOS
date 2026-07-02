from abc import ABC, abstractmethod

from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse
from app.services.providers.manager.provider_manager import ProviderManager


class BaseAgent(ABC):
    """
    Base class for all CreatorOS agents.
    """

    name = "base"

    def __init__(self):
        self.provider_manager = ProviderManager()

    @abstractmethod
    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """
        Execute an AI request.
        """
        raise NotImplementedError