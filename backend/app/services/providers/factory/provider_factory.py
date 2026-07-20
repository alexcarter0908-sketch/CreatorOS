from __future__ import annotations

from app.services.providers.base_provider import BaseProvider
from app.services.providers.registry import PROVIDER_REGISTRY


class ProviderFactory:
    """
    Enterprise Provider Factory
    """

    def __init__(self):

        self._instances: dict[str, BaseProvider] = {}

    @property
    def registry(self):

        return PROVIDER_REGISTRY

    # ---------------------------------------------------------

    def _is_available(self, definition) -> bool:

        try:
            return bool(definition.available)
        except Exception:
            return False

    # ---------------------------------------------------------

    def available(self) -> list[str]:

        providers = [
            provider_id
            for provider_id, definition in self.registry.items()
            if self._is_available(definition)
        ]

        providers.sort(
            key=lambda p: self.registry[p].priority
        )

        return providers

    # ---------------------------------------------------------

    def has_provider(
        self,
        provider: str,
    ) -> bool:

        definition = self.registry.get(provider)

        if definition is None:
            return False

        return self._is_available(definition)

    # ---------------------------------------------------------

    def create(
        self,
        provider: str,
    ) -> BaseProvider:

        if provider in self._instances:
            return self._instances[provider]

        definition = self.registry.get(provider)

        if definition is None:
            raise RuntimeError(
                f"Unknown provider '{provider}'."
            )

        if not definition.enabled:
            raise RuntimeError(
                f"Provider '{provider}' is disabled."
            )

        if not definition.api_key:
            raise RuntimeError(
                f"Missing API key for '{provider}'."
            )

        if definition.provider_class is None:
            raise NotImplementedError(
                f"{provider} provider not implemented."
            )

        try:
            instance = definition.provider_class()
        except TypeError as exc:
            raise RuntimeError(
                f"Provider '{provider}' failed to instantiate "
                f"(likely a missing abstract method implementation): {exc}"
            ) from exc

        self._instances[provider] = instance

        return instance

    # ---------------------------------------------------------

    async def health_report(
        self,
    ) -> dict[str, bool]:

        report: dict[str, bool] = {}

        for provider in self.available():

            try:

                instance = self.create(provider)

                report[provider] = (
                    await instance.health_check()
                )

            except Exception:

                report[provider] = False

        return report

    # ---------------------------------------------------------

    def clear_cache(self):

        self._instances.clear()

    # ---------------------------------------------------------

    def reload(self):

        self.clear_cache()

        return self.available()
