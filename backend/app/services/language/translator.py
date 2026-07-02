from dataclasses import dataclass


@dataclass(slots=True)
class TranslationResult:
    source_language: str
    target_language: str
    original_text: str
    translated_text: str


class Translator:

    async def to_english(
        self,
        text: str,
        source_language: str,
    ) -> TranslationResult:

        if source_language == "en":
            return TranslationResult(
                source_language="en",
                target_language="en",
                original_text=text,
                translated_text=text,
            )

        # Placeholder
        # Later:
        # OpenAI
        # Gemini
        # Anthropic
        # DeepL

        return TranslationResult(
            source_language=source_language,
            target_language="en",
            original_text=text,
            translated_text=text,
        )

    async def from_english(
        self,
        text: str,
        target_language: str,
    ) -> TranslationResult:

        if target_language == "en":
            return TranslationResult(
                source_language="en",
                target_language="en",
                original_text=text,
                translated_text=text,
            )

        return TranslationResult(
            source_language="en",
            target_language=target_language,
            original_text=text,
            translated_text=text,
        )