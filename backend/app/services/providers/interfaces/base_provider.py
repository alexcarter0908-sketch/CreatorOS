from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseProvider(ABC):
    """
    Base interface for every AI provider.

    All providers (OpenAI, Gemini, Claude, etc.)
    must implement these methods.
    """

    name: str

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs,
    ) -> str:
        """
        Generate a text response.
        """
        pass

    @abstractmethod
    async def image(
        self,
        prompt: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate an image.
        """
        pass

    @abstractmethod
    async def video(
        self,
        prompt: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a video.
        """
        pass

    @abstractmethod
    async def audio(
        self,
        prompt: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate speech or audio.
        """
        pass

    @abstractmethod
    async def embeddings(
        self,
        text: str,
    ) -> List[float]:
        """
        Generate embeddings.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check provider availability.
        """
        pass