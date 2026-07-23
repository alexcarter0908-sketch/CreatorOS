from __future__ import annotations
from typing import Any
import re

def with_conversation_history(prompt: str, history: list[dict[str, Any]] | None) -> str:
    if not history: return prompt
    history_str = "\n".join([f"{h['role']}: {h['content']}" for h in history])
    return f"{history_str}\nuser: {prompt}"

def with_language_instruction(prompt: str) -> str:
    return (
        f"{prompt}\n\n"
        "[LANGUAGE RULE]\n"
        "Detect the language/script of the user's CURRENT (most recent) message only - do NOT copy the language used earlier in the conversation history. "
        "If the current message is in English, reply fully in English. If it is in Roman Urdu, reply in Roman Urdu. If it is in Urdu script, reply in Urdu script. "
        "The language can change from one message to the next - always follow the latest message, never the previous pattern.\n"
        "EXCEPTION - QUOTED TITLES/PHRASES: look for any text inside quotation marks (\"...\") anywhere in the user's message, no matter what language the rest of the message is in. That exact quoted text names a specific title, headline, or topic phrase in its OWN language, and you must treat it as a fixed proper-noun-like label - do NOT translate it, do NOT paraphrase it into the main message's language, and do NOT explain its meaning in another language instead of using it directly. Any content you generate that covers that exact topic (a script, a caption, a title, a heading) should use that quoted text verbatim, in its original language, as the actual topic/title - even while all your other surrounding sentences stay in the main message's language.\n"
        "Concrete example: user writes (in Roman Urdu) - Ek video banao jiska topic hai \"5 morning habits for productivity\" - the surrounding reply stays in Roman Urdu, but the video's actual title/topic line must literally read \"5 morning habits for productivity\" in English, not a Roman Urdu translation of that idea."
    )


def with_brand_voice_instruction(prompt: str, brand_voice: str | None) -> str:
    """
    Optional per-project brand voice/style guide, set by the user in
    their Project settings. If the project has none set, the prompt
    is returned completely unchanged - this only adds instructions
    when the user has actually opted in by filling in a brand voice.
    """
    if not brand_voice or not brand_voice.strip():
        return prompt
    return (
        f"{prompt}\n\n"
        "[BRAND VOICE]\n"
        "The user has defined a specific brand voice/style for this "
        "project. Follow it closely for tone, vocabulary, and style, "
        "while still obeying the language rule above (brand voice "
        "affects style, not which language/script you respond in):\n"
        f"{brand_voice.strip()}"
    )


def with_location_context(prompt: str, latitude: float | None, longitude: float | None) -> str:
    """
    Optional user location, sent by the frontend only after the user
    grants browser location permission. If not available, the prompt
    is returned completely unchanged - the assistant simply has no
    location context, exactly like before this feature existed.
    """
    if latitude is None or longitude is None:
        return prompt
    return (
        f"{prompt}\n\n"
        "[USER LOCATION]\n"
        f"The user's current GPS coordinates are latitude {latitude}, "
        f"longitude {longitude}. If they ask about anything near them "
        "(restaurants, shops, services, \"near me\" style questions), "
        "use this as their actual location - do not guess or assume a "
        "different city. If the request is not location-related, ignore "
        "this entirely."
    )

def with_identity_instruction(prompt: str, app_name: str) -> str:
    """
    Only kicks in when the user actually asks about the assistant's own
    identity/features/limitations - it does not change normal answers.
    Without this, the underlying model falls back to a generic "I am an
    AI" textbook answer with no mention of this product at all.
    """
    return (
        f"{prompt}\n\n"
        "[IDENTITY RULE - only relevant if the user asks who/what you are, "
        "your name, your creator, your features, or your limitations]\n"
        f"You are the AI assistant built into {app_name}, an AI content-creation "
        "platform. "
        f"If asked ONLY for your name (e.g. 'what is your name', 'what are you called') - "
        f"answer in ONE short sentence: state your name is {app_name}, nothing more, no "
        "feature list, no headings.\n"
        "If asked to introduce yourself or explain your features (a broader request than "
        "just your name), do NOT give a generic textbook "
        "definition of 'what is AI' (no vague buzzwords like 'Natural Language "
        "Processing' or 'Knowledge Base' with zero specifics). Instead give a "
        "specific, honest answer covering:\n"
        f"1. Identity: you are {app_name}'s AI assistant - say that plainly, first.\n"
        "2. Real capabilities available on this platform, described concretely: "
        "writing scripts/articles/blog posts, generating images and video, "
        "text-to-speech voiceovers, SEO content, live web research, thumbnails, "
        "marketing copy, landing pages/websites, simple app scaffolding, "
        "scheduled automation pipelines, and publishing generated videos "
        "directly to YouTube.\n"
        "3. Real, honest limitations: you can get things wrong and should be "
        "double-checked for anything important; you don't have live access to "
        "the user's other apps/accounts beyond what they've explicitly connected "
        "here; generation quality depends on which underlying AI provider "
        "handled that specific request.\n"
        "4. Keep it conversational and specific to this platform - never a "
        "generic dictionary definition of artificial intelligence in general."
    )

