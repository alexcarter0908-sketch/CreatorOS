from __future__ import annotations
from app.schemas.ai_request import AIRequest
from app.services.agents.base_agent import BaseAgent
from app.services.agents.prompt_helpers import with_knowledge_context
from app.services.agents.search_gate import classify
from app.services.research.web_search import web_search_with_sources
import re


_SMALLTALK_PATTERNS = [
    r"^(hi+|hello+|hey+|heya|yo)[\s!.,]*$",
    r"^(assalam.?u.?alaikum|salam|salaam)[\s!.,]*$",
    r"^(good\s?morning|good\s?evening|good\s?afternoon|good\s?night)[\s!.,]*$",
    r"^(kya|kia|kea)\s?hal\s?(hai|hain|hy|h)?[\s!.,?]*$",
    r"^(kaisay?|kese)\s?ho[\s!.,?]*$",
    r"^(kaise\s?ho|how\s?are\s?you|kya\s?chal\s?raha\s?hai)[\s!.,?]*$",
    r"^(thanks|thank\s?you|shukriya|jazakallah)[\s!.,]*$",
    r"^(ok(ay)?|theek\s?hai|acha|achha)[\s!.,]*$",
    r"^(bye|khuda\s?hafiz|allah\s?hafiz|good\s?bye)[\s!.,]*$",
]


def _is_smalltalk(message: str) -> bool:
    """
    Deterministic, code-level check for very common greetings/small-talk.
    This is a safety net on top of the LLM-based intent classifier
    (classify(), which already reads the full conversation history and
    usually judges this correctly) - a short exchange like a bare "hi"
    or "kaise ho" is exactly the case where a fast classifier can
    occasionally misjudge, so this makes sure such messages NEVER
    trigger a web search regardless of what the classifier decided.
    """
    text = (message or "").strip().lower()
    if not text:
        return False
    return any(re.match(p, text) for p in _SMALLTALK_PATTERNS)


def _retrieve_knowledge_chunks(request: AIRequest) -> list[str]:
    """Fetch relevant chunks from the user's uploaded knowledge base, if any."""
    if not request.owner_id:
        return []

    from app.database.session.database import SessionLocal
    from app.services.knowledge.knowledge_service import KnowledgeService

    db = SessionLocal()
    try:
        kb = KnowledgeService(db)
        chunks = kb.retrieve_context(
            owner_id=request.owner_id,
            query=request.prompt,
            project_id=request.project_id,
        )
        return [c.content for c in chunks]
    except Exception:
        return []
    finally:
        db.close()


class ChatAgent(BaseAgent):

    name = "chat"

    async def execute(
        self,
        request: AIRequest,
    ) -> dict:

        intent = await classify(request.prompt, request.history)
        is_smalltalk = intent.get("casual_reply", False)
        knowledge_chunks = [] if is_smalltalk else _retrieve_knowledge_chunks(request)

        use_search = intent["needs_search"] and not is_smalltalk
        deep = intent["deep_search"] and use_search

        sources: list[dict] = []

        if use_search:
            # BUG FIX: search_query was previously only assigned inside the
            # block below, so any standalone message that didn't match that
            # narrow condition (a longer, self-contained message - exactly
            # the common case) used to leave search_query undefined before
            # it's used a few lines down. Default it to the current prompt
            # first, then only enrich it with recent history for the
            # specific case this was designed for: a short, context-
            # dependent follow-up (e.g. "wahan ka number?" after an earlier
            # message about a specific place).
            search_query = request.prompt
            if len(request.prompt.split()) <= 4 and request.history:
                recent_user_turns = [
                    h.get("content", "") for h in request.history if h.get("role") == "user"
                ][-3:]
                if recent_user_turns:
                    search_query = " ".join(recent_user_turns) + " " + request.prompt

            search_context, sources = web_search_with_sources(
                search_query,
                max_results=6 if deep else 4,
                deep=deep,
                lat=request.latitude,
                lng=request.longitude,
            )
            request.prompt = f"""
{search_context}

User message:

{request.prompt}
"""

        if knowledge_chunks:
            request.prompt = with_knowledge_context(request.prompt, knowledge_chunks)

        request.metadata.update(
            {
                "pipeline": "chat",
                "agent": self.name,
                "web_search_used": use_search,
                "deep_search": deep,
                "knowledge_chunks_used": len(knowledge_chunks),
            }
        )

        result = await self.generate(request, skip_accuracy_instruction=not (use_search or knowledge_chunks))

        if sources:
            result.setdefault("metadata", {})
            result["metadata"]["sources"] = sources

        return result
