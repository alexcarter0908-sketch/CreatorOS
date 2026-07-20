# --- Ensure .NET's CurrentDirectory matches PowerShell's actual location ---
[System.Environment]::CurrentDirectory = (Get-Location).Path

# ============================================================
# CreatorOS - YouTube Publishing + Download endpoint setup
# Run this once from the backend folder:
#   . .\setup_youtube_publish.ps1
# ============================================================

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $fullPath = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    } else {
        Join-Path (Get-Location).Path $Path
    }
    $dir = Split-Path -Parent $fullPath
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    [System.IO.File]::WriteAllText($fullPath, $Content, (New-Object System.Text.UTF8Encoding($false)))
}

Write-Host "=== 1) Creating PublishAccount model ==="
$publishAccountModel = @'
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.mixins import BaseModelMixin


class PublishAccount(
    Base,
    BaseModelMixin,
):
    """
    Stores OAuth credentials for a connected social platform account
    (YouTube, Instagram, TikTok, Facebook, etc.) belonging to a user.
    """

    __tablename__ = "publish_accounts"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    account_label: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    external_account_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    token_expiry: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    scopes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    extra_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    owner = relationship("User")
'@
Write-Utf8NoBom -Path ".\app\database\models\publish_account.py" -Content $publishAccountModel


Write-Host "=== 2) Updating models\__init__.py ==="
$modelsInit = @'
from app.database.models.user import User
from app.database.models.project import Project
from app.database.models.asset import Asset
from app.database.models.workflow import Workflow, WorkflowStep
from app.database.models.auto_target import AutoTarget
from app.database.models.publish_account import PublishAccount

__all__ = [
    "User",
    "Project",
    "Asset",
    "Workflow",
    "WorkflowStep",
    "AutoTarget",
    "PublishAccount",
]
'@
Write-Utf8NoBom -Path ".\app\database\models\__init__.py" -Content $modelsInit


Write-Host "=== 3) Creating PublishAccountRepository ==="
$publishRepo = @'
from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.database.models import PublishAccount


class PublishAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_owner_and_platform(
        self,
        owner_id: str,
        platform: str,
    ) -> PublishAccount | None:
        return (
            self.db.query(PublishAccount)
            .filter(
                PublishAccount.owner_id == owner_id,
                PublishAccount.platform == platform,
                PublishAccount.is_active.is_(True),
            )
            .first()
        )

    def upsert(
        self,
        *,
        owner_id: str,
        platform: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        token_expiry: datetime | None = None,
        account_label: str | None = None,
        external_account_id: str | None = None,
        scopes: str | None = None,
        extra_metadata: dict | None = None,
    ) -> PublishAccount:
        account = self.get_by_owner_and_platform(owner_id, platform)

        if account is None:
            account = PublishAccount(
                owner_id=owner_id,
                platform=platform,
            )

        if access_token is not None:
            account.access_token = access_token
        if refresh_token is not None:
            account.refresh_token = refresh_token
        if token_expiry is not None:
            account.token_expiry = token_expiry
        if account_label is not None:
            account.account_label = account_label
        if external_account_id is not None:
            account.external_account_id = external_account_id
        if scopes is not None:
            account.scopes = scopes
        if extra_metadata is not None:
            account.extra_metadata = extra_metadata

        account.is_active = True

        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        return account

    def deactivate(self, account: PublishAccount) -> None:
        account.is_active = False
        self.db.add(account)
        self.db.commit()
'@
Write-Utf8NoBom -Path ".\app\repositories\publish_account_repository.py" -Content $publishRepo


Write-Host "=== 4) Creating publishing service package ==="
New-Item -ItemType Directory -Force -Path ".\app\services\publishing" | Out-Null
Write-Utf8NoBom -Path ".\app\services\publishing\__init__.py" -Content ""

