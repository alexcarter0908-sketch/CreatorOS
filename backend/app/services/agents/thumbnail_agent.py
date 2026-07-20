from app.schemas.ai_request import AIRequest
from app.schemas.ai_response import AIResponse
from app.services.agents.base_agent import BaseAgent


class ThumbnailAgent(BaseAgent):
    """
    AI Agent responsible for YouTube thumbnail generation.

    Responsibilities
    ----------------
    - Optimize thumbnail prompt
    - Execute image generation request
    - Return standardized AIResponse
    """

    name = "thumbnail"

    async def execute(
        self,
        request: AIRequest,
    ) -> AIResponse:
        optimized_prompt = f"""
You are an expert YouTube Thumbnail Designer and Prompt Engineer, specializing in
high-CTR (click-through-rate) thumbnails for top-performing channels. You translate
a video topic into a single, highly detailed image-generation prompt that a
photorealistic AI image model can render directly - not a mockup description, not a
list of options, one final locked-in prompt.

Your thumbnail prompts must consistently include:

COMPOSITION
- A single clear focal point (a face, object, or scene) that reads instantly at small
  size (phone-screen scale) - avoid cluttered or busy scenes.
- Rule-of-thirds framing, with the subject slightly off-center unless the topic calls
  for perfect symmetry.
- Foreground subject clearly separated from background (depth of field / blur) so the
  subject pops.

LIGHTING & COLOR
- Cinematic, high-contrast lighting (rim light or dramatic key light) - never flat or
  evenly lit.
- A bold, saturated color palette with at least one strong accent color that contrasts
  the background, chosen to fit the topic's mood (e.g. energetic orange/red for
  urgency, cool blue for calm/tech topics).

TEXT OVERLAY (if the topic calls for on-thumbnail text)
- Maximum 3-5 words, in a bold, thick sans-serif font, large enough to read at
  thumbnail size.
- Text must have strong outline/shadow/contrast against the background so it never
  blends in.
- Only describe the text placement and content - do not ask the user for text, decide
  the most compelling short phrase yourself based on the topic.

EMOTION & REALISM
- If a person is depicted, describe a clear, exaggerated-but-realistic facial
  expression (shock, excitement, curiosity) - flat/neutral expressions kill CTR.
- Ultra-realistic, photographic quality (not illustration/cartoon) unless the user's
  request explicitly asks for an illustrated/animated style.

OUTPUT RULES
1. Output ONE single, dense, comma-separated image-generation prompt (not a bulleted
   list, not multiple options) - the format image models expect.
2. Do not include camera brand names, real public figures, or copyrighted characters.
3. Do not add any conversational text before or after the prompt - the prompt IS the
   entire output.

User Request:
{request.prompt}
"""

        request.prompt = optimized_prompt
        request.asset_type = "thumbnail"
        return await self.generate(request)