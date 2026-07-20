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