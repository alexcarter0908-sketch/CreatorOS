from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import SessionLocal, get_db
from app.dependencies.auth import get_current_user
from app.repositories.asset_repository import AssetRepository
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.ai_request import AIRequest
from app.core.config.settings import settings
from app.services.agents.prompt_helpers import (
    with_accuracy_instruction,
    with_brand_voice_instruction,
    with_conversation_history,
    with_current_date,
    with_identity_instruction,
    with_language_instruction,
    with_location_context,
    with_structured_answer_instruction,
)
from app.services.agents.search_gate import classify as classify_intent
from app.services.assets.asset_service import AssetService
from app.services.orchestrator.ai_orchestrator import AIOrchestrator
from app.services.providers.implementations.groq.groq_provider import GroqProvider
from app.services.research.web_search import web_search_with_sources

router = APIRouter(
    prefix="/commands",
    tags=["Commands"],
)

orchestrator = AIOrchestrator()

# ==================================================================
# NEW: voice mic transcription (speech-to-text for command input)
# ==================================================================

@router.post("/transcribe")
async def transcribe_command_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    from app.services.speech.transcription_service import (
        TranscriptionError,
        normalize_transcript_script,
        transcribe_audio_bytes,
    )

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio is empty.")

    try:
        text = await asyncio.to_thread(
            transcribe_audio_bytes,
            audio_bytes,
            file.filename or "audio.webm",
        )
    except TranscriptionError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    # Whisper transcribes Urdu speech inconsistently (Urdu script vs Roman
    # Urdu vs a mid-sentence English drift) - normalize the script here so
    # the command input always sees a consistent Roman Urdu / English mix.
    text = await asyncio.to_thread(normalize_transcript_script, text)

    return {"text": text}



class CommandRequest(BaseModel):
    command: str
    project_id: str | None = None
    conversation_id: str | None = None
    history: list[dict[str, str]] = []
    latitude: float | None = None
    longitude: float | None = None


def detect_asset_type(command: str) -> str:
    command = command.lower()

    research_words = [
        "research", "trends", "trending", "latest news",
        "what's happening", "current state of", "market analysis",
    ]
    if any(word in command for word in research_words):
        return "research"

    script_words = ["script"]
    if any(word in command for word in script_words):
        return "script"

    document_words = [
        "word document", "docx", "pdf", "downloadable document",
        "download document", "proposal document", "document",
    ]
    if any(word in command for word in document_words):
        return "document"

    seo_words = ["seo", "meta description", "meta title", "keyword research"]
    if any(word in command for word in seo_words):
        return "seo"

    text_words = [
        "caption", "blog", "article",
        "post", "description", "title", "hashtag",
    ]
    if any(word in command for word in text_words):
        return "text"

    image_words = [
        "thumbnail", "image", "logo", "poster",
        "banner", "photo", "picture",
    ]
    if any(word in command for word in image_words):
        return "image"

    video_words = ["video", "reel", "animation"]
    if any(word in command for word in video_words):
        return "video"

    audio_words = ["voice", "speech", "audio", "tts", "text to speech"]
    if any(word in command for word in audio_words):
        return "audio"

    return "text"


def _wants_full_pipeline(command: str) -> bool:
    """
    A "video ... for my YouTube channel" style command should trigger
    the full script -> thumbnail -> video -> SEO pipeline instead of
    a single video generation.
    """
    lowered = command.lower()
    has_video = "video" in lowered
    has_publish_intent = any(
        w in lowered for w in ("youtube", "channel", "publish", "upload")
    )
    return has_video and has_publish_intent


def _load_history(db: Session, conversation_id: str, limit: int = 12) -> list[dict[str, str]]:
    """
    Pull recent turns from the DB so memory survives refreshes/devices.
    IMPORTANT: call this BEFORE adding the new user message for the
    current turn, otherwise the current message ends up duplicated.
    """
    convo = ConversationRepository(db).get_by_id(conversation_id)
    if convo is None:
        return []
    turns = [
        {"role": m.role, "content": m.content}
        for m in convo.messages
        if m.status == "completed" and m.content.strip()
    ]
    return turns[-limit:]


