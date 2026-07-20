from __future__ import annotations

from app.services.providers.registry.model import AIModel
from app.services.providers.registry.models import ALL_MODELS

MODEL_REGISTRY: dict[str, AIModel] = {}
PROVIDER_MODELS: dict[str, list[AIModel]] = {}
CATEGORY_MODELS: dict[str, list[AIModel]] = {}


def _priority(model: AIModel) -> int:
    return getattr(model, "priority", 100)


for model in ALL_MODELS:

    if model.id in MODEL_REGISTRY:
        raise RuntimeError(
            f"Duplicate model id: {model.id}"
        )

    MODEL_REGISTRY[model.id] = model

    PROVIDER_MODELS.setdefault(
        model.provider,
        [],
    ).append(model)

    CATEGORY_MODELS.setdefault(
        model.category,
        [],
    ).append(model)


for models in PROVIDER_MODELS.values():

    models.sort(
        key=_priority,
    )


for models in CATEGORY_MODELS.values():

    models.sort(
        key=_priority,
    )


def get_model(
    model_id: str,
) -> AIModel | None:

    return MODEL_REGISTRY.get(model_id)


def get_provider_models(
    provider: str,
) -> list[AIModel]:

    return PROVIDER_MODELS.get(
        provider,
        [],
    )


def get_category_models(
    category: str,
) -> list[AIModel]:

    return CATEGORY_MODELS.get(
        category,
        [],
    )


def get_best_model(
    category: str,
) -> AIModel | None:

    models = CATEGORY_MODELS.get(
        category,
        [],
    )

    if not models:
        return None

    return models[0]


def all_models() -> list[AIModel]:

    return list(
        MODEL_REGISTRY.values()
    )