from __future__ import annotations

from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse
from app.services.agents.base_agent import BaseAgent
from app.services.research.web_search import web_search_with_sources


class ResearchAgent(BaseAgent):

    name = "research"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:

        request.asset_type = "text"

        search_context, sources = web_search_with_sources(
            request.prompt,
            max_results=6,
            deep=True,
        )

        request.prompt = f"""
You are an expert Research Analyst.

Perform deep structured research using the live web search results below
as your primary source of current, factual information. Prefer these
results over prior knowledge when they are relevant, since they reflect
the current state of the topic.

{search_context}

User Request:

{request.prompt}
"""

        request.metadata.update(
            {
                "pipeline": "research",
                "agent": self.name,
                "web_search_used": True,
            }
        )

        result = await self.generate(request)

        if sources:
            result.setdefault("metadata", {})
            result["metadata"]["sources"] = sources

        return result