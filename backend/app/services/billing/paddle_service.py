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