def with_accuracy_instruction(prompt: str) -> str:
    return f"{prompt}\n\nEnsure your response is accurate and directly addresses the user's query."

def with_knowledge_context(prompt: str, knowledge_chunks: list[str]) -> str:
    if not knowledge_chunks: return prompt
    context_str = "\n".join(knowledge_chunks)
    return f"Context from knowledge base:\n{context_str}\n\nUser query: {prompt}"

def with_script_format_instruction(prompt: str) -> str:
    return f"{prompt}\n\nFormat the output as a professional production-ready script with timed beats."


def with_structured_answer_instruction(prompt: str) -> str:
    return (
        f"{prompt}\n\n"
        "[THOROUGH ANSWER RULE]\n"
        "1. Use ALL relevant variants/items found in the search results, not just the first "
        "one - e.g. if there are several unit types, plan tiers, or categories, cover each one "
        "found instead of picking a single example.\n"
        "2. Whenever the answer involves multiple numeric items (prices, plans, schedules, "
        "specs, comparisons), organize them as a clear table or clearly labeled breakdown - "
        "not a single paragraph of numbers.\n"
        "3. Break composite figures into their parts when the source does (e.g. booking %, "
        "possession %, monthly installments, one-time charges) instead of collapsing them "
        "into one number.\n"
        "4. Clearly separate confirmed/official information (official site, verified listing, "
        "primary source) from unconfirmed information (forum post, single video, unverified "
        "reseller listing) - label the unconfirmed parts explicitly as such.\n"
        "5. If complete official data isn't available in the search results, say so plainly "
        "instead of quietly presenting partial or unofficial numbers as the full picture.\n"
        "6. Be as complete and detailed as the search results allow - don't shorten a "
        "genuinely detailed answer just to sound more conversational."
    )


from datetime import datetime, timezone


def with_current_date(prompt: str) -> str:
    today = datetime.now(timezone.utc).strftime("%B %d, %Y")
    return (
        f"Today's real-world date is {today} (UTC). Use this as ground "
        "truth for anything time-sensitive (recent events, \"current\" "
        "anything, dates, schedules) - your own training data may be "
        "outdated, so prefer live information over your own memory "
        "when they conflict.\n\n"
        f"{prompt}"
    )


ROMAN_URDU_MARKERS = {
    "hai", "hain", "ka", "ki", "ke", "aur", "ko", "se", "mein", "nahi",
    "hum", "aap", "kya", "kar", "wala", "wali", "liye", "raha", "rahi",
    "tha", "thi", "the", "hoga", "hogi", "karna", "karte", "karo",
    "apna", "apni", "apne", "yeh", "woh", "jo", "toh", "bhi", "sab",
    "dosto", "dosti", "shuru", "zaroor", "sakte", "sakta", "sakti",
}

HINDI_WORD_REPLACEMENTS = {
    "dhanyavad": "shukriya",
    "namaste": "Assalamu Alaikum",
    "namaskar": "Assalamu Alaikum",
    "jaankari": "maloomat",
    "dwara": "zariye",
    "tatha": "aur",
    "vishesh": "khas",
    "prastut": "paish",
    "pramukh": "aham",
    "adhik": "zyada",
}


def _extract_quoted_phrases(text: str) -> list[str]:
    if not text:
        return []
    return re.findall(r'"([^"]{3,150})"', text)


def _is_english_phrase(phrase: str) -> bool:
    phrase = phrase.strip()
    if not phrase or not phrase.isascii():
        return False
    words = re.findall(r"[a-zA-Z']+", phrase.lower())
    if len(words) < 2:
        return False
    if any(w in ROMAN_URDU_MARKERS for w in words):
        return False
    return True


def get_quoted_english_phrase(user_message: str) -> str | None:
    for phrase in _extract_quoted_phrases(user_message or ""):
        if _is_english_phrase(phrase):
            return phrase.strip()
    return None


def with_quoted_title_language_override(prompt: str, quoted_phrase: str) -> str:
    return (
        prompt
        + "\n\n[FINAL OVERRIDE - HIGHEST PRIORITY - OBEY THIS EXACTLY, IT BEATS EVERYTHING ABOVE]\n"
        + f"The user quoted this exact phrase: \"{quoted_phrase}\". This phrase is written in English.\n"
        + "This means the actual content the user wants produced (script, caption, title, post, ad copy, "
        + "whatever they asked for) must be written ENTIRELY in English.\n"
        + "Every part of your output must be in English: any greeting, the intro/hook, every numbered "
        + "section or point, the conclusion, and the call-to-action - all of it, first word to last word.\n"
        + "Do NOT write any Roman Urdu, Urdu script, or Hindi anywhere in this response, even if earlier "
        + "turns in this conversation were in Roman Urdu."
    )


