function Write-Utf8NoBomAbs {
    param([string]$Path, [string]$Content)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding($false)))
}

$Backend = "C:\Users\hp\Downloads\CreatorOS\CreatorOS-main\backend"

# ============================================================
# FILE 1 (NEW): docker/code-runner/Dockerfile
# Single sandbox image with Python3, Node.js, Bash - non-root user
# ============================================================
$dockerfile = @'
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        nodejs \
        npm \
        bash \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 10001 -s /usr/sbin/nologin sandbox

WORKDIR /sandbox
USER sandbox

CMD ["bash"]
'@
Write-Utf8NoBomAbs -Path "$Backend\docker\code-runner\Dockerfile" -Content $dockerfile
Write-Host "1/6 docker/code-runner/Dockerfile created" -ForegroundColor Green


# ============================================================
# FILE 2 (NEW): app/services/coding/__init__.py
# ============================================================
Write-Utf8NoBomAbs -Path "$Backend\app\services\coding\__init__.py" -Content ""
Write-Host "2/6 app/services/coding/__init__.py created" -ForegroundColor Green


# ============================================================
# FILE 3 (NEW): app/services/coding/code_executor.py
# Runs untrusted code inside an isolated, network-disabled,
# resource-limited Docker container via the docker CLI.
# ============================================================
$codeExecutor = @'
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import dataclass

_RUNNER_IMAGE = "creatoros-code-runner:latest"
_TIMEOUT_SECONDS = 10
_MEM_LIMIT = "256m"
_CPUS = "1"
_PIDS_LIMIT = "64"
_MAX_OUTPUT_CHARS = 20000

_LANGUAGE_CONFIG = {
    "python": {"filename": "main.py", "cmd": ["python3", "/sandbox/main.py"]},
    "javascript": {"filename": "main.js", "cmd": ["node", "/sandbox/main.js"]},
    "js": {"filename": "main.js", "cmd": ["node", "/sandbox/main.js"]},
    "bash": {"filename": "main.sh", "cmd": ["bash", "/sandbox/main.sh"]},
    "sh": {"filename": "main.sh", "cmd": ["bash", "/sandbox/main.sh"]},
}

SUPPORTED_LANGUAGES = sorted(set(_LANGUAGE_CONFIG))

_SANDBOX_ROOT = os.path.join(tempfile.gettempdir(), "creatoros_sandbox")


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    error: str | None = None


def run_code(language: str, code: str) -> ExecutionResult:
    """
    Executes `code` inside a locked-down, single-use Docker container and
    returns captured stdout/stderr. Never raises for normal failures
    (bad code, non-zero exit, timeout, missing Docker) - those come back
    as fields on ExecutionResult so callers can always render something.
    """
    lang = (language or "").lower().strip()
    config = _LANGUAGE_CONFIG.get(lang)
    if config is None:
        return ExecutionResult(
            stdout="",
            stderr="",
            exit_code=None,
            timed_out=False,
            error=f"Unsupported language '{language}'. Supported: {SUPPORTED_LANGUAGES}",
        )

    os.makedirs(_SANDBOX_ROOT, exist_ok=True)
    run_dir = os.path.join(_SANDBOX_ROOT, uuid.uuid4().hex[:12])
    os.makedirs(run_dir, exist_ok=True)
    host_file = os.path.join(run_dir, config["filename"])

    try:
        with open(host_file, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", _MEM_LIMIT,
            "--cpus", _CPUS,
            "--pids-limit", _PIDS_LIMIT,
            "--security-opt", "no-new-privileges",
            "--read-only",
            "--tmpfs", "/tmp:rw,size=32m",
            "-v", f"{run_dir}:/sandbox:ro",
            "-w", "/sandbox",
            "-u", "sandbox",
            _RUNNER_IMAGE,
            *config["cmd"],
        ]

        try:
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_SECONDS,
            )
            return ExecutionResult(
                stdout=proc.stdout[:_MAX_OUTPUT_CHARS],
                stderr=proc.stderr[:_MAX_OUTPUT_CHARS],
                exit_code=proc.returncode,
                timed_out=False,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                stdout="", stderr="", exit_code=None, timed_out=True,
                error=f"Execution exceeded {_TIMEOUT_SECONDS}s timeout.",
            )
        except FileNotFoundError:
            return ExecutionResult(
                stdout="", stderr="", exit_code=None, timed_out=False,
                error="Docker CLI not found. Is Docker Desktop installed, running, and on PATH?",
            )

    finally:
        shutil.rmtree(run_dir, ignore_errors=True)
'@
Write-Utf8NoBomAbs -Path "$Backend\app\services\coding\code_executor.py" -Content $codeExecutor
Write-Host "3/6 app/services/coding/code_executor.py created" -ForegroundColor Green


# ============================================================
# FILE 4 (NEW): app/schemas/code_execution.py
# ============================================================
$codeSchema = @'
from __future__ import annotations

from pydantic import BaseModel, Field


class CodeExecutionRequest(BaseModel):
    language: str = Field(..., description="python | javascript | bash")
    code: str = Field(..., max_length=50_000)


class CodeExecutionResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int | None
    timed_out: bool
    error: str | None = None
'@
Write-Utf8NoBomAbs -Path "$Backend\app\schemas\code_execution.py" -Content $codeSchema
Write-Host "4/6 app/schemas/code_execution.py created" -ForegroundColor Green


# ============================================================
# FILE 5 (NEW): app/api/v1/endpoints/coding.py
# ============================================================
$codingEndpoint = @'
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends

from app.database.models import User
from app.dependencies.auth import get_current_user
from app.schemas.code_execution import CodeExecutionRequest, CodeExecutionResponse
from app.services.coding.code_executor import run_code

router = APIRouter(
    prefix="/coding",
    tags=["Coding"],
)


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user),
):
    result = await asyncio.to_thread(run_code, request.language, request.code)
    return CodeExecutionResponse(
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        timed_out=result.timed_out,
        error=result.error,
    )
'@
Write-Utf8NoBomAbs -Path "$Backend\app\api\v1\endpoints\coding.py" -Content $codingEndpoint
Write-Host "5/6 app/api/v1/endpoints/coding.py created" -ForegroundColor Green


# ============================================================
# FILE 6: app/api/v1/endpoints/__init__.py - register coding_router
# Safe targeted insert: only touches the one known line, doesn't
# overwrite the rest of your existing router list.
# ============================================================
$initPath = "$Backend\app\api\v1\endpoints\__init__.py"

if (-not (Test-Path $initPath)) {
    Write-Host "6/6 SKIPPED - $initPath not found. Add this line manually:" -ForegroundColor Red
    Write-Host "     from .coding import router as coding_router" -ForegroundColor Yellow
} else {
    $initContent = Get-Content -Raw -Encoding UTF8 $initPath

    if ($initContent -match "from \.coding import router as coding_router") {
        Write-Host "6/6 __init__.py already has coding_router - skipped" -ForegroundColor Yellow
    } elseif ($initContent -match "from \.commands import router as commands_router") {
        $newInitContent = $initContent -replace `
            "from \.commands import router as commands_router", `
            "from .commands import router as commands_router`r`nfrom .coding import router as coding_router"
        Write-Utf8NoBomAbs -Path $initPath -Content $newInitContent
        Write-Host "6/6 __init__.py updated (coding_router added)" -ForegroundColor Green
    } else {
        Write-Host "6/6 SKIPPED - couldn't find anchor line. Add this manually to __init__.py:" -ForegroundColor Red
        Write-Host "     from .coding import router as coding_router" -ForegroundColor Yellow
    }
}


# ============================================================
# FILE 7: app/main.py - auto-patch (targeted insert, not a full
# overwrite): adds coding_router to the import block AND adds the
# app.include_router(coding_router, ...) call.
# ============================================================
$mainPath = "$Backend\app\main.py"

if (-not (Test-Path $mainPath)) {
    Write-Host "7/7 SKIPPED - $mainPath not found." -ForegroundColor Red
} else {
    $mainContent = Get-Content -Raw -Encoding UTF8 $mainPath
    $changed = $false

    if ($mainContent -notmatch "coding_router") {
        # 1) add to the import block (anchor: commands_router,)
        if ($mainContent -match "(?m)^(\s*)commands_router,\s*$") {
            $indent = $Matches[1]
            $mainContent = $mainContent -replace `
                "(?m)^(\s*)commands_router,\s*$", `
                "`$1commands_router,`r`n${indent}coding_router,"
            $changed = $true
        } else {
            Write-Host "7/7 WARNING - couldn't find 'commands_router,' import anchor in main.py" -ForegroundColor Red
        }

        # 2) add the include_router call (anchor: commands_router include line)
        if ($mainContent -match "app\.include_router\(commands_router, prefix=settings\.API_V1_PREFIX\)") {
            $mainContent = $mainContent -replace `
                "app\.include_router\(commands_router, prefix=settings\.API_V1_PREFIX\)", `
                "app.include_router(commands_router, prefix=settings.API_V1_PREFIX)`r`napp.include_router(coding_router, prefix=settings.API_V1_PREFIX)"
            $changed = $true
        } else {
            Write-Host "7/7 WARNING - couldn't find commands_router include_router anchor in main.py" -ForegroundColor Red
        }

        if ($changed) {
            Write-Utf8NoBomAbs -Path $mainPath -Content $mainContent
            Write-Host "7/7 main.py updated (coding_router wired in)" -ForegroundColor Green
        }
    } else {
        Write-Host "7/7 main.py already has coding_router - skipped" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "  1) Make sure Docker Desktop is installed and running" -ForegroundColor Cyan
Write-Host "  2) Build the sandbox image:" -ForegroundColor Cyan
Write-Host "     cd `"$Backend\docker\code-runner`"" -ForegroundColor Cyan
Write-Host "     docker build -t creatoros-code-runner:latest ." -ForegroundColor Cyan
Write-Host "  3) Restart uvicorn, then POST to /api/v1/coding/execute" -ForegroundColor Cyan
Write-Host "     body: { \"language\": \"python\", \"code\": \"print('hi')\" }" -ForegroundColor Cyan
