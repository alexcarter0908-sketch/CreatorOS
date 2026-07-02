from dataclasses import dataclass, field


@dataclass(slots=True)
class AISettings:
    default_provider: str = "openai"
    fallback_enabled: bool = True
    retry_attempts: int = 2
    timeout_seconds: int = 120
    max_parallel_requests: int = 5


@dataclass(slots=True)
class GenerationSettings:
    quality: str = "ultra"
    speed: str = "balanced"

    auto_detect_language: bool = True
    auto_detect_platform: bool = True
    auto_detect_asset: bool = True

    optimize_prompt: bool = True


@dataclass(slots=True)
class ImageSettings:
    default_format: str = "png"
    upscale: bool = True
    remove_background: bool = False


@dataclass(slots=True)
class VideoSettings:
    default_format: str = "mp4"
    fps: int = 30
    auto_subtitles: bool = True


@dataclass(slots=True)
class AudioSettings:
    default_format: str = "mp3"
    normalize_audio: bool = True


@dataclass(slots=True)
class LanguageSettings:
    default_language: str = "auto"
    supported_languages: list[str] = field(
        default_factory=lambda: [
            "english",
            "urdu",
            "roman_urdu",
            "hindi",
            "arabic",
        ]
    )


@dataclass(slots=True)
class CreatorOSConfig:
    ai: AISettings = field(default_factory=AISettings)
    generation: GenerationSettings = field(default_factory=GenerationSettings)
    image: ImageSettings = field(default_factory=ImageSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    language: LanguageSettings = field(default_factory=LanguageSettings)


creatoros_config = CreatorOSConfig()