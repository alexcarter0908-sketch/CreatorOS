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

# Below this many credits we nudge the user to top up (not a hard
# limit - just a UI hint on the billing page). Roughly "less than
# enough for a couple of cheap generations".
LOW_BALANCE_THRESHOLD = 100


@router.get("/packs", response_model=list[CreditPackOut])
async def list_packs():
    return [
        {
            "id": p["id"],
            "credits": p["credits"],
            "price_usd": p["price_usd"],
            "popular": p.get("popular", False),
        }
        for p in CREDIT_PACKS
    ]


@router.get("/balance", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(BillingAccount).filter(BillingAccount.user_id == current_user.id).first()
    balance = account.credit_balance if account else 0
    return BalanceResponse(
        credit_balance=balance,
        free_quota_used_today=account.free_quota_used_today if account else 0,
        low_balance=balance < LOW_BALANCE_THRESHOLD,
    )


@router.get("/history", response_model=TransactionHistoryResponse)
async def get_history(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    safe_limit = max(1, min(limit, 100))
    safe_offset = max(0, offset)

    rows = (
        db.query(CreditTransaction)
        .filter(CreditTransaction.user_id == current_user.id)
        .order_by(CreditTransaction.created_at.desc())
        .offset(safe_offset)
        .limit(safe_limit)
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
        if not credit_service.is_paddle_event_processed(db, paddle_txn_id, "purchase"):
            credit_service.add_credits(
                db, user_id, int(credits),
                description=f"Paddle purchase ({paddle_txn_id})",
                paddle_transaction_id=paddle_txn_id,
            )

    elif event_type == "transaction.refunded" and user_id and credits:
        if not credit_service.is_paddle_event_processed(db, paddle_txn_id, "refund"):
            credit_service.deduct_credits(
                db, user_id, int(credits),
                description=f"Paddle refund ({paddle_txn_id})",
            )

    return {"status": "ok"}