from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from app.core.config.settings import settings


def send_low_credit_email(to_email: str, user_name: str, balance: int) -> None:
    """
    Reuses the same SMTP settings/pattern as email_service.py, kept in
    its own module so it can never interfere with the OTP login flow.
    Raises if SMTP is not configured, same contract as email_service.py,
    so the caller decides how to handle that (billing swallows it - see
    credit_service.py - so a missing SMTP config never breaks a
    generation request).
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP is not configured (SMTP_USER/SMTP_PASSWORD missing).")

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

    subject = "Your CreatorOS credit balance is running low"
    body = (
        f"Hi {user_name or 'there'},\n\n"
        f"Your CreatorOS credit balance is down to {balance} credits.\n"
        "Top up from Settings > Credits & Usage so your pipelines don't get interrupted.\n\n"
        "You'll get this reminder again the next time your balance dips low after a top-up."
    )

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(from_email, [to_email], message.as_string())
