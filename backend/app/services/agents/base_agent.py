from __future__ import annotations
from abc import ABC, abstractmethod
from app.schemas.ai_request import AIRequest
from app.services.agents.prompt_helpers import (
    with_accuracy_instruction,
    with_brand_voice_instruction,
    with_conversation_history,
    with_language_instruction,
    with_location_context,
    with_structured_answer_instruction,
    get_quoted_english_phrase,
    with_quoted_title_language_override,
    looks_like_roman_urdu_or_hindi,
    has_markdown_headings,
    looks_like_it_needs_headings,
    with_heading_enforcement_override,
    extract_result_text,
    apply_sanitization_to_result,
)
from app.services.assets.asset_intelligence import AssetIntelligence

class BaseAgent(ABC):
    def __init__(self):
        self.ai = AssetIntelligence()

    @abstractmethod
    async def execute(self, request: AIRequest) -> dict:
        raise NotImplementedError

    async def generate(self, request: AIRequest, skip_accuracy_instruction: bool = False) -> dict:
        # IMPORTANT: use the *original* human message for quote-detection,
        # not request.prompt - by the time some agents (e.g. ScriptAgent)
        # call generate(), request.prompt has already been overwritten
        # with a big system-prompt template that itself contains quoted
        # English example text (e.g. "exact voiceover line(s) in Roman
        # Urdu + English mix"). Scanning that template instead of the
        # real user message caused the whole response to be wrongly
        # force-switched to English. request.metadata["raw_user_message"]
        # is set once, before any agent touches request.prompt.
        raw_user_message = request.metadata.get("raw_user_message") or request.prompt
        quoted_english_phrase = get_quoted_english_phrase(raw_user_message)

        prompt = with_conversation_history(request.prompt, request.history)
        prompt = with_language_instruction(prompt)
        prompt = with_location_context(prompt, request.latitude, request.longitude)
        prompt = with_brand_voice_instruction(prompt, request.brand_voice)
        if not skip_accuracy_instruction:
            prompt = with_accuracy_instruction(prompt)
            prompt = with_structured_answer_instruction(prompt)

        prompt = (
            prompt
            + "1. Reply naturally in the user's language/script (Roman Urdu stays Roman Urdu).\n"
            + "2. FOR ROMAN URDU: You MUST avoid formal Hindi vocabulary. \n"
            + "   - NEVER use: 'jaankari', 'dwara', 'tatha', 'vishesh', 'prastut', 'pramukh', 'samay', 'adhik'.\n"
            + "   - ALWAYS use: 'maloomat', 'zariye', 'aur', 'khas', 'paish', 'aham', 'waqt', 'zyada'.\n"
            + "3. Talk like a professional content creator, not a formal textbook.\n"
            + "4. If search results are provided, give a direct answer, not just links."
        )
        prompt = (
            prompt
            + "\n\n[RESPONSE QUALITY RULE]\n"
            + "1. Answer the user's actual question directly first - do not dodge it with generic questions.\n"
            + "2. Never repeat a question or code snippet you already gave earlier in this conversation - check history first.\n"
            + "3. If you need specific info/files from the user, ask ONE precise question and give an exact command or format to provide it - never vague options like 'paste it or send a link'.\n"
            + "4. Do not give generic/templated examples (like plain HTML/JS code) unless you know that matches the user's actual project or stack.\n"
            + "5. If the user already told you relevant context (project name, stack, files available), use it - do not ask for it again.\n"
            + "6. NEVER restate the same point, question, or request under multiple headings (e.g. do not ask for the same info in a 'Data Collection' section and then again in 'Next Steps' and again in 'Conclusion'). Each section must add NEW information only. If you have one clarifying question, ask it ONCE near the top, then stop - do not pad the response with a summary section that just repeats it."
        )
        prompt = (
            prompt
            + "\n\n[FORMATTING RULE]\n"
            + "1. Structure every response like a professional writer, not a casual paragraph dump.\n"
            + "2. Use clear headings (## Heading) to break the response into labeled sections.\n"
            + "3. Use bullet points or numbered lists for multiple items, steps, or tips.\n"
            + "4. Highlight important tips, warnings, or key takeaways using a blockquote (> Note: ...).\n"
            + "5. Keep paragraphs short and scannable - avoid long unbroken text blocks.\n"
            + "6. Maintain this professional structure regardless of the language/script used (Roman Urdu, English, or mixed)."
        )

        if quoted_english_phrase:
            prompt = with_quoted_title_language_override(prompt, quoted_english_phrase)

        request.prompt = prompt
        result = await self.ai.generate(request)

        if quoted_english_phrase:
            current_text = extract_result_text(result)
            if current_text and looks_like_roman_urdu_or_hindi(current_text):
                request.prompt = (
                    prompt
                    + "\n\n[MANDATORY CORRECTION - YOUR PREVIOUS DRAFT FAILED THIS RULE]\n"
                    + f"Your previous draft still contained Roman Urdu/Hindi text even though the quoted "
                    + f"topic \"{quoted_english_phrase}\" is in English. Rewrite the ENTIRE response from "
                    + "scratch, 100% in English, with absolutely no Roman Urdu or Hindi words anywhere."
                )
                retried_result = await self.ai.generate(request)
                retried_text = extract_result_text(retried_result)
                if retried_text:
                    result = retried_result

        current_text = extract_result_text(result)
        if current_text and looks_like_it_needs_headings(current_text) and not has_markdown_headings(current_text):
            request.prompt = with_heading_enforcement_override(prompt)
            retried_result = await self.ai.generate(request)
            retried_text = extract_result_text(retried_result)
            if retried_text and has_markdown_headings(retried_text):
                result = retried_result

        result = apply_sanitization_to_result(result)
        return result

    async def health_check(self) -> bool:
        try:
            await self.ai.health_report()
            return True
        except Exception:
            return False