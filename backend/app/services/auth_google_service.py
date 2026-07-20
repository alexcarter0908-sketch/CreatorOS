from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import requests
from google_auth_oauthlib.flow import Flow
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.security import create_access_token
from app.repositories.user_repository import UserRepository

if settings.DEBUG:
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

LOGIN_SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

STATE_ALGORITHM = settings.JWT_ALGORITHM


class GoogleLoginError(RuntimeError):
    pass


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_LOGIN_REDIRECT_URI],
        }
    }


def build_login_url() -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise GoogleLoginError(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not configured in .env"
        )

    flow = Flow.from_client_config(
        _client_config(),
        scopes=LOGIN_SCOPES,
        redirect_uri=settings.GOOGLE_LOGIN_REDIRECT_URI,
    )

    # PKCE code_verifier is generated inside flow.authorization_url();
    # it must be persisted (inside the signed state JWT) so the callback
    # can hand it to a *new* Flow instance during token exchange.
    state = jwt.encode(
        {
            "cv": flow.code_verifier,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        settings.JWT_SECRET_KEY,
        algorithm=STATE_ALGORITHM,
    )

    auth_url, _ = flow.authorization_url(
        access_type="online",
        include_granted_scopes="true",
        prompt="select_account",
        state=state,
    )

    return auth_url


def _code_verifier_from_state(state: str) -> str | None:
    payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[STATE_ALGORITHM])
    return payload.get("cv")


def handle_google_callback(db: Session, *, code: str, state: str) -> str:
    """
    Exchanges the OAuth code for tokens, fetches the Google profile,
    finds-or-creates the matching CreatorOS user, and returns a
    CreatorOS access token (JWT) for that user.
    """
    flow = Flow.from_client_config(
        _client_config(),
        scopes=LOGIN_SCOPES,
        redirect_uri=settings.GOOGLE_LOGIN_REDIRECT_URI,
    )
    flow.code_verifier = _code_verifier_from_state(state)
    flow.fetch_token(code=code)
    creds = flow.credentials

    resp = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {creds.token}"},
        timeout=10,
    )
    resp.raise_for_status()
    profile = resp.json()

    google_id = profile.get("sub")
    email = profile.get("email")
    full_name = profile.get("name") or (email.split("@")[0] if email else "Google User")
    avatar_url = profile.get("picture")

    if not google_id or not email:
        raise GoogleLoginError("Google did not return the expected profile fields.")

    users = UserRepository(db)

    user = users.get_by_google_id(google_id)

    if user is None:
        # Not linked yet - if an account with this email already exists
        # (e.g. they registered with email/password before), link it.
        existing = users.get_by_email(email)
        if existing is not None:
            existing.google_id = google_id
            if not existing.avatar_url and avatar_url:
                existing.avatar_url = avatar_url
            user = users.update(existing)
        else:
            user = users.create_google_user(
                full_name=full_name,
                email=email,
                google_id=google_id,
                avatar_url=avatar_url,
            )

    return create_access_token(subject=str(user.id))
