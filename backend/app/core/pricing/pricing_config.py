from __future__ import annotations

# ============================================================
# SINGLE SOURCE OF TRUTH for AI-provider costs, profit margins,
# and credit economics. Update ONLY this file when a provider
# changes its price - every other part of the app reads from
# here, so nothing else needs to change.
#
# Sources (verified against provider pricing pages, mid-2026):
#   - fal.ai (Flux Pro image, Kling v2 video)  -> fal.ai/pricing
#   - ElevenLabs (text-to-speech)               -> elevenlabs.io/pricing/api
# ============================================================

CREDIT_VALUE_USD = 0.01  # 1 credit = $0.01 USD  (100 credits = $1)

# Raw provider cost per unit, in USD - what WE pay the provider.
# "assumed_quantity" is used when we charge a flat per-generation
# price up front (before the real output length is known). Phase 2
# can replace this with exact post-generation metering.
PROVIDER_RAW_COSTS_USD: dict[str, dict[str, dict]] = {
    "image": {
        "flux-pro": {"unit": "image", "cost": 0.05},
        "flux-schnell": {"unit": "image", "cost": 0.025},
    },
    "video": {
        "kling-v2-pro": {"unit": "second", "cost": 0.112, "assumed_quantity": 5},
        "kling-v2-standard": {"unit": "second", "cost": 0.084, "assumed_quantity": 5},
    },
    "audio": {
        "elevenlabs-multilingual-v2": {"unit": "1000_characters", "cost": 0.10, "assumed_quantity": 500},
        "elevenlabs-flash": {"unit": "1000_characters", "cost": 0.05, "assumed_quantity": 500},
    },
}

# Profit margin multiplier applied on top of raw cost, per asset type.
# Tune these based on market analysis - video stays tighter since raw
# cost is already high; image/audio can carry more markup.
MARGIN_MULTIPLIER: dict[str, float] = {
    "image": 4.0,
    "video": 2.5,
    "audio": 5.0,
}

# Asset types that are ALWAYS free, no daily cap.
FULLY_FREE_ASSET_TYPES = {"text", "research", "seo", "document"}

# Asset types free up to a daily quota, then cost credits.
LIMITED_FREE_ASSET_TYPES: dict[str, dict] = {
    "script": {
        "daily_free_quota": 10,        # 10 free scripts per user per day
        "credit_cost_after_quota": 8,  # flat credits per script after quota
    },
}

# Asset types that always consume credits (no free quota at all).
PAID_ASSET_TYPES = {"image", "video", "audio"}

# Credit packs sold to users. `paddle_price_id` must be filled in once
# you create matching Products/Prices in your Paddle dashboard
# (sandbox first, then production) - see README note at bottom.
CREDIT_PACKS: list[dict] = [
    {
        "id": "starter",
        "credits": 500,
        "price_usd": 5.00,
        "popular": False,
        "paddle_price_id": "REPLACE_WITH_PADDLE_PRICE_ID_STARTER",
    },
    {
        "id": "creator",
        "credits": 1200,
        "price_usd": 10.00,
        "popular": True,
        "paddle_price_id": "REPLACE_WITH_PADDLE_PRICE_ID_CREATOR",
    },
    {
        "id": "pro",
        "credits": 6500,
        "price_usd": 50.00,
        "popular": False,
        "paddle_price_id": "REPLACE_WITH_PADDLE_PRICE_ID_PRO",
    },
]


def get_credit_pack(pack_id: str) -> dict | None:
    return next((p for p in CREDIT_PACKS if p["id"] == pack_id), None)


# ------------------------------------------------------------
# HOW TO UPDATE PRICING LATER (the only file you should touch):
#   1. Provider changes price -> edit PROVIDER_RAW_COSTS_USD above.
#   2. Want more/less profit -> edit MARGIN_MULTIPLIER above.
#   3. New credit pack / price change -> edit CREDIT_PACKS above.
# Nothing else in the codebase needs to change.
# ------------------------------------------------------------