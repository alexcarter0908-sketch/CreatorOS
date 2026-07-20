from __future__ import annotations

from dataclasses import dataclass, field

from app.services.providers.registry.capabilities import Capability


@dataclass(slots=True, frozen=True)
class AIModel:
    """
    Canonical AI Model Definition.

    Every provider registers one or more AIModel objects.

    Capability-driven architecture.

    Future ready:
    • OpenAI
    • Anthropic
    • Gemini
    • Groq
    • Together
    • Fireworks
    • DeepSeek
    • Mistral
    • Cohere
    • ElevenLabs
    • FAL
    • Replicate
    • Kling
    • Runway
    • Pika
    • Stability
    • Ideogram
    • Minimax
    • MCP
    • A2A
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
    # NEW CAPABILITY SYSTEM
    # =====================================================

    capabilities: frozenset[Capability] = field(
        default_factory=frozenset
    )

    # =====================================================
    # Legacy Compatibility
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
    # Fallback
    # =====================================================

    fallback: tuple[str, ...] = field(
        default_factory=tuple
    )

    # =====================================================
    # Metadata
    # =====================================================

    metadata: dict = field(
        default_factory=dict
    )

    # =====================================================
    # Auto capability bridge
    # =====================================================

    def __post_init__(self):

        caps = set(self.capabilities)

        if self.supports_text:
            caps.add(Capability.TEXT)

        if self.supports_image:
            caps.add(Capability.IMAGE)

        if self.supports_video:
            caps.add(Capability.VIDEO)

        if self.supports_audio:
            caps.add(Capability.AUDIO)

        if self.supports_vision:
            caps.add(Capability.VISION)

        if self.supports_embeddings:
            caps.add(Capability.EMBEDDING)

        if self.supports_reasoning:
            caps.add(Capability.REASONING)

        if self.supports_streaming:
            caps.add(Capability.STREAMING)

        if self.supports_json_mode:
            caps.add(Capability.JSON)

        if self.supports_function_calling:
            caps.add(Capability.FUNCTION_CALLING)

        if self.supports_web_search:
            caps.add(Capability.WEB_SEARCH)

        if self.supports_tools:
            caps.add(Capability.TOOLS)

        if self.supports_editing:
            caps.add(Capability.EDITING)

        object.__setattr__(
            self,
            "capabilities",
            frozenset(caps),
        )

    # =====================================================

    def supports(
        self,
        capability: Capability,
    ) -> bool:

        return capability in self.capabilities