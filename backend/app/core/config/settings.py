from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Global application configuration.

    This is the single source of truth for all runtime settings.
    """

    APP_NAME: str = "CreatorOS API"
    APP_VERSION: str = "1.0.0"

    API_V1_PREFIX: str = "/api/v1"

    DEBUG: bool = True

    FRONTEND_URL: str = "http://localhost:3000"

    DATABASE_URL: str = "sqlite:///./creatoros.db"

    JWT_SECRET_KEY: str = Field(
        default="CHANGE_THIS_IN_PRODUCTION"
    )

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # ---------- AI Providers ----------

    OPENAI_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

    ANTHROPIC_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    DEEPSEEK_API_KEY: str = ""

    FAL_API_KEY: str = ""

    REPLICATE_API_TOKEN: str = ""

    RUNWAY_API_KEY: str = ""

    KLING_ACCESS_KEY: str = ""
    KLING_SECRET_KEY: str = ""

    PIKA_API_KEY: str = ""

    ELEVENLABS_API_KEY: str = ""

    FISH_AUDIO_API_KEY: str = ""
    PIXVERSE_API_KEY: str = ""
    SOGNI_API_KEY: str = ""

    # ---------- Billing (Paddle) ----------

    PADDLE_API_KEY: str = ""

    PADDLE_WEBHOOK_SECRET: str = ""

    PADDLE_ENVIRONMENT: str = "sandbox"  # "sandbox" or "production"

    TOGETHER_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""
    XAI_API_KEY: str = ""

    # ---------- Search (research grounding) ----------
    SERPER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    EXA_API_KEY: str = ""

    # ---------- Email (SMTP for OTP) ----------

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""

    OTP_EXPIRE_MINUTES: int = 10

    # ---------- Publishing / Social OAuth ----------

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/publish/youtube/callback"
    GOOGLE_LOGIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # ---------- Defaults ----------

    DEFAULT_TEXT_MODEL: str = "gpt-5.5"

    DEFAULT_IMAGE_MODEL: str = "flux-pro"

    DEFAULT_VIDEO_MODEL: str = "kling-v2"
    DEFAULT_AUDIO_MODEL: str = "elevenlabs-v2"

    REQUEST_TIMEOUT: int = 300
    STORAGE_PATH: str = "storage"
    STORAGE_BASE_URL: str = "http://localhost:8000/storage"

    # Used to interpret AutoTarget.run_at_hour as local time (e.g. PKT = UTC+5)
    DEFAULT_TIMEZONE_OFFSET_HOURS: int = 5

    MAX_RETRIES: int = 3

    # ---------- Knowledge / RAG ----------

    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    KNOWLEDGE_CHUNK_SIZE: int = 1000
    KNOWLEDGE_CHUNK_OVERLAP: int = 150
    KNOWLEDGE_TOP_K: int = 5
    KNOWLEDGE_MAX_FILE_SIZE_MB: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    # NOTE: A stale Windows User-level environment variable for
    # ELEVENLABS_API_KEY was found to override the .env file value
    # (OS env vars normally take priority over .env in pydantic-settings).
    # Since Windows caches User env vars in already-running processes
    # until a full logoff/reboot, we explicitly strip it here so the
    # .env file value is always authoritative for this key.
    import os
    os.environ.pop("ELEVENLABS_API_KEY", None)
    return Settings()


settings = get_settings()