from __future__ import annotations

import math

from app.core.pricing.pricing_config import (
    CREDIT_VALUE_USD,
    MARGIN_MULTIPLIER,
    PROVIDER_RAW_COSTS_USD,
    FULLY_FREE_ASSET_TYPES,
    LIMITED_FREE_ASSET_TYPES,
    PAID_ASSET_TYPES,
)


def is_fully_free(asset_type: str) -> bool:
    return asset_type in FULLY_FREE_ASSET_TYPES


def is_limited_free(asset_type: str) -> bool:
    return asset_type in LIMITED_FREE_ASSET_TYPES


def is_paid(asset_type: str) -> bool:
    return asset_type in PAID_ASSET_TYPES


def limited_free_config(asset_type: str) -> dict | None:
    return LIMITED_FREE_ASSET_TYPES.get(asset_type)


def credits_for_generation(
    asset_type: str,
    model_key: str = "default",
    quantity: float | None = None,
) -> int:
    """
    Computes how many credits a single generation costs, using the
    live pricing_config.py numbers. If `quantity` is None, falls back
    to each model's configured `assumed_quantity` (flat per-generation
    pricing) - pass an explicit quantity for exact metered billing
    once the real output length is known.
    Returns an integer number of credits (rounded up - never undercharge).
    """
    bucket = PROVIDER_RAW_COSTS_USD.get(asset_type)
    if not bucket:
        return 0

    model_info = bucket.get(model_key) or next(iter(bucket.values()))

    unit = model_info["unit"]
    raw_cost = model_info["cost"]

    if quantity is None:
        quantity = model_info.get("assumed_quantity", 1)

    if unit == "1000_characters":
        raw_total_usd = raw_cost * (quantity / 1000.0)
    else:
        raw_total_usd = raw_cost * quantity

    margin = MARGIN_MULTIPLIER.get(asset_type, 3.0)
    sell_usd = raw_total_usd * margin

    credits = math.ceil(sell_usd / CREDIT_VALUE_USD)
    return max(credits, 1)