from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.pricing.pricing_service import limited_free_config
from app.database.models.billing import BillingAccount, CreditTransaction
from app.database.models.user import User

LOW_CREDIT_THRESHOLD = 10

logger = logging.getLogger("billing")


class InsufficientCreditsError(Exception):
    pass


def _local_today() -> str:
    """Same local-time convention used for automation scheduling
    (DEFAULT_TIMEZONE_OFFSET_HOURS), so the free daily quota resets at the
    same day-boundary users see elsewhere in the product instead of the
    server/UTC day."""
    local_now = datetime.now(timezone.utc) + timedelta(
        hours=settings.DEFAULT_TIMEZONE_OFFSET_HOURS
    )
    return local_now.date().isoformat()


def _get_or_create_account(db: Session, user_id: str, *, lock: bool = False) -> BillingAccount:
    """Fetch the user's billing account, optionally taking a row-level
    lock (SELECT ... FOR UPDATE) so concurrent requests for the same user
    (double-clicks, multiple tabs, retried requests) serialize instead of
    racing each other on the same balance. Every function that *mutates*
    the balance must pass lock=True; read-only lookups should not.
    """
    query = db.query(BillingAccount).filter(BillingAccount.user_id == user_id)
    if lock:
        query = query.with_for_update()
    account = query.first()

    if account is not None:
        return account

    # First-time account creation is itself a race: two concurrent
    # requests can both miss the row above and both try to insert. The
    # unique constraint on user_id lets only one succeed - catch that
    # instead of letting it surface as an unhandled 500.
    account = BillingAccount(user_id=user_id, credit_balance=0)
    db.add(account)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        query = db.query(BillingAccount).filter(BillingAccount.user_id == user_id)
        if lock:
            query = query.with_for_update()
        account = query.first()
        if account is None:
            raise

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
    if amount <= 0:
        raise ValueError("add_credits amount must be positive.")

    account = _get_or_create_account(db, user_id, lock=True)
    account.credit_balance += amount
    db.add(CreditTransaction(
        user_id=user_id,
        type="purchase" if paddle_transaction_id else "bonus",
        amount=amount,
        balance_after=account.credit_balance,
        description=description,
        paddle_transaction_id=paddle_transaction_id,
    ))

    if paddle_transaction_id:
        # A retried/duplicate webhook delivery for a transaction we've
        # already credited hits the unique constraint on
        # paddle_transaction_id - treat that as "already processed"
        # instead of double-crediting the user or raising a 500.
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            logger.info(
                "Duplicate Paddle webhook for transaction %s ignored (already credited).",
                paddle_transaction_id,
            )
            return get_balance(db, user_id)
    else:
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
    if amount <= 0:
        raise ValueError("deduct_credits amount must be positive.")

    # lock=True holds a row lock on this user's billing account for the
    # rest of this transaction, so a second concurrent deduction has to
    # wait until this one commits (or rolls back) before it can read the
    # balance - closing the double-spend window that plain read-then-write
    # leaves open.
    account = _get_or_create_account(db, user_id, lock=True)

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
    if amount <= 0:
        raise ValueError("refund_credits amount must be positive.")

    account = _get_or_create_account(db, user_id, lock=True)
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

    account = _get_or_create_account(db, user_id, lock=True)
    today = _local_today()

    if account.free_quota_date != today:
        account.free_quota_date = today
        account.free_quota_used_today = 0

    if account.free_quota_used_today < config["daily_free_quota"]:
        account.free_quota_used_today += 1
        db.commit()
        return True

    # Nothing to spend, but a day-rollover reset above may still need
    # persisting, and we must release the row lock either way.
    db.commit()
    return False
