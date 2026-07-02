from app.schemas.ai_request import AIRequest


class PromptEngine:
    """
    Central prompt optimization engine.

    Future responsibilities:
    - Language detection
    - Asset detection
    - Platform detection
    - Prompt enhancement
    - Negative prompt generation
    - Provider formatting
    """

    def process(
        self,
        request: AIRequest,
    ) -> AIRequest:

        request.prompt = request.prompt.strip()

        if not request.asset_type:
            request.asset_type = "text"

        if not request.language:
            request.language = "auto"

        if not request.platform:
            request.platform = "generic"

        return request