from enum import StrEnum


class AssetType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    THUMBNAIL = "thumbnail"
    POSTER = "poster"
    LOGO = "logo"
    BANNER = "banner"
    PROFILE_PHOTO = "profile_photo"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"


class ProviderType(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    FAL = "fal"
    REPLICATE = "replicate"
    RUNWAY = "runway"
    KLING = "kling"
    PIKA = "pika"
    ELEVENLABS = "elevenlabs"


class WorkflowType(StrEnum):
    CHAT = "chat"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    RESEARCH = "research"
    WEBSITE = "website"
    APP = "app"
    MARKETING = "marketing"
    AUTOMATION = "automation"


class LanguageType(StrEnum):
    AUTO = "auto"
    ENGLISH = "english"
    URDU = "urdu"
    ROMAN_URDU = "roman_urdu"
    HINDI = "hindi"
    ARABIC = "arabic"


class PlatformType(StrEnum):
    GENERIC = "generic"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    X = "x"


class OutputFormat(StrEnum):
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    MP4 = "mp4"
    MP3 = "mp3"
    WAV = "wav"
    PDF = "pdf"
    DOCX = "docx"