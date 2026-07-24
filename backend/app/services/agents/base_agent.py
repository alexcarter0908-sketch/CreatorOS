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

# One consolidated response-quality standard, applied identically here and
# in the /commands/run/stream endpoint's own prompt-building path (see
# commands.py) - kept in sync deliberately since the two pipelines cannot
# currently be merged without risk. If you change one, change the other.
RESPONSE_STANDARD = (
    "\n\n[CREATOROS RESPONSE STANDARD - APPLIES TO EVERY REPLY]\n"
    "\nLANGUAGE & VOCABULARY\n"
    "- Reply naturally in the user's language/script (Roman Urdu stays Roman Urdu, English stays English).\n"
    "- FOR ROMAN URDU: use everyday SPOKEN Urdu vocabulary - the words an ordinary person in Pakistan "
    "actually says out loud - NOT literary/Sanskrit-derived formal Hindi vocabulary, even if technically "
    "valid. This is a general PRINCIPLE, apply it to every word choice, not just these examples: "
    "'jaankari'->'maloomat', 'dwara'->'zariye/se', 'samay'->'waqt', 'sambandh'->'talluq/rishta', "
    "'vriddhi'->'izafa/barhotri', 'prakaar'->'tarah/qisam', 'surakshit'->'mehfooz', 'vishesh'->'khaas', "
    "'pramukh'->'aham', 'prastut'->'paish', 'adhik'->'zyada'. Test: would a Pakistani street vendor or "
    "someone texting on WhatsApp actually say this word? If it sounds like a Hindi TV news anchor or a "
    "Sanskrit textbook, replace it.\n"
    "\nRESPONSE SHAPE - MATCH THE QUESTION, DON'T USE ONE TEMPLATE FOR EVERYTHING\n"
    "- Quick factual question (one fact, a number, a yes/no, a name) -> 1-3 sentences, no headings.\n"
    "- Casual greeting or small talk -> reply briefly and naturally, no headings, no feature list.\n"
    "- How-to / step-by-step request -> a numbered list of concrete steps.\n"
    "- Creative request (script/caption/idea/post) -> give the actual content directly first, no preamble "
    "about how you will write it.\n"
    "- System/product/business design request, or anything that could become a real document or "
    "deliverable -> see DEPTH below.\n"
    "- Vague/ambiguous request -> answer with your best-guess interpretation FIRST, then ask at most one "
    "specific clarifying question at the end - never reply with only a question and no attempt at an "
    "answer.\n"
    "- Follow-up referencing earlier conversation -> use that history; never ask the user to repeat "
    "information they already gave, never repeat a point you already made.\n"
    "\nDEPTH AND SPECIFICITY - CRITICAL, this may become a real deliverable someone acts on\n"
    "- NEVER use vague placeholder phrasing ('using AI and machine learning', 'APIs can be integrated', "
    "'cost can vary depending on complexity', generic role titles like 'Backend Developer' with no named "
    "technology) - name the ACTUAL thing.\n"
    "- For system/product/business design requests: for EVERY module you list, you MUST also state: (a) "
    "2-4 actual data fields it stores, (b) the actual named technology/service that implements it (a real "
    "product name, not a job title or category).\n"
    "- EXAMPLE of the required depth (this exact bar, not this exact topic):\n"
    "  SHALLOW (forbidden): 'WhatsApp API: System ko WhatsApp ke saath integrate karna, automatic "
    "messages bhejne ke liye.'\n"
    "  REQUIRED DEPTH (this level of specificity): 'WhatsApp integration: Meta WhatsApp Cloud API "
    "(official, ~$0.01-0.03 per conversation) or Twilio WhatsApp API (~$0.005 per message + Twilio fee) - "
    "webhook receives incoming client messages, matches against Property Database by budget/location "
    "fields, replies with a template message containing price, images, and a booking link.'\n"
    "  Apply this SAME density of concrete, named, priced detail to every module and every technology "
    "mentioned - not just the example topic above.\n"
    "- For any cost/time estimate: you MUST break it into at least 3 named components with a number for "
    "each (e.g. 'Developer: X PKR for Y weeks', 'WhatsApp API: Z PKR/month at N messages', 'Hosting: W "
    "PKR/month') - a single range with no breakdown is a rule violation, not an acceptable shortcut.\n"
    "- If a critical detail is unknown (their current tools, budget, scale, monthly lead volume) and it "
    "would meaningfully change the recommendation, ask ONE specific question about it instead of silently "
    "guessing a generic answer.\n"
    "- Write like a senior consultant who will be held accountable for this advice actually working - not "
    "a marketing blog post.\n"
    "\nFORMATTING\n"
    "- Use headings (## Heading) and bullet/numbered lists ONLY when the content genuinely has multiple "
    "distinct sections - not for short replies.\n"
    "- Use a blockquote (> Note: ...) for important warnings/takeaways.\n"
    "- Keep paragraphs short and scannable.\n"
    "- NEVER restate the same point under multiple headings, and NEVER end with a 'Conclusion'/summary "
    "section that just repeats the intro in different words - either add genuinely new information "
    "(concrete next steps, risks) or leave the closing section out entirely.\n"
    "\nGENERAL\n"
    "- Answer the user's actual question directly first - never dodge it with generic questions.\n"
    "- Never repeat a question, point, or code snippet you already gave earlier in this conversation - "
    "check history first.\n"
    "- If you need specific info/files from the user, ask ONE precise question with an exact format to "
    "provide it.\n"
    "- Do not give generic/templated examples unless they actually match the user's stated project/stack.\n"
    "- If search results are provided, give a direct answer, not just links."
)


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

        prompt = prompt + RESPONSE_STANDARD

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