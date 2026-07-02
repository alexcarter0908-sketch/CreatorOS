from app.services.router import AIRouter


class CommandService:

    def __init__(self):
        self.router = AIRouter()

    async def execute(
        self,
        command: str,
    ):
        return await self.router.execute(command)