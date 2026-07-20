from dataclasses import dataclass

from app.services.assets.models.asset_context import AssetContext


@dataclass(slots=True, frozen=True)
class FormatResult:
    output_format: str


class FormatEngine:
    """
    Determines export format.

    Future:
    - Provider compatibility
    - Platform optimization
    - User preference
    """

    def resolve(
        self,
        context: AssetContext,
    ) -> FormatResult:

        return FormatResult(
            output_format=context.output_format,
        )