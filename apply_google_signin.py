"""
apply_google_signin.py
=======================

Adds a complete "Sign in with Google" (login) feature to CreatorOS.
This is SEPARATE from the existing YouTube-publish OAuth (which stays
untouched) - it lets a user log into their CreatorOS account itself
using their Google account.

WHERE TO PUT THIS FILE
-----------------------
Place this file directly inside your project's MAIN folder, i.e.
right next to the "backend" and "frontend" folders:

    CreatorOS-main/
      backend/
      frontend/
      apply_google_signin.py   <-- here

HOW TO RUN
----------
Open PowerShell in that CreatorOS-main folder and run:

    .\\backend\\venv\\Scripts\\python.exe apply_google_signin.py

(If your venv folder is named ".venv" instead of "venv", use
".\\backend\\.venv\\Scripts\\python.exe apply_google_signin.py" instead.)

The script edits/creates the necessary backend + frontend files,
then automatically runs the Alembic migration.

ONE MANUAL STEP YOU MUST DO YOURSELF (Google Cloud Console)
-------------------------------------------------------------
Your existing Google OAuth Client (the one already used for YouTube
publishing) needs ONE more "Authorized redirect URI" added to it:

    http://localhost:8000/api/v1/auth/google/callback

Steps:
  1. Go to https://console.cloud.google.com/apis/credentials
  2. Open your existing OAuth 2.0 Client ID (same one used for YouTube)
  3. Under "Authorized redirect URIs", click "+ ADD URI"
  4. Paste: http://localhost:8000/api/v1/auth/google/callback
  5. Save

Without this step, Google will show "redirect_uri_mismatch" when you
click "Sign in with Google".
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"

results: list[tuple[str, bool, str]] = []


def ok(step: str, msg: str = "") -> None:
    results.append((step, True, msg))
    print(f"[OK]   {step}" + (f" - {msg}" if msg else ""))


def fail(step: str, msg: str) -> None:
    results.append((step, False, msg))
    print(f"[FAIL] {step} - {msg}")


def safe_replace(path: Path, old: str, new: str, step: str) -> bool:
    if not path.exists():
        fail(step, f"file not found: {path}")
        return False
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        fail(step, f"expected exact match once, found {count} times in {path.name} - no changes made")
        return False
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
    ok(step)
    return True


def safe_append(path: Path, addition: str, step: str, unless_contains: str | None = None) -> bool:
    if not path.exists():
        fail(step, f"file not found: {path}")
        return False
    text = path.read_text(encoding="utf-8")
    if unless_contains and unless_contains in text:
        ok(step, "already applied, skipped")
        return True
    if not text.endswith("\n"):
        text += "\n"
    text += addition
    path.write_text(text, encoding="utf-8")
    ok(step)
    return True


def write_file(path: Path, content: str, step: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    ok(step)


# ======================================================================
# 1. backend/app/database/models/user.py
#    - make password_hash nullable (Google-only accounts have no password)
#    - add google_id column
# ======================================================================

safe_replace(
    BACKEND / "app/database/models/user.py",
    old=(
        '    password_hash: Mapped[str] = mapped_column(\n'
        '        String(255),\n'
        '        nullable=False,\n'
        '    )\n'
    ),
    new=(
        '    password_hash: Mapped[str | None] = mapped_column(\n'
        '        String(255),\n'
        '        nullable=True,\n'
        '    )\n'
        '\n'
        '    google_id: Mapped[str | None] = mapped_column(\n'
        '        String(255),\n'
        '        unique=True,\n'
        '        index=True,\n'
        '        nullable=True,\n'
        '    )\n'
    ),
    step="1. user.py: password_hash nullable + google_id column",
)

# ======================================================================
# 2. backend/app/repositories/user_repository.py
#    - add get_by_google_id + create_google_user
# ======================================================================

safe_append(
    BACKEND / "app/repositories/user_repository.py",
    unless_contains="get_by_google_id",
    step="2. user_repository.py: add Google lookup/create methods",
    addition=(
        '\n'
        '    def get_by_google_id(\n'
        '        self,\n'
        '        google_id: str,\n'
        '    ) -> User | None:\n'
        '        return (\n'
        '            self.db.query(User)\n'
        '            .filter(User.google_id == google_id)\n'
        '            .first()\n'
        '        )\n'
        '\n'
        '    def create_google_user(\n'
        '        self,\n'
        '        *,\n'
        '        full_name: str,\n'
        '        email: str,\n'
        '        google_id: str,\n'
        '        avatar_url: str | None = None,\n'
        '    ) -> User:\n'
        '        user = User(\n'
        '            full_name=full_name,\n'
        '            email=email.lower(),\n'
        '            password_hash=None,\n'
        '            google_id=google_id,\n'
        '            avatar_url=avatar_url,\n'
        '        )\n'
        '\n'
        '        self.db.add(user)\n'
        '        self.db.commit()\n'
        '        self.db.refresh(user)\n'
        '\n'
        '        return user\n'
    ),
)

# ======================================================================
# 3. backend/app/services/auth.py
#    - guard against password login on a Google-only account
# ======================================================================

safe_replace(
    BACKEND / "app/services/auth.py",
    old=(
        '        if not verify_password(\n'
        '            password,\n'
        '            user.password_hash,\n'
        '        ):\n'
        '            raise ValueError("Invalid email or password.")\n'
    ),
    new=(
        '        if not user.password_hash:\n'
        '            raise ValueError(\n'
        '                "This account uses Google Sign-In. Please continue "\n'
        '                "with the \'Sign in with Google\' button instead."\n'
        '            )\n'
        '\n'
        '        if not verify_password(\n'
        '            password,\n'
        '            user.password_hash,\n'
        '        ):\n'
        '            raise ValueError("Invalid email or password.")\n'
    ),
    step="3. auth.py (service): guard password-login for Google-only accounts",
)

# ======================================================================
# 4. backend/app/core/config/settings.py
#    - add GOOGLE_LOGIN_REDIRECT_URI
# ======================================================================

safe_replace(
    BACKEND / "app/core/config/settings.py",
    old=(
        '    GOOGLE_CLIENT_ID: str = ""\n'
        '    GOOGLE_CLIENT_SECRET: str = ""\n'
        '    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/publish/youtube/callback"\n'
    ),
    new=(
        '    GOOGLE_CLIENT_ID: str = ""\n'
        '    GOOGLE_CLIENT_SECRET: str = ""\n'
        '    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/publish/youtube/callback"\n'
        '    GOOGLE_LOGIN_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"\n'
    ),
    step="4. settings.py: add GOOGLE_LOGIN_REDIRECT_URI",
)

# ======================================================================
# 5. backend/app/services/auth_google_service.py  (NEW FILE)
# ======================================================================

write_file(
    BACKEND / "app/services/auth_google_service.py",
    '''from __future__ import annotations

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
''',
    step="5. auth_google_service.py created",
)

# ======================================================================
# 6. backend/app/api/v1/endpoints/auth.py
#    - append the two new routes (safe: pure append, nothing existing touched)
# ======================================================================

safe_append(
    BACKEND / "app/api/v1/endpoints/auth.py",
    unless_contains="google/login",
    step="6. auth.py (endpoints): add /google/login + /google/callback routes",
    addition='''

from fastapi.responses import RedirectResponse

from app.core.config.settings import settings
from app.services.auth_google_service import (
    GoogleLoginError,
    build_login_url,
    handle_google_callback,
)


@router.get("/google/login")
def google_login():
    try:
        url = build_login_url()
    except GoogleLoginError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return RedirectResponse(url)


@router.get("/google/callback")
def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    try:
        token = handle_google_callback(db, code=code, state=state)
    except GoogleLoginError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Google sign-in failed: {exc}")

    return RedirectResponse(f"{settings.FRONTEND_URL}/auth/callback?token={token}")
''',
)

# ======================================================================
# 7. frontend/features/auth/components/LoginForm.tsx
#    - point the Google button at the real backend endpoint
# ======================================================================

safe_replace(
    FRONTEND / "features/auth/components/LoginForm.tsx",
    old=(
        '  function handleGoogleLogin() {\n'
        '    window.location.href = "/api/auth/google";\n'
        '  }\n'
    ),
    new=(
        '  function handleGoogleLogin() {\n'
        '    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";\n'
        '    window.location.href = `${apiBase}/api/v1/auth/google/login`;\n'
        '  }\n'
    ),
    step="7. LoginForm.tsx: Google button now points at real backend endpoint",
)

# ======================================================================
# 8. frontend/app/auth/callback/page.tsx  (NEW FILE)
#    - receives the token from the backend redirect, stores it, and
#      forwards the user into the app
# ======================================================================

write_file(
    FRONTEND / "app/auth/callback/page.tsx",
    '''"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ACCESS_TOKEN_KEY } from "@/lib/api/client";

function CallbackInner() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get("token");

    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
      router.replace("/command-center");
    } else {
      router.replace("/login");
    }
  }, [searchParams, router]);

  return (
    <div className="flex min-h-screen items-center justify-center text-slate-400">
      Signing you in...
    </div>
  );
}

export default function GoogleAuthCallbackPage() {
  return (
    <Suspense fallback={null}>
      <CallbackInner />
    </Suspense>
  );
}
''',
    step="8. app/auth/callback/page.tsx created",
)

# ======================================================================
# 9. Alembic migration
# ======================================================================

print("\\nRunning Alembic migration...\\n")

try:
    subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", "add google sign-in support"],
        cwd=BACKEND,
        check=True,
    )
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND,
        check=True,
    )
    ok("9. Alembic migration generated + applied")
except subprocess.CalledProcessError as exc:
    fail("9. Alembic migration", f"exit code {exc.returncode} - check the output above")

# ======================================================================
# Summary
# ======================================================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for step, success, msg in results:
    print(f"{'OK  ' if success else 'FAIL'} - {step}")

failed = [r for r in results if not r[1]]
if failed:
    print(f"\n{len(failed)} step(s) failed - see [FAIL] lines above. Nothing else was touched.")
else:
    print("\nAll steps applied successfully.")
    print("\nREMINDER: add this redirect URI in Google Cloud Console")
    print("(same OAuth Client you already use for YouTube):")
    print("  http://localhost:8000/api/v1/auth/google/callback")
    print("\nThen restart your backend (uvicorn) and frontend (npm run dev),")
    print("and try 'Sign in with Google' again.")