def looks_like_roman_urdu_or_hindi(text: str) -> bool:
    if not text:
        return False
    if any('\u0900' <= ch <= '\u097F' for ch in text):
        return True
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if not words:
        return False
    marker_hits = sum(1 for w in words if w in ROMAN_URDU_MARKERS)
    return marker_hits >= 3


def has_markdown_headings(text: str) -> bool:
    if not text:
        return False
    import re as _re
    return bool(_re.search(r"(?m)^#{1,6}\s+\S", text))


def looks_like_it_needs_headings(text: str) -> bool:
    if not text:
        return False
    word_count = len(text.split())
    paragraph_count = len([p for p in text.split("\n\n") if p.strip()])
    return word_count >= 120 and paragraph_count >= 3


def with_heading_enforcement_override(prompt: str) -> str:
    return (
        prompt
        + "\n\n[FINAL OVERRIDE - HIGHEST PRIORITY - OBEY THIS EXACTLY]\n"
        + "Your previous draft was long/multi-part but used no Markdown headings. Rewrite the ENTIRE "
        + "response from scratch, this time broken into clearly labeled sections using Markdown headings "
        + "(## Heading) for each distinct part, so it is easy to scan."
    )


def sanitize_hindi_words(text: str) -> str:
    if not text:
        return text
    cleaned = text
    for hindi_word, urdu_word in HINDI_WORD_REPLACEMENTS.items():
        cleaned = re.sub(rf"\b{re.escape(hindi_word)}\b", urdu_word, cleaned, flags=re.IGNORECASE)
    return cleaned


def extract_result_text(result: Any) -> str:
    if not isinstance(result, dict):
        return ""
    meta = result.get("metadata")
    if isinstance(meta, dict):
        for key in ("text", "raw_result", "result"):
            val = meta.get(key)
            if isinstance(val, str) and val:
                return val
    for key in ("text", "raw_result", "result"):
        val = result.get(key)
        if isinstance(val, str) and val:
            return val
    return ""


def apply_sanitization_to_result(result: Any) -> Any:
    if not isinstance(result, dict):
        return result
    meta = result.get("metadata")
    if isinstance(meta, dict):
        for key in ("text", "raw_result", "result"):
            val = meta.get(key)
            if isinstance(val, str) and val:
                meta[key] = sanitize_hindi_words(val)
    for key in ("text", "raw_result", "result"):
        val = result.get(key)
        if isinstance(val, str) and val:
            result[key] = sanitize_hindi_words(val)
    return result


_DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")


def has_devanagari(text: str) -> bool:
    return bool(text) and bool(_DEVANAGARI_PATTERN.search(text))


async def _transliterate_devanagari_to_roman_urdu(text: str) -> str:
    """
    Only called when has_devanagari(text) is True - a rare generation
    slip, not the normal path - so this adds no cost or extra
    instructions to the vast majority of responses. Uses the same
    small/fast Groq model already used elsewhere in this codebase for
    script normalization (see transcription_service.py).
    """
    from app.core.config.settings import settings
    if not settings.GROQ_API_KEY:
        return text

    import requests

    system_prompt = (
        "You fix script/spelling ONLY - you never translate or change the "
        "meaning or wording.\n"
        "The text below is mostly Urdu/Roman Urdu but has some words "
        "accidentally written in Devanagari (Hindi script). Rewrite ONLY "
        "those Devanagari words in Roman Urdu (Latin letters) - "
        "transliterate the sounds, do not translate the meaning. Leave "
        "every other word (Urdu script, Roman Urdu, English) exactly as "
        "it is, unchanged.\n"
        "Output ONLY the corrected full text - no explanation, no quotes, "
        "no preamble."
    )
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "temperature": 0,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        fixed = data["choices"][0]["message"]["content"].strip()
        return fixed if fixed else text
    except Exception:
        return text


async def sanitize_language_output(text: str) -> str:
    """
    Final safety net applied to assistant-generated text before it is
    stored or returned to the client: (1) swaps any stray Roman-Hindi
    words for their Urdu equivalents (cheap, no network call), (2) if
    any Devanagari script slipped in, fixes ONLY that via one small
    LLM call. Skips the LLM call entirely when there is nothing to
    fix, so normal responses are not slowed down or given any extra
    instructions - the main generation prompt is untouched.
    """
    if not text:
        return text
    cleaned = sanitize_hindi_words(text)
    if has_devanagari(cleaned):
        cleaned = await _transliterate_devanagari_to_roman_urdu(cleaned)
    return cleaned

