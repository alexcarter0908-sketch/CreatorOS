from app.services.providers.interfaces.base_provider import BaseProvider


class ProviderExecutor:
    """
    Responsible ONLY for executing requests on a provider.

    It does NOT:
    - select providers
    - create providers
    - choose models
    """

    async def execute(
        self,
        provider: BaseProvider,
        prompt: str,
        **kwargs,
    ):

        return await provider.generate(
            prompt=prompt,
            **kwargs,
        )