from app.services.providers.base_provider import BaseProvider


class MockProvider(BaseProvider):

    name = "mock"

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):

        return {
            "success": True,
            "provider": self.name,
            "model": "mock-v1",
            "result": {
                "prompt": prompt,
                "message": "Mock provider executed successfully."
            },
        }