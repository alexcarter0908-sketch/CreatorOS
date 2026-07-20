function Write-Utf8NoBomAbs {
    param([string]$Path, [string]$Content)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding($false)))
}

$Backend = "C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\backend"

# ============================================================
# FILE 1 (NEW): app/core/pricing/__init__.py
# ============================================================
Write-Utf8NoBomAbs -Path "$Backend\app\core\pricing\__init__.py" -Content ""
Write-Host "1/16 app/core/pricing/__init__.py created" -ForegroundColor Green


# ============================================================
# FILE 2 (NEW): app/core/pricing/pricing_config.py
# SINGLE SOURCE OF TRUTH for all costs, margins, credit packs.
# Update ONLY this file when a provider's price changes.
# ============================================================
$pricingConfig = @'
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
FULLY_FREE_ASSET_TYPES = {"text", "research"}

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
        "paddle_price_id": "REPLACE_WITH_PADDLE_PRICE_ID_STARTER",
    },
    {
        "id": "creator",
        "credits": 1200,
        "price_usd": 10.00,
        "paddle_price_id": "REPLACE_WITH_PADDLE_PRICE_ID_CREATOR",
    },
    {
        "id": "pro",
        "credits": 6500,
        "price_usd": 50.00,
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
'@
Write-Utf8NoBomAbs -Path "$Backend\app\core\pricing\pricing_config.py" -Content $pricingConfig
Write-Host "2/16 app/core/pricing/pricing_config.py created" -ForegroundColor Green


# ============================================================
# FILE 3 (NEW): app/core/pricing/pricing_service.py
# ============================================================
$pricingService = @'
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
'@
Write-Utf8NoBomAbs -Path "$Backend\app\core\pricing\pricing_service.py" -Content $pricingService
Write-Host "3/16 app/core/pricing/pricing_service.py created" -ForegroundColor Green


# ============================================================
# FILE 4 (NEW): app/database/models/billing.py
# ============================================================
$billingModel = @'
from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class BillingAccount(Base, BaseModelMixin):
    """One-to-one with User. Tracks credit balance and daily free quotas."""

    __tablename__ = "billing_accounts"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    credit_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Free-tier daily quota tracking (e.g. for "script")
    free_quota_used_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    free_quota_date: Mapped[str | None] = mapped_column(String(10), nullable=True)  # "YYYY-MM-DD"

    user = relationship("User")


class CreditTransaction(Base, BaseModelMixin):
    """Append-only ledger of every credit movement (audit trail)."""

    __tablename__ = "credit_transactions"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # purchase | consumption | refund | bonus
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = added, negative = spent
    balance_after: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_id: Mapped[str | None] = mapped_column(
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    paddle_transaction_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    user = relationship("User")
'@
Write-Utf8NoBomAbs -Path "$Backend\app\database\models\billing.py" -Content $billingModel
Write-Host "4/16 app/database/models/billing.py created" -ForegroundColor Green


# ============================================================
# FILE 5: app/database/models/__init__.py - register new models
# (targeted insert, existing models untouched)
# ============================================================
$modelsInitPath = "$Backend\app\database\models\__init__.py"
$modelsInitContent = Get-Content -Raw -Encoding UTF8 $modelsInitPath

if ($modelsInitContent -match "BillingAccount") {
    Write-Host "5/16 models/__init__.py already has billing models - skipped" -ForegroundColor Yellow
} else {
    $modelsInitContent = $modelsInitContent -replace `
        "from app\.database\.models\.knowledge import KnowledgeDocument, KnowledgeChunk", `
        "from app.database.models.knowledge import KnowledgeDocument, KnowledgeChunk`r`nfrom app.database.models.billing import BillingAccount, CreditTransaction"
    $modelsInitContent = $modelsInitContent -replace `
        '"KnowledgeChunk",', `
        "`"KnowledgeChunk`",`r`n    `"BillingAccount`",`r`n    `"CreditTransaction`","
    Write-Utf8NoBomAbs -Path $modelsInitPath -Content $modelsInitContent
    Write-Host "5/16 models/__init__.py updated (BillingAccount, CreditTransaction)" -ForegroundColor Green
}


# ============================================================
# FILE 6 (NEW): app/services/billing/__init__.py
# ============================================================
Write-Utf8NoBomAbs -Path "$Backend\app\services\billing\__init__.py" -Content ""
Write-Host "6/16 app/services/billing/__init__.py created" -ForegroundColor Green


# ============================================================
# FILE 7 (NEW): app/services/billing/credit_service.py
# ============================================================
$creditService = @'
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.database.models.billing import BillingAccount, CreditTransaction
from app.core.pricing.pricing_service import limited_free_config


class InsufficientCreditsError(Exception):
    pass


def _get_or_create_account(db: Session, user_id: str) -> BillingAccount:
    account = db.query(BillingAccount).filter(BillingAccount.user_id == user_id).first()
    if account is None:
        account = BillingAccount(user_id=user_id, credit_balance=0)
        db.add(account)
        db.flush()
    return account


def get_balance(db: Session, user_id: str) -> int:
    return _get_or_create_account(db, user_id).credit_balance


def add_credits(
    db: Session,
    user_id: str,
    amount: int,
    description: str,
    paddle_transaction_id: str | None = None,
) -> int:
    account = _get_or_create_account(db, user_id)
    account.credit_balance += amount
    db.add(CreditTransaction(
        user_id=user_id,
        type="purchase" if paddle_transaction_id else "bonus",
        amount=amount,
        balance_after=account.credit_balance,
        description=description,
        paddle_transaction_id=paddle_transaction_id,
    ))
    db.commit()
    return account.credit_balance


def deduct_credits(
    db: Session,
    user_id: str,
    amount: int,
    description: str,
    asset_id: str | None = None,
) -> int:
    account = _get_or_create_account(db, user_id)
    if account.credit_balance < amount:
        raise InsufficientCreditsError(f"Need {amount} credits, have {account.credit_balance}")
    account.credit_balance -= amount
    db.add(CreditTransaction(
        user_id=user_id,
        type="consumption",
        amount=-amount,
        balance_after=account.credit_balance,
        description=description,
        asset_id=asset_id,
    ))
    db.commit()
    return account.credit_balance


def refund_credits(
    db: Session,
    user_id: str,
    amount: int,
    description: str,
    asset_id: str | None = None,
) -> int:
    account = _get_or_create_account(db, user_id)
    account.credit_balance += amount
    db.add(CreditTransaction(
        user_id=user_id,
        type="refund",
        amount=amount,
        balance_after=account.credit_balance,
        description=description,
        asset_id=asset_id,
    ))
    db.commit()
    return account.credit_balance


def try_consume_free_quota(db: Session, user_id: str, asset_type: str) -> bool:
    """
    Returns True if this generation was covered by today's free quota
    (and marks it used). Returns False if the quota is exhausted,
    meaning the caller must charge credits instead.
    """
    config = limited_free_config(asset_type)
    if not config:
        return False

    account = _get_or_create_account(db, user_id)
    today = date.today().isoformat()

    if account.free_quota_date != today:
        account.free_quota_date = today
        account.free_quota_used_today = 0

    if account.free_quota_used_today < config["daily_free_quota"]:
        account.free_quota_used_today += 1
        db.commit()
        return True

    return False
'@
Write-Utf8NoBomAbs -Path "$Backend\app\services\billing\credit_service.py" -Content $creditService
Write-Host "7/16 app/services/billing/credit_service.py created" -ForegroundColor Green


# ============================================================
# FILE 8 (NEW): app/services/billing/paddle_service.py
# ============================================================
$paddleService = @'
from __future__ import annotations

import hashlib
import hmac

import requests

from app.core.config.settings import settings

_PADDLE_API_BASE = {
    "sandbox": "https://sandbox-api.paddle.com",
    "production": "https://api.paddle.com",
}


def _api_base() -> str:
    return _PADDLE_API_BASE.get(settings.PADDLE_ENVIRONMENT, _PADDLE_API_BASE["sandbox"])


def create_transaction(price_id: str, customer_email: str, custom_data: dict) -> dict:
    """
    Creates a Paddle transaction for a one-time credit-pack purchase.
    Returns Paddle's transaction object, including a checkout URL the
    frontend can redirect to (or open via Paddle.js overlay checkout).
    """
    resp = requests.post(
        f"{_api_base()}/transactions",
        headers={
            "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "items": [{"price_id": price_id, "quantity": 1}],
            "customer": {"email": customer_email},
            "custom_data": custom_data,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["data"]


def verify_webhook_signature(raw_body: bytes, signature_header: str) -> bool:
    """
    Verifies Paddle's webhook HMAC-SHA256 signature.
    Header format: "ts=<timestamp>;h1=<hex_signature>"
    """
    if not signature_header:
        return False

    try:
        parts = dict(p.split("=", 1) for p in signature_header.split(";") if "=" in p)
    except ValueError:
        return False

    ts = parts.get("ts")
    received_sig = parts.get("h1")
    if not ts or not received_sig:
        return False

    signed_payload = f"{ts}:{raw_body.decode('utf-8')}"
    expected_sig = hmac.new(
        settings.PADDLE_WEBHOOK_SECRET.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected_sig, received_sig)
'@
Write-Utf8NoBomAbs -Path "$Backend\app\services\billing\paddle_service.py" -Content $paddleService
Write-Host "8/16 app/services/billing/paddle_service.py created" -ForegroundColor Green


# ============================================================
# FILE 9 (NEW): app/schemas/billing.py
# ============================================================
$billingSchema = @'
from __future__ import annotations

from pydantic import BaseModel


class CreditPackOut(BaseModel):
    id: str
    credits: int
    price_usd: float


class BalanceResponse(BaseModel):
    credit_balance: int
    free_quota_used_today: int


class CheckoutRequest(BaseModel):
    pack_id: str


class CheckoutResponse(BaseModel):
    transaction_id: str
    checkout_url: str | None = None


class TransactionOut(BaseModel):
    id: str
    type: str
    amount: int
    balance_after: int
    description: str | None
    created_at: str


class TransactionHistoryResponse(BaseModel):
    transactions: list[TransactionOut]
'@
Write-Utf8NoBomAbs -Path "$Backend\app\schemas\billing.py" -Content $billingSchema
Write-Host "9/16 app/schemas/billing.py created" -ForegroundColor Green


# ============================================================
# FILE 10 (NEW): app/api/v1/endpoints/billing.py
# ============================================================
$billingEndpoint = @'
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.models.billing import BillingAccount, CreditTransaction
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.core.pricing.pricing_config import CREDIT_PACKS, get_credit_pack
from app.schemas.billing import (
    BalanceResponse,
    CheckoutRequest,
    CheckoutResponse,
    CreditPackOut,
    TransactionHistoryResponse,
    TransactionOut,
)
from app.services.billing import credit_service, paddle_service

router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


@router.get("/packs", response_model=list[CreditPackOut])
async def list_packs():
    return [
        {"id": p["id"], "credits": p["credits"], "price_usd": p["price_usd"]}
        for p in CREDIT_PACKS
    ]


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(BillingAccount).filter(BillingAccount.user_id == current_user.id).first()
    return BalanceResponse(
        credit_balance=account.credit_balance if account else 0,
        free_quota_used_today=account.free_quota_used_today if account else 0,
    )


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(100)
        .all()
    )
    return TransactionHistoryResponse(transactions=[
        TransactionOut(
            id=r.id,
            type=r.type,
            amount=r.amount,
            balance_after=r.balance_after,
            description=r.description,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    pack = get_credit_pack(request.pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Unknown credit pack")

    txn = paddle_service.create_transaction(
        price_id=pack["paddle_price_id"],
        customer_email=current_user.email,
        custom_data={
            "user_id": current_user.id,
            "pack_id": pack["id"],
            "credits": pack["credits"],
        },
    )
    checkout_url = (txn.get("checkout") or {}).get("url")
    return CheckoutResponse(transaction_id=txn["id"], checkout_url=checkout_url)


@router.post("/webhook/paddle")
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("Paddle-Signature", "")

    if not paddle_service.verify_webhook_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = await request.json()
    event_type = payload.get("event_type")
    data = payload.get("data", {})
    custom_data = data.get("custom_data") or {}
    user_id = custom_data.get("user_id")
    credits = custom_data.get("credits")
    paddle_txn_id = data.get("id")

    if event_type == "transaction.completed" and user_id and credits:
        credit_service.add_credits(
            db, user_id, int(credits),
            description=f"Paddle purchase ({paddle_txn_id})",
            paddle_transaction_id=paddle_txn_id,
        )

    elif event_type == "transaction.refunded" and user_id and credits:
        credit_service.deduct_credits(
            db, user_id, int(credits),
            description=f"Paddle refund ({paddle_txn_id})",
        )

    return {"status": "ok"}
'@
Write-Utf8NoBomAbs -Path "$Backend\app\api\v1\endpoints\billing.py" -Content $billingEndpoint
Write-Host "10/16 app/api/v1/endpoints/billing.py created" -ForegroundColor Green


# ============================================================
# FILE 11: app/api/v1/endpoints/__init__.py - register billing_router
# ============================================================
$initPath = "$Backend\app\api\v1\endpoints\__init__.py"
$initContent = Get-Content -Raw -Encoding UTF8 $initPath

if ($initContent -match "billing_router") {
    Write-Host "11/16 endpoints/__init__.py already has billing_router - skipped" -ForegroundColor Yellow
} elseif ($initContent -match "from \.coding import router as coding_router") {
    $initContent = $initContent -replace `
        "from \.coding import router as coding_router", `
        "from .coding import router as coding_router`r`nfrom .billing import router as billing_router"
    Write-Utf8NoBomAbs -Path $initPath -Content $initContent
    Write-Host "11/16 endpoints/__init__.py updated (billing_router added)" -ForegroundColor Green
} else {
    Write-Host "11/16 WARNING - anchor not found, add manually: from .billing import router as billing_router" -ForegroundColor Red
}


# ============================================================
# FILE 12: app/main.py - wire billing_router in
# ============================================================
$mainPath = "$Backend\app\main.py"
$mainContent = Get-Content -Raw -Encoding UTF8 $mainPath

if ($mainContent -match "billing_router") {
    Write-Host "12/16 main.py already has billing_router - skipped" -ForegroundColor Yellow
} else {
    $changed = $false
    if ($mainContent -match "(?m)^(\s*)coding_router,\s*$") {
        $indent = $Matches[1]
        $mainContent = $mainContent -replace `
            "(?m)^(\s*)coding_router,\s*$", `
            "`$1coding_router,`r`n${indent}billing_router,"
        $changed = $true
    }
    if ($mainContent -match "app\.include_router\(coding_router, prefix=settings\.API_V1_PREFIX\)") {
        $mainContent = $mainContent -replace `
            "app\.include_router\(coding_router, prefix=settings\.API_V1_PREFIX\)", `
            "app.include_router(coding_router, prefix=settings.API_V1_PREFIX)`r`napp.include_router(billing_router, prefix=settings.API_V1_PREFIX)"
        $changed = $true
    }
    if ($changed) {
        Write-Utf8NoBomAbs -Path $mainPath -Content $mainContent
        Write-Host "12/16 main.py updated (billing_router wired in)" -ForegroundColor Green
    } else {
        Write-Host "12/16 WARNING - anchors not found in main.py, wire billing_router manually" -ForegroundColor Red
    }
}


# ============================================================
# FILE 13: app/core/config/settings.py - add Paddle settings
# ============================================================
$settingsPath = "$Backend\app\core\config\settings.py"
$settingsContent = Get-Content -Raw -Encoding UTF8 $settingsPath

if ($settingsContent -match "PADDLE_API_KEY") {
    Write-Host "13/16 settings.py already has Paddle settings - skipped" -ForegroundColor Yellow
} else {
    $settingsContent = $settingsContent -replace `
        '(\s*)ELEVENLABS_API_KEY: str = ""', `
        "`$1ELEVENLABS_API_KEY: str = `"`"`r`n`r`n    # ---------- Billing (Paddle) ----------`r`n`r`n    PADDLE_API_KEY: str = `"`"`r`n`r`n    PADDLE_WEBHOOK_SECRET: str = `"`"`r`n`r`n    PADDLE_ENVIRONMENT: str = `"sandbox`"  # `"sandbox`" or `"production`""
    Write-Utf8NoBomAbs -Path $settingsPath -Content $settingsContent
    Write-Host "13/16 settings.py updated (PADDLE_API_KEY, PADDLE_WEBHOOK_SECRET, PADDLE_ENVIRONMENT)" -ForegroundColor Green
}


# ============================================================
# FILE 14: app/api/v1/endpoints/commands.py
#   (a) split "script" out of the generic "text" bucket
#   (b) charge credits / consume free quota before generation
#   (c) refund credits if generation fails
# ============================================================
$commandsPath = "$Backend\app\api\v1\endpoints\commands.py"
$commandsContent = Get-Content -Raw -Encoding UTF8 $commandsPath

if ($commandsContent -match "_billing_charged_credits") {
    Write-Host "14/16 commands.py already patched for billing - skipped" -ForegroundColor Yellow
} else {
    $patchedAny = $false

    # --- (a) split "script" out of detect_asset_type() ---
    $oldDetect = @'
def detect_asset_type(command: str) -> str:
    command = command.lower()

    research_words = [
        "research", "trends", "trending", "latest news",
        "what's happening", "current state of", "market analysis",
    ]
    if any(word in command for word in research_words):
        return "research"

    text_words = [
        "script", "caption", "seo", "blog", "article",
        "post", "description", "title", "hashtag",
    ]
    if any(word in command for word in text_words):
        return "text"
'@
    $newDetect = @'
def detect_asset_type(command: str) -> str:
    command = command.lower()

    research_words = [
        "research", "trends", "trending", "latest news",
        "what's happening", "current state of", "market analysis",
    ]
    if any(word in command for word in research_words):
        return "research"

    script_words = ["script"]
    if any(word in command for word in script_words):
        return "script"

    text_words = [
        "caption", "seo", "blog", "article",
        "post", "description", "title", "hashtag",
    ]
    if any(word in command for word in text_words):
        return "text"
'@
    if ($commandsContent.Contains($oldDetect)) {
        $commandsContent = $commandsContent.Replace($oldDetect, $newDetect)
        $patchedAny = $true
    } else {
        Write-Host "14/16 WARNING - detect_asset_type anchor not found, script-splitting NOT applied" -ForegroundColor Red
    }

    # --- (b) credit gating in /run endpoint ---
    $oldRunBlock = @'
    asset_type = detect_asset_type(request.command)

    ai_request = AIRequest(
        prompt=request.command,
        asset_type=asset_type,
        project_id=request.project_id,
        owner_id=current_user.id,
        history=history,
    )

    asset_service = AssetService(db)
'@
    $newRunBlock = @'
    asset_type = detect_asset_type(request.command)

    from app.services.billing import credit_service
    from app.core.pricing.pricing_service import is_paid, is_limited_free, credits_for_generation
    from app.core.pricing.pricing_config import LIMITED_FREE_ASSET_TYPES

    _billing_user_id = current_user.id
    _billing_charged_credits = 0

    if is_paid(asset_type):
        _billing_charged_credits = credits_for_generation(asset_type)
        try:
            credit_service.deduct_credits(
                db, _billing_user_id, _billing_charged_credits,
                description=f"{asset_type} generation",
            )
        except credit_service.InsufficientCreditsError:
            raise HTTPException(status_code=402, detail="Insufficient credits. Please buy more credits.")
    elif is_limited_free(asset_type):
        covered = credit_service.try_consume_free_quota(db, _billing_user_id, asset_type)
        if not covered:
            _billing_charged_credits = LIMITED_FREE_ASSET_TYPES[asset_type]["credit_cost_after_quota"]
            try:
                credit_service.deduct_credits(
                    db, _billing_user_id, _billing_charged_credits,
                    description=f"{asset_type} generation (free quota used)",
                )
            except credit_service.InsufficientCreditsError:
                raise HTTPException(status_code=402, detail="Insufficient credits. Please buy more credits.")

    ai_request = AIRequest(
        prompt=request.command,
        asset_type=asset_type,
        project_id=request.project_id,
        owner_id=current_user.id,
        history=history,
    )

    asset_service = AssetService(db)
'@
    if ($commandsContent.Contains($oldRunBlock)) {
        $commandsContent = $commandsContent.Replace($oldRunBlock, $newRunBlock)
        $patchedAny = $true
    } else {
        Write-Host "14/16 WARNING - /run credit-gate anchor not found, NOT applied" -ForegroundColor Red
    }

    # --- (c) credit gating in /run/stream non-text branch ---
    $oldStreamBlock = @'
            asset_type = detect_asset_type(request.command)

            # ------------------------------------------------------
            # Non-text: run normally, emit a single "done" event.
            # ------------------------------------------------------
            if asset_type != "text":
'@
    $newStreamBlock = @'
            asset_type = detect_asset_type(request.command)

            from app.services.billing import credit_service
            from app.core.pricing.pricing_service import is_paid, is_limited_free, credits_for_generation
            from app.core.pricing.pricing_config import LIMITED_FREE_ASSET_TYPES

            _billing_user_id = owner_id
            _billing_charged_credits = 0

            if is_paid(asset_type):
                _billing_charged_credits = credits_for_generation(asset_type)
                try:
                    credit_service.deduct_credits(
                        db, _billing_user_id, _billing_charged_credits,
                        description=f"{asset_type} generation",
                    )
                except credit_service.InsufficientCreditsError:
                    yield f"event: error\ndata: {json.dumps({'detail': 'Insufficient credits. Please buy more credits.'})}\n\n"
                    return
            elif is_limited_free(asset_type):
                covered = credit_service.try_consume_free_quota(db, _billing_user_id, asset_type)
                if not covered:
                    _billing_charged_credits = LIMITED_FREE_ASSET_TYPES[asset_type]["credit_cost_after_quota"]
                    try:
                        credit_service.deduct_credits(
                            db, _billing_user_id, _billing_charged_credits,
                            description=f"{asset_type} generation (free quota used)",
                        )
                    except credit_service.InsufficientCreditsError:
                        yield f"event: error\ndata: {json.dumps({'detail': 'Insufficient credits. Please buy more credits.'})}\n\n"
                        return

            # ------------------------------------------------------
            # Non-text: run normally, emit a single "done" event.
            # ------------------------------------------------------
            if asset_type != "text":
'@
    if ($commandsContent.Contains($oldStreamBlock)) {
        $commandsContent = $commandsContent.Replace($oldStreamBlock, $newStreamBlock)
        $patchedAny = $true
    } else {
        Write-Host "14/16 WARNING - /run/stream credit-gate anchor not found, NOT applied" -ForegroundColor Red
    }

    # --- (d) refund on failure, everywhere asset_service.fail(...) is called ---
    $refundPattern = '(?m)^([ ]*)asset_service\.fail\(asset, error_message=str\(e\)\)\s*$'
    if ($commandsContent -match $refundPattern) {
        $commandsContent = $commandsContent -replace $refundPattern, `
            "`$1asset_service.fail(asset, error_message=str(e))`r`n`$1if _billing_charged_credits:`r`n`$1    credit_service.refund_credits(db, _billing_user_id, _billing_charged_credits, description=f`"refund: {asset_type} generation failed`")"
        $patchedAny = $true
    }

    if ($patchedAny) {
        Write-Utf8NoBomAbs -Path $commandsPath -Content $commandsContent
        Write-Host "14/16 commands.py patched (script split + credit gating + refunds)" -ForegroundColor Green
    } else {
        Write-Host "14/16 SKIPPED - no anchors matched, commands.py left untouched" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "15/16 Reminder: new BillingAccount/CreditTransaction tables will" -ForegroundColor Cyan
Write-Host "       auto-create on next uvicorn restart (same as knowledge_chunks did)." -ForegroundColor Cyan
Write-Host ""
Write-Host "16/16 REQUIRED before payments work - add to your .env:" -ForegroundColor Cyan
Write-Host "       PADDLE_API_KEY=your_key_here" -ForegroundColor Cyan
Write-Host "       PADDLE_WEBHOOK_SECRET=your_webhook_secret_here" -ForegroundColor Cyan
Write-Host "       PADDLE_ENVIRONMENT=sandbox" -ForegroundColor Cyan
Write-Host "       (get these from paddle.com after creating a sandbox account" -ForegroundColor Cyan
Write-Host "       and creating 3 one-time Prices matching CREDIT_PACKS in" -ForegroundColor Cyan
Write-Host "       pricing_config.py, then paste those price IDs in there too)" -ForegroundColor Cyan
