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