$youtubeService = @'
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

    state = jwt.encode(
        {
            "sub": owner_id,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
        settings.JWT_SECRET_KEY,
        algorithm=STATE_ALGORITHM,
    )

    flow = Flow.from_client_config(
        _client_config(),
        scopes=YOUTUBE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )

    return auth_url


def owner_id_from_state(state: str) -> str:
    payload = jwt.decode(state, settings.JWT_SECRET_KEY, algorithms=[STATE_ALGORITHM])
    owner_id = payload.get("sub")
    if not owner_id:
        raise YouTubeNotConnectedError("Invalid OAuth state.")
    return owner_id


def exchange_code_for_tokens(db: Session, owner_id: str, code: str) -> None:
    flow = Flow.from_client_config(
        _client_config(),
        scopes=YOUTUBE_SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )

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
    repo.upsert(
        owner_id=owner_id,
        platform="youtube",
        access_token=creds.token,
        refresh_token=creds.refresh_token,
        token_expiry=(
            creds.expiry.replace(tzinfo=timezone.utc) if creds.expiry else None
        ),
        account_label=channel_title,
        external_account_id=channel_id,
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

    creds = _load_credentials(db, owner_id)
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
'@
Write-Utf8NoBom -Path ".\app\services\publishing\youtube_service.py" -Content $youtubeService


Write-Host "=== 5) Creating publish endpoints (connect / callback / upload / download) ==="
$publishEndpoint = @'
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.models import User
from app.database.session.database import get_db
from app.dependencies.auth import get_current_user
from app.repositories.asset_repository import AssetRepository
from app.services.publishing import youtube_service
from app.services.publishing.youtube_service import YouTubeNotConnectedError

router = APIRouter(
    prefix="/publish",
    tags=["Publishing"],
)


class YouTubeUploadRequest(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = "public"


@router.get("/youtube/connect")
def youtube_connect(
    current_user: User = Depends(get_current_user),
):
    try:
        url = youtube_service.build_authorization_url(current_user.id)
    except YouTubeNotConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {"authorization_url": url}


@router.get("/youtube/callback")
def youtube_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db),
):
    try:
        owner_id = youtube_service.owner_id_from_state(state)
        youtube_service.exchange_code_for_tokens(db, owner_id, code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return {"message": "YouTube account connected successfully. You can close this tab."}


@router.post("/youtube/upload/{asset_id}")
def youtube_upload(
    asset_id: str,
    request: YouTubeUploadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = AssetRepository(db).get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if asset.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Asset is not ready (status={asset.status}).",
        )

    try:
        result = youtube_service.upload_video(
            db,
            owner_id=current_user.id,
            asset=asset,
            title=request.title,
            description=request.description,
            tags=request.tags,
            privacy_status=request.privacy_status,
        )
    except YouTubeNotConnectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    return result


@router.get("/download/{asset_id}")
def download_asset(
    asset_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    asset = AssetRepository(db).get_by_id(asset_id)

    if asset is None or asset.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found.",
        )

    if not asset.storage_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Asset has no downloadable file.",
        )

    file_path = Path(asset.storage_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File missing on disk.",
        )

    ext = file_path.suffix or ".mp4"
    download_name = f"creatoros_{asset.id}{ext}"

    return FileResponse(
        path=str(file_path),
        media_type=asset.mime_type or "application/octet-stream",
        filename=download_name,
    )
'@
Write-Utf8NoBom -Path ".\app\api\v1\endpoints\publish.py" -Content $publishEndpoint


Write-Host "=== 6) Registering publish_router in endpoints\__init__.py ==="
$endpointsInitPath = ".\app\api\v1\endpoints\__init__.py"
$endpointsInit = Get-Content $endpointsInitPath -Raw

if ($endpointsInit -notmatch "publish_router") {
    $endpointsInit = $endpointsInit -replace `
        '(from \.assembly import router as assembly_router)', `
        "`$1`r`nfrom .publish import router as publish_router"

    $endpointsInit = $endpointsInit -replace `
        '("assembly_router",)', `
        "`$1`r`n    `"publish_router`","

    Write-Utf8NoBom -Path $endpointsInitPath -Content $endpointsInit
    Write-Host "Patched endpoints/__init__.py"
} else {
    Write-Host "endpoints/__init__.py already patched"
}


Write-Host "=== 7) Registering publish_router in main.py ==="
$mainPath = ".\app\main.py"
$mainContent = Get-Content $mainPath -Raw

if ($mainContent -notmatch "publish_router") {
    $mainContent = $mainContent -replace `
        '(assembly_router,\r?\n\))', `
        "assembly_router,`r`n    publish_router,`r`n)"

    $mainContent = $mainContent -replace `
        '(app\.include_router\(assembly_router, prefix=settings\.API_V1_PREFIX\))', `
        "`$1`r`napp.include_router(publish_router, prefix=settings.API_V1_PREFIX)"

    Write-Utf8NoBom -Path $mainPath -Content $mainContent
    Write-Host "Patched main.py"
} else {
    Write-Host "main.py already patched"
}


Write-Host "=== 8) Adding Google OAuth settings ==="
$settingsPath = ".\app\core\config\settings.py"
$settingsContent = Get-Content $settingsPath -Raw

if ($settingsContent -notmatch "GOOGLE_CLIENT_ID") {
    $settingsContent = $settingsContent -replace `
        '(XAI_API_KEY: str = "")', `
        "`$1`r`n`r`n    # ---------- Publishing / Social OAuth ----------`r`n`r`n    GOOGLE_CLIENT_ID: str = `"`"`r`n    GOOGLE_CLIENT_SECRET: str = `"`"`r`n    GOOGLE_REDIRECT_URI: str = `"http://localhost:8000/api/v1/publish/youtube/callback`""

    Write-Utf8NoBom -Path $settingsPath -Content $settingsContent
    Write-Host "Patched settings.py"
} else {
    Write-Host "settings.py already patched"
}


Write-Host "=== 9) Verifying all new/changed files are valid Python ==="
$filesToCheck = @(
    ".\app\database\models\publish_account.py",
    ".\app\database\models\__init__.py",
    ".\app\repositories\publish_account_repository.py",
    ".\app\services\publishing\youtube_service.py",
    ".\app\api\v1\endpoints\publish.py",
    ".\app\api\v1\endpoints\__init__.py",
    ".\app\main.py",
    ".\app\core\config\settings.py"
)

foreach ($f in $filesToCheck) {
    $result = python -c "import ast; ast.parse(open(r'$f', encoding='utf-8-sig').read())" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SYNTAX ERROR in $f :" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
    } else {
        Write-Host "OK: $f"
    }
}

Write-Host ""
Write-Host "=== DONE ==="
Write-Host "Next steps:"
Write-Host "1) pip install google-auth-oauthlib google-api-python-client"
Write-Host "2) Add to your .env: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET"
Write-Host "3) Restart uvicorn"
Write-Host "4) GET /api/v1/publish/youtube/connect (with auth token) to get the authorization_url"