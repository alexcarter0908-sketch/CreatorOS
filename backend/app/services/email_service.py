from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

from app.core.config.settings import settings


def send_otp_email(to_email: str, otp_code: str) -> None:
    """
    Sends a one-time-password code to the user's email via SMTP.
    Raises RuntimeError if SMTP is not configured or sending fails,
    so the caller can surface a clear error instead of silently
    pretending the email went out.
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP is not configured (SMTP_USER/SMTP_PASSWORD missing)."
        )

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

    subject = "Your CreatorOS verification code"
    body = (
        f"Your CreatorOS verification code is: {otp_code}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n"
        "If you did not request this, you can safely ignore this email."
    )

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(from_email, [to_email], message.as_string())
    except Exception as e:
        raise RuntimeError(f"Failed to send OTP email: {e}") from e