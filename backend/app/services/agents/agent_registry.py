from typing import Type

from app.services.agents.base_agent import BaseAgent
from app.services.agents.chat_agent import ChatAgent


class AgentRegistry:
    """
    Central registry for all CreatorOS agents.

    New agents should be registered here.
    """

    _agents: dict[str, Type[BaseAgent]] = {
        "chat": ChatAgent,
    }

    @classmethod
    def register(
        cls,
        name: str,
        agent_class: Type[BaseAgent],
    ) -> None:

        cls._agents[name.lower()] = agent_class

    @classmethod
    def get(
        cls,
        name: str,
    ) -> BaseAgent:

        agent = cls._agents.get(name.lower())

        if agent is None:
            agent = ChatAgent

        return agent()

    @classmethod
    def available_agents(
        cls,
    ) -> list[str]:

        return sorted(cls._agents.keys())