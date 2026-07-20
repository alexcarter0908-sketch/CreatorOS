from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request as GoogleAuthRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.database.models import Asset
from app.repositories.publish_account_repository import PublishAccountRepository

# Allow http (non-TLS) redirect during local development.
if settings.DEBUG:
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

STATE_ALGORITHM = settings.JWT_ALGORITHM


class YouTubeNotConnectedError(RuntimeError):
    pass


def _client_config() -> dict:
    return {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }


def build_authorization_url(owner_id: str) -> str:
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise YouTubeNotConnectedError(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not configured in .env"
        )

    flow = Flow.from_client_config(
        _client_config(),
        scopes=YOUTUBE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        autogenerate_code_verifier=True,
    )

    dummy_state = "pending"
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent select_account",
        state=dummy_state,
    )

    state = jwt.encode(
        {
            "sub": owner_id,
            "cv": flow.code_verifier,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        settings.JWT_SECRET_KEY,
        algorithm=STATE_ALGORITHM,
    )

    auth_url = auth_url.replace(f"state={dummy_state}", f"state={state}")

    return auth_url


def owner_id_from_state(state: str) -> str:
    payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[STATE_ALGORITHM])
    owner_id = payload.get("sub")
    if not owner_id:
        raise YouTubeNotConnectedError("Invalid OAuth state.")
    return owner_id


def _code_verifier_from_state(state: str):
    payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[STATE_ALGORITHM])
    return payload.get("cv")


def exchange_code_for_tokens(db: Session, owner_id: str, code: str, state: str) -> None:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=YOUTUBE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    flow.code_verifier = _code_verifier_from_state(state)

    flow.fetch_token(code=code)
    creds = flow.credentials

    youtube = build("youtube", "v3", credentials=creds)
    channels = youtube.channels().list(part="snippet", mine=True).execute()

    channel_title = None
    channel_id = None
    items = channels.get("items", [])
    if items:
        channel_id = items[0].get("id")
        channel_title = items[0].get("snippet", {}).get("title")

    repo = PublishAccountRepository(db)
    repo.upsert_by_external_id(
        owner_id=owner_id,
        platform="youtube",
        external_account_id=channel_id or "",
        access_token=creds.token,
        refresh_token=creds.refresh_token,
        token_expiry=(
            creds.expiry.replace(tzinfo=timezone.utc) if creds.expiry else None
        ),
        account_label=channel_title,
        scopes=" ".join(creds.scopes or YOUTUBE_SCOPES),
    )


def _load_credentials(db: Session, owner_id: str) -> Credentials:
    repo = PublishAccountRepository(db)
    account = repo.get_by_owner_and_platform(owner_id, "youtube")

    if account is None or not account.refresh_token:
        raise YouTubeNotConnectedError(
            "YouTube account not connected. Call GET /publish/youtube/connect first."
        )

    creds = Credentials(
        token=account.access_token,
        refresh_token=account.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=(account.scopes or "").split() or YOUTUBE_SCOPES,
    )

    if not creds.valid:
        creds.refresh(GoogleAuthRequest())
        repo.upsert(
            owner_id=owner_id,
            platform="youtube",
            access_token=creds.token,
            refresh_token=creds.refresh_token or account.refresh_token,
            token_expiry=(
                creds.expiry.replace(tzinfo=timezone.utc) if creds.expiry else None
            ),
        )

    return creds


def upload_video(
    db: Session,
    *,
    owner_id: str,
    asset: Asset,
    title: str,
    description: str = "",
    tags: list[str] | None = None,
    privacy_status: str = "public",
) -> dict:
    if not asset.storage_path:
        raise ValueError("Asset has no local file to upload.")

    file_path = Path(asset.storage_path)
    if not file_path.exists():
        raise ValueError(f"File not found on disk: {file_path}")

    is_short = bool(
        asset.duration_seconds
        and asset.duration_seconds <= 60
        and asset.height
        and asset.width
        and asset.height >= asset.width
    )

    final_title = title
    final_description = description

    if (
        is_short
        and "#shorts" not in final_title.lower()
        and "#shorts" not in final_description.lower()
    ):
        final_description = f"{final_description}\n\n#Shorts".strip()

    creds = _load_credentials(db, owner_id, account_id)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": final_title[:100],
            "description": final_description[:5000],
            "tags": (tags or [])[:500],
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(file_path),
        chunksize=-1,
        resumable=True,
        mimetype="video/mp4",
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        _status_obj, response = request.next_chunk()

    video_id = response.get("id")

    return {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "is_short": is_short,
    }


