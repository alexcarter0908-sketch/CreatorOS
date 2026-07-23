from __future__ import annotations
from abc import ABC, abstractmethod
from app.schemas.ai_request import AIRequest
from app.core.config.settings import settings
from app.services.agents.prompt_helpers import (
    with_accuracy_instruction,
    with_brand_voice_instruction,
    with_conversation_history,
    with_identity_instruction,
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
        raw_user_message = request.prompt
        quoted_english_phrase = get_quoted_english_phrase(raw_user_message)

        app_name = (settings.APP_NAME or "CreatorOS").replace(" API", "").strip() or "CreatorOS"

        prompt = with_conversation_history(request.prompt, request.history)
        prompt = with_identity_instruction(prompt, app_name)
        prompt = with_language_instruction(prompt)
        prompt = with_location_context(prompt, request.latitude, request.longitude)
        prompt = with_brand_voice_instruction(prompt, request.brand_voice)
        if not skip_accuracy_instruction:
            prompt = with_accuracy_instruction(prompt)
            prompt = with_structured_answer_instruction(prompt)

        prompt = (
            prompt
            + "1. Reply naturally in the user's language/script (Roman Urdu stays Roman Urdu).\n"
            + "2. FOR ROMAN URDU: use everyday SPOKEN Urdu vocabulary - the words an ordinary person in "
            + "Pakistan actually says out loud - NOT literary/Sanskrit-derived formal Hindi vocabulary, even "
            + "if technically valid. This is a general PRINCIPLE, apply it to every word choice:\n"
            + "'jaankari'->'maloomat', 'dwara'->'zariye/se', 'samay'->'waqt', 'sambandh'->'talluq/rishta', "
            + "'vriddhi'->'izafa/barhotri', 'prakaar'->'tarah/qisam', 'surakshit'->'mehfooz', "
            + "'vishesh'->'khaas', 'pramukh'->'aham', 'prastut'->'paish', 'adhik'->'zyada'.\n"
            + "Test for every sentence: would a Pakistani street vendor or someone texting on WhatsApp "
            + "actually say this word? If it sounds like a Hindi TV news anchor or a Sanskrit textbook, "
            + "replace it with the everyday Urdu equivalent.\n"
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
            + "\n\n[DEPTH AND SPECIFICITY RULE - CRITICAL]\n"
            + "This response may become a real deliverable (a document, a script, a plan someone actually "
            + "acts on) - generic filler is a failure, not just a style issue.\n"
            + "1. NEVER use vague placeholder phrasing like 'using AI and machine learning', 'APIs can be "
            + "integrated', 'cost can vary depending on complexity' - these say nothing. Instead name the "
            + "ACTUAL thing: which specific API/library/service, which specific database, which specific "
            + "number and why.\n"
            + "2. For any system/product/business design request: give concrete modules with their actual "
            + "data fields (not just module names), name real tools/technologies to build each part, and "
            + "describe the actual step-by-step flow of data through the system.\n"
            + "3. For any cost/time estimate: break it into its actual components (e.g. developer cost, "
            + "which paid API and its per-message/per-call price, hosting) - a single vague range with no "
            + "breakdown is not acceptable.\n"
            + "4. Do NOT end with a 'Conclusion' or summary section that just restates the intro in "
            + "different words - either add genuinely new information (concrete next steps, risks, what "
            + "to decide first) or omit the closing section entirely.\n"
            + "5. If a critical detail is unknown (e.g. their current tools, budget, scale) and it would "
            + "meaningfully change the recommendation, ask ONE specific question about it rather than "
            + "silently picking a generic answer that ignores it.\n"
            + "6. Write like a senior consultant who will be held accountable for this advice actually "
            + "working - not like a marketing blog post skimming the surface of a topic."
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