async def _run_pipeline_in_background(workflow_id: str, conversation_id: str) -> None:
    """
    Runs every step of an already-created workflow, then posts a
    summary message (the script text, plus any step failures) back
    into the conversation so the user sees a result even though this
    runs after the original HTTP request already returned.
    """
    db = SessionLocal()
    try:
        from app.services.workflows.workflow_service import WorkflowService

        service = WorkflowService(db)
        workflow = service.repo.get_by_id(workflow_id)
        if workflow is None:
            return

        workflow = await service.run(workflow_id, owner_id=workflow.owner_id)

        summary = ""
        text_step = next(
            (s for s in workflow.steps if s.asset_type == "text" and s.asset_id),
            None,
        )
        if text_step:
            asset = AssetRepository(db).get_by_id(text_step.asset_id)
            if asset and asset.extra_metadata:
                summary = asset.extra_metadata.get("text", "") or ""

        failed = [s for s in workflow.steps if s.status == "failed"]
        if failed:
            failure_lines = "\n".join(
                f"- {s.asset_type} step failed: {s.error_message}" for s in failed
            )
            summary = f"{summary}\n\n{failure_lines}".strip()

        ConversationRepository(db).add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=summary or "Pipeline complete.",
            status="failed" if workflow.status == "failed" else "completed",
        )
    except Exception:
        pass
    finally:
        db.close()


# ==================================================================
# EXISTING: buffered command endpoint
# ==================================================================

@router.post("/run")
async def run_command(
    request: CommandRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convo_repo = ConversationRepository(db)

    conversation = None
    if request.conversation_id:
        conversation = convo_repo.get_by_id(request.conversation_id)
        if conversation is None or conversation.owner_id != current_user.id:
            conversation = None

    if conversation is None:
        conversation = convo_repo.create(
            owner_id=current_user.id,
            title=request.command[:60],
            project_id=request.project_id,
        )

    history = _load_history(db, conversation.id) or request.history

    convo_repo.add_message(
        conversation_id=conversation.id,
        role="user",
        content=request.command,
    )

    intent = await classify_intent(request.command, history)
    asset_type = intent.get("asset_type") or detect_asset_type(request.command)
    _seo_override_words = ("seo title", "seo tags", "meta description", "meta title", "seo description", " seo ")
    _lowered_command = " " + request.command.lower() + " "
    if any(w in _lowered_command for w in _seo_override_words):
        asset_type = "seo"

    if asset_type == "video" and _wants_full_pipeline(request.command):
        from app.services.orchestrator.full_pipeline import PIPELINE_STEPS
        from app.services.workflows.workflow_service import WorkflowService

        service = WorkflowService(db)
        steps = [
            {"asset_type": at, "prompt": tpl.replace("{prompt}", request.command)}
            for at, tpl in PIPELINE_STEPS
        ]
        workflow = service.create(
            owner_id=current_user.id,
            name=f"Chat: {request.command[:50]}",
            steps=steps,
            project_id=request.project_id,
        )

        asyncio.create_task(
            _run_pipeline_in_background(
                workflow_id=workflow.id,
                conversation_id=conversation.id,
            )
        )

        return {
            "workflow_id": workflow.id,
            "status": "running",
            "conversation_id": conversation.id,
            "asset_id": None,
            "text": "",
        }

    from app.services.billing import credit_service
    from app.core.pricing.pricing_service import is_paid, is_limited_free, credits_for_generation
    from app.core.pricing.pricing_config import LIMITED_FREE_ASSET_TYPES

    _billing_user_id = current_user.id
    _billing_charged_credits = 0

    if is_paid(asset_type):
        _billing_charged_credits = credits_for_generation(asset_type)
        try:
            credit_service.deduct_credits(
                db, _billing_user_id, _billing_charged_credits,
                description=f"{asset_type} generation",
            )
        except credit_service.InsufficientCreditsError:
            raise HTTPException(status_code=402, detail="Insufficient credits. Please buy more credits.")
    elif is_limited_free(asset_type):
        covered = credit_service.try_consume_free_quota(db, _billing_user_id, asset_type)
        if not covered:
            _billing_charged_credits = LIMITED_FREE_ASSET_TYPES[asset_type]["credit_cost_after_quota"]
            try:
                credit_service.deduct_credits(
                    db, _billing_user_id, _billing_charged_credits,
                    description=f"{asset_type} generation (free quota used)",
                )
            except credit_service.InsufficientCreditsError:
                raise HTTPException(status_code=402, detail="Insufficient credits. Please buy more credits.")

    _brand_voice = None
    if request.project_id:
        from app.repositories.project_repository import ProjectRepository
        _project = ProjectRepository(db).get_by_id(request.project_id)
        if _project is not None:
            _brand_voice = _project.brand_voice

    ai_request = AIRequest(
        prompt=request.command,
        asset_type=asset_type,
        project_id=request.project_id,
        owner_id=current_user.id,
        history=history,
        latitude=request.latitude,
        longitude=request.longitude,
        brand_voice=_brand_voice,
        conversation_id=conversation.id,
        metadata={"raw_user_message": request.command},
    )
    asset_service = AssetService(db)
    asset = asset_service.start(
        owner_id=current_user.id,
        asset_type=asset_type,
        provider="auto",
        model_id="auto",
        prompt=request.command,
        project_id=request.project_id,
    )

    try:
        result = await orchestrator.execute(ai_request)
        asset = asset_service.complete_from_provider_result(asset, result)
        result["asset_id"] = asset.id
        result["conversation_id"] = conversation.id

        reply_text = ""
        meta = asset.extra_metadata or {}
        if isinstance(meta.get("text"), str) and meta.get("text"):
            reply_text = meta["text"]
        elif isinstance(meta.get("raw_result"), str) and meta.get("raw_result"):
            reply_text = meta["raw_result"]
        elif isinstance(meta.get("result"), str) and meta.get("result"):
            reply_text = meta["result"]

        if reply_text:
            from app.services.agents.prompt_helpers import sanitize_language_output
            reply_text = await sanitize_language_output(reply_text)
            if isinstance(result, dict) and isinstance(result.get("text"), str) and result.get("text"):
                result["text"] = reply_text

        message_metadata = {"sources": meta["sources"]} if meta.get("sources") else None

        convo_repo.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply_text,
            status="completed" if asset.status != "failed" else "failed",
            asset_id=asset.id,
            error_message=asset.error_message,
            extra_metadata=message_metadata,
        )

        return result

    except RuntimeError as e:
        asset_service.fail(asset, error_message=str(e))
        if _billing_charged_credits:
            credit_service.refund_credits(db, _billing_user_id, _billing_charged_credits, description=f"refund: {asset_type} generation failed")
        convo_repo.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content="",
            status="failed",
            error_message=str(e),
        )
        raise HTTPException(status_code=503, detail=str(e)) from e

    except Exception as e:
        asset_service.fail(asset, error_message=str(e))
        if _billing_charged_credits:
            credit_service.refund_credits(db, _billing_user_id, _billing_charged_credits, description=f"refund: {asset_type} generation failed")
        convo_repo.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content="",
            status="failed",
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e)) from e


