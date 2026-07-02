import os

from google import genai

from app.services.providers.base_provider import BaseProvider


class GeminiProvider(BaseProvider):

    name = "gemini"

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
        )

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
        )

        return {
            "success": True,
            "provider": self.name,
            "model": "gemini-2.5-pro",
            "result": response.text,
        }