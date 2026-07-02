from dataclasses import dataclass
from typing import Dict


@dataclass(slots=True, frozen=True)
class ToolDefinition:
    id: str
    name: str
    category: str
    provider: str
    enabled: bool = True


TOOL_REGISTRY: Dict[str, ToolDefinition] = {

    # ---------- LLM ----------

    "gpt": ToolDefinition(
        id="gpt",
        name="GPT",
        category="llm",
        provider="openai",
    ),

    "claude": ToolDefinition(
        id="claude",
        name="Claude",
        category="llm",
        provider="anthropic",
    ),

    "gemini": ToolDefinition(
        id="gemini",
        name="Gemini",
        category="llm",
        provider="google",
    ),

    # ---------- Image ----------

    "flux": ToolDefinition(
        id="flux",
        name="Flux",
        category="image_generation",
        provider="fal",
    ),

    # ---------- Video ----------

    "runway": ToolDefinition(
        id="runway",
        name="Runway",
        category="video_generation",
        provider="runway",
    ),

    "kling": ToolDefinition(
        id="kling",
        name="Kling",
        category="video_generation",
        provider="kling",
    ),

    "pika": ToolDefinition(
        id="pika",
        name="Pika",
        category="video_generation",
        provider="pika",
    ),

    # ---------- Audio ----------

    "elevenlabs": ToolDefinition(
        id="elevenlabs",
        name="ElevenLabs",
        category="text_to_speech",
        provider="elevenlabs",
    ),

    # ---------- Search ----------

    "tavily": ToolDefinition(
        id="tavily",
        name="Tavily",
        category="search",
        provider="tavily",
    ),

    "serper": ToolDefinition(
        id="serper",
        name="Serper",
        category="search",
        provider="serper",
    ),

    "exa": ToolDefinition(
        id="exa",
        name="Exa",
        category="search",
        provider="exa",
    ),
}