from enum import Enum


class AgentType(str, Enum):
    SCRIPT = "script"
    THUMBNAIL = "thumbnail"
    VIDEO = "video"
    SEO = "seo"
    RESEARCH = "research"
    WORKFLOW = "workflow"
    UNKNOWN = "unknown"


class AIRouter:

    def route(self, command: str) -> AgentType:

        text = command.lower()

        if any(x in text for x in ["script", "write", "blog", "article"]):
            return AgentType.SCRIPT

        if any(x in text for x in ["thumbnail", "cover", "poster"]):
            return AgentType.THUMBNAIL

        if any(x in text for x in ["video", "short", "reel"]):
            return AgentType.VIDEO

        if any(x in text for x in ["seo", "keyword"]):
            return AgentType.SEO

        if any(x in text for x in ["research", "analyze"]):
            return AgentType.RESEARCH

        return AgentType.UNKNOWN

    async def execute(self, command: str):

        agent = self.route(command)

        return {
            "agent": agent.value,
            "status": "completed",
            "message": f"Command routed to {agent.value} agent.",
        }
