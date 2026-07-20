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