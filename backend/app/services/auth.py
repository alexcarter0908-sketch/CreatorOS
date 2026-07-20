from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from app.core.config.settings import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest
from app.services.email_service import send_otp_email

# In DEBUG mode only, this fixed code always verifies successfully so
# developers can test the verification flow without needing real email
# access. It is never accepted when settings.DEBUG is False.
_DEV_BYPASS_OTP = "000000"


def _generate_and_send_otp(users: UserRepository, user) -> None:
    otp_code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.OTP_EXPIRE_MINUTES
    )
    users.set_otp(user, otp_code=otp_code, expires_at=expires_at)
    send_otp_email(user.email, otp_code)


class AuthService:
    def __init__(self, db):
        self.users = UserRepository(db)

    def register(
        self,
        request: RegisterRequest,
    ) -> str:
        """
        Creates the account (unverified) and emails a one-time code.
        Returns the email so the caller can prompt for the code next.
        """
        existing = self.users.get_by_email(request.email)

        if existing:
            raise ValueError("Email already registered.")

        password_hash = hash_password(request.password)

        user = self.users.create(
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash,
        )

        _generate_and_send_otp(self.users, user)

        return user.email

    def verify_email(
        self,
        email: str,
        otp_code: str,
    ) -> str:
        """
        Verifies the emailed one-time code from registration, marks the
        account as verified, and issues the access token so the user is
        logged in immediately after verifying.
        """
        user = self.users.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or code.")

        is_dev_bypass = settings.DEBUG and otp_code == _DEV_BYPASS_OTP

        if not is_dev_bypass:
            if not user.otp_code or not user.otp_expires_at:
                raise ValueError("No pending verification for this account.")

            if user.otp_expires_at < datetime.now(timezone.utc):
                raise ValueError("Code expired. Please request a new one.")

            if user.otp_code != otp_code:
                raise ValueError("Invalid email or code.")

        self.users.mark_email_verified(user)

        return create_access_token(subject=str(user.id))

    def resend_verification(
        self,
        email: str,
    ) -> None:
        user = self.users.get_by_email(email)

        if user is None:
            # Don't reveal whether the email exists.
            return

        if user.is_email_verified:
            return

        _generate_and_send_otp(self.users, user)

    def login(
        self,
        email: str,
        password: str,
    ) -> str:
        """
        Plain email/password login. No OTP step here -- verification
        only happens once, right after registration.
        """
        user = self.users.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password.")

        if not user.password_hash:
            raise ValueError(
                "This account uses Google Sign-In. Please continue "
                "with the 'Sign in with Google' button instead."
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password.")

        if not user.is_email_verified:
            raise ValueError(
                "Please verify your email before logging in. "
                "Check your inbox for the verification code."
            )

        return create_access_token(
            subject=str(user.id),
        )