from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.orm import Session

from app.database.models.billing import BillingAccount, CreditTransaction
from app.database.models.user import User
from app.core.pricing.pricing_service import limited_free_config

LOW_CREDIT_THRESHOLD = 10

logger = logging.getLogger("billing")


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


def _maybe_send_low_credit_alert(db: Session, user_id: str, new_balance: int) -> None:
    """
    Fires the moment a deduction pushes the balance under
    LOW_CREDIT_THRESHOLD. Guarded by low_credit_alert_sent so the user
    gets exactly one email per dip, not one per generation while they
    stay low - the flag resets itself once they top back up
    (see _reset_low_credit_alert).
    """
    if new_balance >= LOW_CREDIT_THRESHOLD:
        return

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.notify_low_credit_email or user.low_credit_alert_sent:
        return

    from app.services.billing.low_credit_email import send_low_credit_email

    try:
        send_low_credit_email(user.email, user.full_name, new_balance)
    except Exception:
        # Email delivery must never break a generation request.
        logger.exception("Failed to send low-credit email to %s", user.email)
        return

    user.low_credit_alert_sent = True
    db.add(user)
    db.commit()


def _reset_low_credit_alert(db: Session, user_id: str, new_balance: int) -> None:
    if new_balance < LOW_CREDIT_THRESHOLD:
        return
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.low_credit_alert_sent:
        user.low_credit_alert_sent = False
        db.add(user)
        db.commit()


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
    _reset_low_credit_alert(db, user_id, account.credit_balance)
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
    _maybe_send_low_credit_alert(db, user_id, account.credit_balance)
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
    _reset_low_credit_alert(db, user_id, account.credit_balance)
    return account.credit_balance


def try_consume_free_quota(db: Session, user_id: str, asset_type: str) -> bool:
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
