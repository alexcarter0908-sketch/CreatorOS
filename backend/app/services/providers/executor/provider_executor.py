from __future__ import annotations

import pprint
from app.schemas.ai_request import AIRequest
from app.services.providers.fallback.fallback_resolver import FallbackResolver
from app.services.providers.factory.provider_factory import ProviderFactory
from app.services.providers.selector.provider_selector import ProviderSelector


def _friendly_provider_error(raw: str) -> str:
    """
    Provider/billing errors come back as raw technical blobs (nested
    JSON, API error codes, provider metadata, etc.) - not something to
    show a user directly. The full technical detail is already printed
    above in the "PROVIDER FAILED" block for server-side debugging;
    this just decides what short, human message goes to the chat/UI.
    """
    lowered = raw.lower()
    if (
        "requires more credits" in lowered
        or "insufficient credits" in lowered
        or "not enough credits" in lowered
        or "do not have enough credits" in lowered
    ):
        return "This generation didn't go through because of insufficient credits - either on your account or on our provider's side. Please check your credit balance, and try again shortly - this usually clears up quickly."
    return "All AI providers are temporarily unavailable. Please try again in a moment."


class ProviderExecutor:
    """
    Executes AI requests with automatic provider/model fallback.
    """

    def __init__(self):
        self.fallback = FallbackResolver()
        self.selector = ProviderSelector()
        self.factory = ProviderFactory()

    async def execute(self, request: AIRequest) -> dict:
        print("\n" + "=" * 80)
        print("INCOMING REQUEST")
        print("=" * 80)
        pprint.pprint(request.model_dump())
        print("=" * 80)

        # Initial model selection
        model = self.selector.select(request)

        print("\nAFTER SELECT")
        print("request.asset_type =", request.asset_type)
        print("selected.id        =", model.id)
        print("selected.provider  =", model.provider)

        payload = request.model_dump(
            exclude={
                "asset_type",
                "provider",
                "model",
                "prompt",
            },
            exclude_none=True,
        )

        tried: set[tuple[str, str]] = set()

        while True:
            key = (model.provider, model.id)

            if key in tried:
                raise RuntimeError("No working AI model available.")

            tried.add(key)
            try:
                provider = self.factory.create(model.provider)

                print("=" * 80)
                print("EXECUTING")
                print("=" * 80)
                print("Provider :", model.provider)
                print("Model    :", model.model)
                print("Asset    :", request.asset_type)
                print("=" * 80)

                result = await provider.generate(
                    asset_type=request.asset_type,
                    model=model.model,
                    prompt=request.prompt,
                    **payload,
                )

                print("=" * 80)
                print("SUCCESS")
                print("=" * 80)
                return result

            except Exception as e:
                print("=" * 80)
                print("PROVIDER FAILED")
                print("=" * 80)
                print("Provider :", model.provider)
                print("Model    :", model.id)
                print("Error    :", repr(e))
                print("Type     :", type(e).__name__)
                print("=" * 80)

                # Use Fallback Resolver to find the next best model
                next_model = self.fallback.resolve(
                    asset_type=request.asset_type,
                    tried=tried,
                )

                if next_model is None:
                    raise RuntimeError(
                        _friendly_provider_error(str(e))
                    ) from e

                print(f"Fallback: {model.id} -> {next_model.id}")
                model = next_model

    async def health_report(self) -> dict[str, bool]:
        return await self.factory.health_report()

    def available_providers(self) -> list[str]:
        return self.factory.available()

    def reload(self) -> list[str]:
        return self.factory.reload()