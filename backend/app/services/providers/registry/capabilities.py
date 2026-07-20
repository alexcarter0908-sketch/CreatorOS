from __future__ import annotations

from enum import StrEnum


class Capability(StrEnum):
    TEXT = "text"
    CHAT = "chat"

    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    POSTER = "poster"
    BANNER = "banner"
    LOGO = "logo"
    PROFILE_PHOTO = "profile_photo"
    COVER = "cover"

    VIDEO = "video"

    AUDIO = "audio"
    VOICE = "voice"

    EMBEDDING = "embedding"

    VISION = "vision"

    OCR = "ocr"

    MODERATION = "moderation"

    TRANSLATION = "translation"

    CODE = "code"

    # -----------------------------
    # AI Features
    # -----------------------------

    REASONING = "reasoning"
    FUNCTION_CALLING = "function_calling"
    TOOL_CALLING = "tool_calling"
    JSON_MODE = "json_mode"
    STRUCTURED_OUTPUT = "structured_output"
    STREAMING = "streaming"
    LONG_CONTEXT = "long_context"
    JSON = "json"
    WEB_SEARCH = "web_search"
    TOOLS = "tools"
    EDITING = "editing"    

