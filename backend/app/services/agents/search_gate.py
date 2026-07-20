from __future__ import annotations

import json
import logging

logger = logging.getLogger("search_gate")

_CLASSIFIER_MODEL = "llama-3.3-70b-versatile"

_VALID_ASSET_TYPES = (
    "text", "script", "seo", "document", "research", "image", "video", "audio", "dub",
)

_CLASSIFIER_SYSTEM_PROMPT = """You are a routing classifier for an AI creator-tools assistant. \
Read the FULL conversation context (not just isolated words) and the user's newest message, \
then decide:

1. asset_type: what the user actually wants produced. One of:
   - "script": a written script/screenplay for a video, ad, or content piece
   - "seo": SEO titles, meta descriptions, keyword lists, or on-page SEO copy
   - "document": a downloadable Word document/file the user explicitly wants \
to save, download, or send (a pitch, proposal, report, or similar) -- only \
when they ask for an actual file/document, not just written text in chat
   - "research": a broad research/trend/market report
   - "image": an image, thumbnail, logo, poster, or picture
   - "video": an actual video file to be generated
   - "audio": a voiceover, speech, or audio/TTS file
   - "dub": the user wants an EXISTING video from this conversation translated \
and re-voiced into another language (e.g. "is video ko Urdu mein dub karo", \
"dub this in Spanish") -- only when a video was already generated earlier \
in this conversation and they want a dubbed/translated version of it
   - "text": anything else -- casual conversation, questions, general writing \
(captions, blog posts, articles), or any request that doesn't match the \
categories above

2. needs_search: true if answering well requires current/real-world/factual information \
this assistant cannot reliably know from memory (a specific business, person, place, price, \
news, "latest", addresses, contact info, or any named real-world entity). false for casual \
conversation, greetings, small talk, opinions, creative writing, or timeless general knowledge.

3. deep_search: true only if needs_search is true AND the question needs thorough, \
multi-source research (comparisons, "best X", detailed specifics). Otherwise false.

4. casual_reply: true if the newest message, understood together with the full conversation history, is casual conversation deserving a short natural reply (greetings, small talk, thanks, short remarks) rather than a full structured answer -- judge this from the whole sentence and its relation to prior turns, never from matching isolated words. false for any real question, request, or task, however short.

Judge intent from what the user is actually asking for, in context -- never from matching a \
single keyword. A message can mention a word like "video" while only asking a question about \
videos in general, not asking you to generate one; read the whole sentence.

This distinction matters most when the user is explaining or describing their own \
product/system and mentions a script/video/image only as an EXAMPLE within that explanation \
(e.g. "my system takes a command like 'make me a football video' and generates it \
automatically -- now write me a pitch about this for my client"). In cases like this the \
user's real goal is a pitch, explanation, overview, or description ABOUT the product for an \
audience/client -- classify that as "text", not as the example content type they mentioned \
while explaining.

Respond with ONLY a compact JSON object, nothing else, in this exact form:
{"asset_type": "text", "needs_search": false, "deep_search": false, "casual_reply": false}
"""


def _build_classifier_prompt(prompt: str, history: list[dict] | None) -> str:
    lines = []
    if history:
        lines.append("Recent conversation:")
        for turn in history[-6:]:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            speaker = "User" if role == "user" else "Assistant"
            lines.append(f"{speaker}: {content}")
        lines.append("")
    lines.append(f"Newest user message: {prompt}")
    return "\n".join(lines)


async def classify(prompt: str, history: list[dict] | None = None) -> dict:
    """
    Uses a small, fast LLM call to read the full conversation context and
    decide what the user wants (asset_type) and whether a live web search
    is needed, and how deep. This replaces brittle keyword matching so
    intent is understood from the whole sentence/conversation rather than
    triggering off isolated words (in any phrasing, including Roman Urdu).

    Returns a dict: {"asset_type": str | None, "needs_search": bool, "deep_search": bool}
    "asset_type" is None on failure so the caller can fall back to its own
    keyword-based detect_asset_type() as a safety net. needs_search
    defaults to True on failure (a missed search producing a fabricated
    answer is worse than an unnecessary one).
    """
    from app.services.providers.implementations.groq.groq_provider import GroqProvider

    try:
        provider = GroqProvider()
        user_prompt = _build_classifier_prompt(prompt, history)
        result = await provider.chat(
            model=_CLASSIFIER_MODEL,
            prompt=f"{_CLASSIFIER_SYSTEM_PROMPT}\n\n{user_prompt}",
            temperature=0,
        )
        raw = result.get("result", "") if isinstance(result, dict) else str(result)
        raw = raw.strip()

        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"No JSON object found in classifier output: {raw!r}")

        parsed = json.loads(raw[start : end + 1])

        asset_type = parsed.get("asset_type")
        if asset_type not in _VALID_ASSET_TYPES:
            asset_type = None

        needs_search = bool(parsed.get("needs_search", True))
        deep_search = bool(parsed.get("deep_search", False)) if needs_search else False
        casual_reply = bool(parsed.get("casual_reply", False))
        return {
            "asset_type": asset_type,
            "needs_search": needs_search,
            "deep_search": deep_search,
            "casual_reply": casual_reply,
        }
    except Exception:
        logger.exception("Intent classification failed; falling back to keyword detection.")
        return {"asset_type": None, "needs_search": True, "deep_search": False, "casual_reply": False}
