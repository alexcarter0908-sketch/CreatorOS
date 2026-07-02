from abc import ABC, abstractmethod


class BaseProvider(ABC):

    name = "base"

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):
        """
        Execute AI request.

        Returns:

        {
            "success": bool,
            "provider": "...",
            "model": "...",
            "result": ...
        }
        """
        raise NotImplementedError