# ==================================================================
# NEW: streaming command endpoint (SSE)
# ==================================================================

@router.post("/run/stream")
async def run_command_stream(
    request: CommandRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
):
    owner_id = current_user.id

    async def event_generator():
        db = SessionLocal()
        try:
            convo_repo = ConversationRepository(db)

            conversation = None
            if request.conversation_id:
                conversation = convo_repo.get_by_id(request.conversation_id)
                if conversation is None or conversation.owner_id != owner_id:
                    conversation = None

            if conversation is None:
                conversation = convo_repo.create(
                    owner_id=owner_id,
                    title=request.command[:60],
                    project_id=request.project_id,
                )

            history = _load_history(db, conversation.id) or request.history

            convo_repo.add_message(
                conversation_id=conversation.id,
                role="user",
                content=request.command,
            )

            intent = await classify_intent(request.command, history)
            asset_type = intent.get("asset_type") or detect_asset_type(request.command)
            _seo_override_words = ("seo title", "seo tags", "meta description", "meta title", "seo description", " seo ")
            _lowered_command = " " + request.command.lower() + " "
            if any(w in _lowered_command for w in _seo_override_words):
                asset_type = "seo"

            from app.services.billing import credit_service
            from app.core.pricing.pricing_service import is_paid, is_limited_free, credits_for_generation
            from app.core.pricing.pricing_config import LIMITED_FREE_ASSET_TYPES

            _billing_user_id = owner_id
            _billing_charged_credits = 0

            if is_paid(asset_type):
                _billing_charged_credits = credits_for_generation(asset_type)
                try:
                    credit_service.deduct_credits(
                        db, _billing_user_id, _billing_charged_credits,
                        description=f"{asset_type} generation",
                    )
                except credit_service.InsufficientCreditsError:
                    yield f"event: error\ndata: {json.dumps({'detail': 'Insufficient credits. Please buy more credits.'})}\n\n"
                    return
            elif is_limited_free(asset_type):
                covered = credit_service.try_consume_free_quota(db, _billing_user_id, asset_type)
                if not covered:
                    _billing_charged_credits = LIMITED_FREE_ASSET_TYPES[asset_type]["credit_cost_after_quota"]
                    try:
                        credit_service.deduct_credits(
                            db, _billing_user_id, _billing_charged_credits,
                            description=f"{asset_type} generation (free quota used)",
                        )
                    except credit_service.InsufficientCreditsError:
                        yield f"event: error\ndata: {json.dumps({'detail': 'Insufficient credits. Please buy more credits.'})}\n\n"
                        return

            # ------------------------------------------------------
            # Non-text (excluding "script", which reuses the reliable
            # text/chat streaming branch below so it keeps search and
            # conversation history): run normally, single "done" event.
            # ------------------------------------------------------
            if asset_type not in ("text", "script"):
                ai_request = AIRequest(
                    prompt=request.command,
                    asset_type=asset_type,
                    project_id=request.project_id,
                    owner_id=owner_id,
                    history=history,
                    metadata={"raw_user_message": request.command},
                )
                asset_service = AssetService(db)
                asset = asset_service.start(
                    owner_id=owner_id,
                    asset_type=asset_type,
                    provider="auto",
                    model_id="auto",
                    prompt=request.command,
                    project_id=request.project_id,
                )
                try:
                    result = await orchestrator.execute(ai_request)
                    asset = asset_service.complete_from_provider_result(asset, result)
                    meta = asset.extra_metadata or {}
                    text = meta.get("text", "") if isinstance(meta.get("text"), str) else ""
                    if text:
                        from app.services.agents.prompt_helpers import sanitize_language_output
                        text = await sanitize_language_output(text)

                    message_metadata = {"sources": meta["sources"]} if meta.get("sources") else None

                    convo_repo.add_message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content=text,
                        status="completed" if asset.status != "failed" else "failed",
                        asset_id=asset.id,
                        error_message=asset.error_message,
                        extra_metadata=message_metadata,
                    )

                    payload = {
                        "asset_id": asset.id,
                        "conversation_id": conversation.id,
                        "status": asset.status,
                    }
                    yield f"event: done\ndata: {json.dumps(payload)}\n\n"

                except Exception as e:
                    asset_service.fail(asset, error_message=str(e))
                    if _billing_charged_credits:
                        credit_service.refund_credits(db, _billing_user_id, _billing_charged_credits, description=f"refund: {asset_type} generation failed")
                    convo_repo.add_message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content="",
                        status="failed",
                        error_message=str(e),
                    )
                    yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"
                return

            # ------------------------------------------------------
            # Text/chat: stream token-by-token via Groq.
            # ------------------------------------------------------
            use_search = intent.get("needs_search", False)
            deep = intent.get("deep_search", False)

            # Short follow-ups often chain ("bricks empire..." ->
            # "details do" -> "location btao") - use the last few
            # user turns, not just the immediately previous one, so
            # the search query keeps the original topic.
            search_query = request.command
            if use_search and len(request.command.split()) <= 8 and history:
                last_user_turns = [h.get("content", "") for h in history if h.get("role") == "user"]
                context_turns = last_user_turns[-3:]
                if context_turns:
                    search_query = " ".join(context_turns) + " " + request.command

            sources: list[dict] = []
            search_context = ""
            if use_search:
                search_context, sources = web_search_with_sources(
                    search_query,
                    max_results=6 if deep else 4,
                    deep=deep,
                    lat=request.latitude,
                    lng=request.longitude,
                )

            knowledge_context = ""
            try:
                from app.services.knowledge.knowledge_service import KnowledgeService
                kb = KnowledgeService(db)
                chunks = kb.retrieve_context(
                    owner_id=owner_id,
                    query=request.command,
                    project_id=request.project_id,
                )
                if chunks:
                    excerpts = "\n\n".join(
                        f"[Excerpt {i + 1}]\n{c.content}" for i, c in enumerate(chunks)
                    )
                    knowledge_context = (
                        "The following excerpts are from the user's own uploaded "
                        "documents (knowledge base) and are likely relevant:\n\n"
                        f"{excerpts}\n\n"
                    )
            except Exception:
                knowledge_context = ""

            chat_prompt = f"{knowledge_context}{search_context}\n\nUser message:\n\n{request.command}\n"
            if asset_type == "script":
                # This streaming shortcut skips ScriptAgent entirely (see
                # comment above), which previously meant scripts silently
                # lost the mandatory Roman Urdu + scene-format rules and
                # came out as plain English with no structure. Re-apply
                # the same non-negotiable rules here so behavior stays
                # consistent regardless of which code path handles it.
                chat_prompt = (
                    chat_prompt
                    + "\n\n[SCRIPT RULES - MANDATORY]\n"
                    + "You are writing a short-form video script (reel/ad/YouTube Short). "
                    + "You MUST write in Roman Urdu mixed with English (not Hindi, not pure "
                    + "Urdu script) unless the user explicitly asked for English. Use clear "
                    + "markdown scene headings for every scene, e.g. '### SCENE 1 - HOOK "
                    + "(0:00-0:05s)', each with a Visual line, a VO line (the spoken line in "
                    + "quotes), and an On-screen text line. End with a strong Call To Action. "
                    + "Scale the number of scenes to the requested duration (default 45-60s).\n"
                    + "Begin the script directly - do not restate, repeat, or quote back the "
                    + "user's own instruction/request as if it were part of the script."
                )
            full_prompt = with_conversation_history(chat_prompt, history)
            full_prompt = with_language_instruction(full_prompt)
            full_prompt = with_identity_instruction(
                full_prompt,
                (settings.APP_NAME or "CreatorOS").replace(" API", "").strip() or "CreatorOS",
            )
            full_prompt = with_current_date(full_prompt)
            full_prompt = (
                full_prompt
                + "\n\n[FORMATTING RULE]\n"
                + "1. Structure every response like a professional writer, not a casual paragraph dump.\n"
                + "2. Use clear headings (## Heading) to break the response into labeled sections whenever "
                + "the answer has more than one distinct part (e.g. identity + features + limitations).\n"
                + "3. Use bullet points or numbered lists for multiple items, steps, or tips.\n"
                + "4. Highlight important tips, warnings, or key takeaways using a blockquote (> Note: ...).\n"
                + "5. Keep paragraphs short and scannable - avoid long unbroken text blocks.\n"
                + "6. Maintain this structure regardless of the language/script used (Roman Urdu, English, or mixed).\n"
                + "7. Short one-line replies (a greeting, a yes/no, a single fact) do NOT need headings - only "
                + "use headings when the content genuinely has multiple sections."
            )
            full_prompt = (
                full_prompt
                + "\n\n[RESPONSE QUALITY RULE]\n"
                + "1. Answer the user's actual question directly first - do not dodge it with generic questions.\n"
                + "2. Never repeat a question or point you already made earlier in this conversation - check "
                + "history first.\n"
                + "3. Do not give generic/templated content unless you know it matches the user's actual "
                + "project or request.\n"
                + "4. NEVER restate the same point under multiple headings - each section must add NEW "
                + "information only."
            )
            full_prompt = (
                full_prompt
                + "\n\n[VOCABULARY RULE - ROMAN URDU ONLY]\n"
                + "When replying in Roman Urdu, use everyday SPOKEN Urdu vocabulary - the words an ordinary "
                + "person in Pakistan actually says out loud - NOT literary/Sanskrit-derived formal Hindi "
                + "vocabulary, even if that vocabulary is technically valid. This is a general PRINCIPLE, "
                + "apply it to every word choice, not just the examples below:\n"
                + "'jaankari'->'maloomat', 'dwara'->'zariye/se', 'samay'->'waqt', 'sambandh'->'talluq/rishta', "
                + "'vriddhi'->'izafa/barhotri', 'prakaar'->'tarah/qisam', 'surakshit'->'mehfooz', "
                + "'vishesh'->'khaas', 'pramukh'->'aham', 'prastut'->'paish', 'adhik'->'zyada'.\n"
                + "Test for every sentence: would a Pakistani street vendor, rickshaw driver, or someone "
                + "texting on WhatsApp actually say this word? If it sounds like a Hindi TV news anchor or "
                + "a Sanskrit textbook, replace it with the everyday Urdu equivalent."
            )
            full_prompt = (
                full_prompt
                + "\n\n[QUESTION UNDERSTANDING RULE]\n"
                + "Before answering, silently identify what KIND of message this is, and match your "
                + "response shape to it - do not use the same heavy structure for every message:\n"
                + "- Identity/features question -> answer using the IDENTITY RULE above.\n"
                + "- Quick factual question (one fact, a number, a yes/no) -> answer in 1-3 sentences, "
                + "no headings needed.\n"
                + "- How-to / step-by-step request -> use a numbered list of concrete steps.\n"
                + "- Creative request (write a script/caption/idea/post) -> give the actual content "
                + "directly first, do not lecture about how you will write it before writing it.\n"
                + "- Vague or ambiguous request -> give your best-guess answer using the most reasonable "
                + "interpretation, THEN ask at most one specific clarifying question at the end - never "
                + "reply with only a clarifying question and no attempt at an answer.\n"
                + "- Follow-up message that references something already said earlier in this "
                + "conversation -> use that history, do not ask the user to repeat information they "
                + "already gave, and do not repeat a point/answer you already gave earlier.\n"
                + "- Casual greeting or small talk -> reply briefly and naturally, no headings, no "
                + "feature list, no lecture.\n"
                + "The goal: the response shape should always fit what was actually asked, not follow "
                + "one fixed template for every message."
            )
            if request.project_id:
                from app.repositories.project_repository import ProjectRepository
                _project = ProjectRepository(db).get_by_id(request.project_id)
                if _project is not None:
                    full_prompt = with_brand_voice_instruction(full_prompt, _project.brand_voice)
            full_prompt = with_location_context(full_prompt, request.latitude, request.longitude)
            if use_search or knowledge_context:
                full_prompt = with_accuracy_instruction(full_prompt)
                full_prompt = with_structured_answer_instruction(full_prompt)

            asset_service = AssetService(db)
            asset = asset_service.start(
                owner_id=owner_id,
                asset_type=asset_type,
                provider="groq",
                model_id="llama-4-scout",
                prompt=request.command,
                project_id=request.project_id,
            )

            collected = ""
            stream_failed = False
            client_stopped = False

            try:
                groq = GroqProvider()
                async for delta in groq.stream_chat(
                    model="llama-3.3-70b-versatile",
                    prompt=full_prompt,
                ):
                    collected += delta
                    yield f"event: token\ndata: {json.dumps({'text': delta})}\n\n"
                    # The user may have clicked Stop - no point paying for
                    # more provider tokens once nobody's listening.
                    if await http_request.is_disconnected():
                        client_stopped = True
                        break
            except Exception:
                stream_failed = True

            if stream_failed or not collected:
                try:
                    ai_request = AIRequest(
                        prompt=request.command,
                        asset_type="text",
                        project_id=request.project_id,
                        owner_id=owner_id,
                        history=history,
                        metadata={"raw_user_message": request.command},
                    )
                    result = await orchestrator.execute(ai_request)
                    asset = asset_service.complete_from_provider_result(asset, result)
                    meta = asset.extra_metadata or {}
                    collected = meta.get("text", "") if isinstance(meta.get("text"), str) else ""
                    if collected:
                        from app.services.agents.prompt_helpers import sanitize_language_output
                        collected = await sanitize_language_output(collected)
                    if isinstance(meta.get("sources"), list):
                        sources = meta["sources"]
                    yield f"event: token\ndata: {json.dumps({'text': collected})}\n\n"
                except Exception as e:
                    asset_service.fail(asset, error_message=str(e))
                    if _billing_charged_credits:
                        credit_service.refund_credits(db, _billing_user_id, _billing_charged_credits, description=f"refund: {asset_type} generation failed")
                    convo_repo.add_message(
                        conversation_id=conversation.id,
                        role="assistant",
                        content="",
                        status="failed",
                        error_message=str(e),
                    )
                    yield f"event: error\ndata: {json.dumps({'detail': str(e)})}\n\n"
                    return
            else:
                from app.services.agents.prompt_helpers import sanitize_language_output
                collected = await sanitize_language_output(collected)
                extra_metadata = {"text": collected}
                if sources:
                    extra_metadata["sources"] = sources
                asset_service.mark_completed(
                    asset,
                    file_url="",
                    storage_path="",
                    extra_metadata=extra_metadata,
                    provider="groq",
                    model_id="llama-4-scout",
                )

            message_metadata = {"sources": sources} if sources else None

            convo_repo.add_message(
                conversation_id=conversation.id,
                role="assistant",
                content=collected,
                status="completed",
                asset_id=asset.id,
                extra_metadata=message_metadata,
            )

            payload = {
                "asset_id": asset.id,
                "conversation_id": conversation.id,
                "status": "completed",
            }
            yield f"event: done\ndata: {json.dumps(payload)}\n\n"

        finally:
            db.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )



