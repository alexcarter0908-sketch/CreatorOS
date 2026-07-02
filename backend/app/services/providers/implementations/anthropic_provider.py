import os

from anthropic import AsyncAnthropic

from app.services.providers.base_provider import BaseProvider


class AnthropicProvider(BaseProvider):

    name = "anthropic"

    def __init__(self):

        self.client = AsyncAnthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
        )

    async def generate(
        self,
        prompt: str,
        **kwargs,
    ):

        response = await self.client.messages.create(
            model="claude-sonnet-4",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return {
            "success": True,
            "provider": self.name,
            "model": "claude-sonnet-4",
            "result": response.content[0].text,
        }