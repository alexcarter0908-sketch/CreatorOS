from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class AIModel:
    """
    Canonical definition of an AI model.

    Every provider model inside CreatorOS must be registered
    using this dataclass.

    The registry is provider-agnostic and supports:

    • Text
    • Vision
    • Image Generation
    • Video Generation
    • Audio
    • Embeddings
    • Search
    • Reasoning
    • Function Calling

    Future:
    • MCP
    • A2A
    • Multi-Agent
    """

    # =====================================================
    # Identity
    # =====================================================

    id: str

    provider: str

    model: str

    category: str

    display_name: str = ""

    description: str = ""

    # =====================================================
    # Availability
    # =====================================================

    enabled: bool = True

    priority: int = 100

    # =====================================================
    # Performance
    # =====================================================

    quality: str = "high"

    speed: str = "balanced"

    cost: str = "medium"

    max_context: int = 0

    # =====================================================
    # Supported Capabilities
    # =====================================================

    supports_text: bool = False

    supports_image: bool = False

    supports_video: bool = False

    supports_audio: bool = False

    supports_vision: bool = False

    supports_streaming: bool = False

    supports_embeddings: bool = False

    supports_reasoning: bool = False

    supports_json_mode: bool = False

    supports_function_calling: bool = False

    supports_web_search: bool = False

    supports_tools: bool = False

    supports_editing: bool = False

    # =====================================================
    # Limits
    # =====================================================

    max_images: int = 0

    max_video_seconds: int = 0

    max_audio_minutes: int = 0

    # =====================================================
    # Automatic fallback chain
    # =====================================================

    fallback: tuple[str, ...] = field(
        default_factory=tuple,
    )

    # =====================================================
    # Provider Metadata
    # =====================================================

    metadata: dict = field(
        default_factory=dict,
    )