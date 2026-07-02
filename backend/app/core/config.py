from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    CreatorOS Configuration

    Loads all environment variables
    from the .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ======================
    # Application
    # ======================

    APP_NAME: str = "CreatorOS API"
    APP_VERSION: str = "1.0.0"

    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    FRONTEND_URL: str = "http://localhost:3000"

    # ======================
    # Database
    # ======================

    DATABASE_URL: str = "sqlite:///./creatoros.db"

    # ======================
    # Authentication
    # ======================

    JWT_SECRET_KEY: str = ""

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ======================
    # AI Providers
    # ======================

    OPENAI_API_KEY: str = ""

    ANTHROPIC_API_KEY: str = ""

    GEMINI_API_KEY: str = ""

    DEEPSEEK_API_KEY: str = ""

    GROQ_API_KEY: str = ""

    ELEVENLABS_API_KEY: str = ""

    RUNWAY_API_KEY: str = ""

    PIKA_API_KEY: str = ""

    KLING_API_KEY: str = ""

    FAL_API_KEY: str = ""

    REPLICATE_API_TOKEN: str = ""

    SERPER_API_KEY: str = ""

    TAVILY_API_KEY: str = ""

    EXA_API_KEY: str = ""


settings = Settings()