class ThumbnailAgent:

    name = "thumbnail"

    def __init__(self, provider_manager):

        self.provider_manager = provider_manager

    async def execute(
        self,
        command: str,
    ):

        prompt = f"""
You are a professional YouTube thumbnail designer.

Create a detailed thumbnail generation prompt.

User Request:

{command}
"""

        response = await self.provider_manager.generate(
            prompt=prompt,
        )

        return {
            "agent": self.name,
            "status": "completed",
            "result": response["result"],
            "provider": response.get("provider"),
            "model": response.get("model"),
        }