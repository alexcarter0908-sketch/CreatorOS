from __future__ import annotations

import base64

from app.schemas.ai_request import AIRequest
from app.services.agents.base_agent import BaseAgent

# Common language name variants (English, Roman Urdu, native spellings) ->
# ElevenLabs ISO language codes. Extend this list as new languages are needed.
_LANGUAGE_ALIASES: dict[str, str] = {
    "urdu": "ur", "اردو": "ur",
    "english": "en", "angrezi": "en", "angraizi": "en",
    "turkish": "tr", "turkey": "tr", "turki": "tr",
    "arabic": "ar", "arbi": "ar", "عربی": "ar",
    "spanish": "es", "espanol": "es",
    "hindi": "hi", "हिंदी": "hi",
    "french": "fr", "france": "fr",
    "german": "de", "germany": "de",
    "portuguese": "pt", "portugal": "pt",
    "indonesian": "id", "indonesia": "id",
    "italian": "it", "italy": "it",
    "russian": "ru",
    "chinese": "zh", "mandarin": "zh",
    "japanese": "ja",
    "korean": "ko",
    "bengali": "bn", "bangla": "bn",
    "punjabi": "pa",
    "pashto": "ps",
}

_VIDEO_ASSET_TYPES = ("video", "short_video", "long_video")


def _extract_target_language(prompt: str) -> str | None:
    """Simple keyword match against the user's message for a language name."""
    lowered = prompt.lower()
    for alias, code in _LANGUAGE_ALIASES.items():
        if alias in lowered:
            return code
    return None


def _find_latest_video_asset(conversation_id: str, owner_id: str):
    """
    Looks through the conversation's messages (most recent first) for the
    last one that points to a completed video asset, and returns that
    Asset row. Returns None if no video is found.
    """
    from app.database.session.database import SessionLocal
    from app.repositories.asset_repository import AssetRepository
    from app.repositories.conversation_repository import ConversationRepository

    db = SessionLocal()
    try:
        convo = ConversationRepository(db).get_by_id(conversation_id)
        if convo is None:
            return None

        asset_repo = AssetRepository(db)

        for message in reversed(convo.messages):
            if not message.asset_id:
                continue
            asset = asset_repo.get_by_id(message.asset_id)
            if (
                asset is not None
                and asset.owner_id == owner_id
                and asset.asset_type in _VIDEO_ASSET_TYPES
                and asset.status == "completed"
                and asset.file_url
            ):
                return asset
        return None
    finally:
        db.close()


class DubbingAgent(BaseAgent):
    """
    Handles requests like "is video ko urdu mein dub karo" - finds the most
    recent video generated in this conversation and dubs it into the
    requested language using ElevenLabs' Dubbing API (which handles
    translation and voice-matching on its own).
    """

    name = "dub"

    async def execute(self, request: AIRequest) -> dict:
        target_lang = _extract_target_language(request.prompt)
        if target_lang is None:
            raise RuntimeError(
                "Mujhe pata nahi chal saka aap kaunsi language mein dub karna "
                "chahte hain. Language ka naam sath likh dein, jaise "
                "\"is video ko Urdu mein dub karo\"."
            )

        if not request.conversation_id or not request.owner_id:
            raise RuntimeError(
                "Dubbing ke liye conversation context nahi mil saka."
            )

        video_asset = _find_latest_video_asset(
            request.conversation_id, request.owner_id
        )
        if video_asset is None:
            raise RuntimeError(
                "Mujhe is conversation mein koi complete video nahi mila jise "
                "dub kiya ja sake. Pehle ek video generate karein, phir dubbing "
                "ka kahein."
            )

        from app.services.providers.implementations.elevenlabs.elevenlabs_provider import (
            ElevenLabsProvider,
        )

        provider = ElevenLabsProvider()
        dubbed_bytes = await provider.dub(
            source_url=video_asset.file_url,
            target_lang=target_lang,
        )

        # Encode as a data URI so this reuses the same, already-working
        # storage path other agents use for URL/data-uri results (see
        # AssetService.complete_from_provider_result / _save_data_uri).
        data_uri = "data:video/mp4;base64," + base64.b64encode(dubbed_bytes).decode()

        return {
            "result": data_uri,
            "provider": "elevenlabs",
            "model": "dubbing",
            "metadata": {
                "dubbed_from_asset_id": video_asset.id,
                "target_language": target_lang,
            },
        }
