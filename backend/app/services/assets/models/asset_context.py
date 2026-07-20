from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class AssetContext:
    """
    Runtime asset context.

    Created once by AssetDetector.

    Every engine consumes this object.

    No engine should detect the prompt again.
    """

    # Original Request

    prompt: str

    # Detection

    asset_type: str

    platform: str

    workflow: str

    language: str

    # Output

    width: int

    height: int

    aspect_ratio: str

    orientation: str

    output_format: str

    quality: str

    # AI

    provider: str | None = None

    model: str | None = None

    # Runtime

    metadata: dict[str, Any] = field(default_factory=dict)