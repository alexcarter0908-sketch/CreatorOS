from typing import Any


class MockProvider:
    """
    Development fallback provider.

    Used when no real AI provider is configured.
    """

    name = "mock"

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):

        return {
            "success": True,
            "provider": self.name,
            "model": "mock-model",
            "result": f"[MOCK RESPONSE]\n\n{prompt}",
            "metadata": {
                "mock": True,
            },
        }

    async def chat(self, messages, **kwargs):

        return "Mock chat response."

    async def image(self, prompt: str, **kwargs):

        return {
            "url": "",
            "prompt": prompt,
        }

    async def video(self, prompt: str, **kwargs):

        return {
            "url": "",
            "prompt": prompt,
        }

    async def audio(self, prompt: str, **kwargs):

        return {
            "url": "",
            "prompt": prompt,
        }

    async def embeddings(self, text: str):

        return []

    async def health_check(self):

        return True