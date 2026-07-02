import os

from openai import AsyncOpenAI

from app.services.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):

    name = "openai"

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):

        response = await self.client.responses.create(
            model="gpt-5.5",
            input=prompt,
        )

        return {
            "success": True,
            "provider": self.name,
            "model": "gpt-5.5",
            "result": response.output_text,
        }