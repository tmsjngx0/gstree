from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

_GSTREE_REPO_ENV = "GSTREE_REPO_PATH"
_GSTREE_REPO_DEFAULT = "~/.local/share/gstree"


def _detect_repo_path() -> Path | None:
    import gstree as _self
    candidate = Path(_self.__file__).resolve().parent.parent.parent
    if (candidate / ".git").exists():
        return candidate
    return None


def cmd_upgrade() -> int:
    env_repo = os.environ.get(_GSTREE_REPO_ENV)
    if env_repo is not None:
        repo = Path(env_repo).expanduser().resolve()
    else:
        detected = _detect_repo_path()
        repo = detected or Path(_GSTREE_REPO_DEFAULT).expanduser().resolve()

    if not (repo / ".git").exists():
        sys.stderr.write(f"gstree: error: gstree repo not found at {repo}\n")
        sys.stderr.write(f"gstree: set {_GSTREE_REPO_ENV} to override the default path\n")
        return 1

    sys.stderr.write(f"gstree: pulling latest from {repo}...\n")
    pull = subprocess.run(
        ["git", "-C", str(repo), "pull"],
        capture_output=True, text=True, timeout=60,
    )
    if pull.stdout:
        sys.stdout.write(pull.stdout)
    if pull.returncode != 0:
        sys.stderr.write(pull.stderr)
        return pull.returncode

    sys.stderr.write("gstree: reinstalling tool...\n")
    reinstall = subprocess.run(
        ["uv", "tool", "upgrade", "gstree", "--reinstall"],
        capture_output=True, text=True, timeout=120,
    )
    if reinstall.stdout:
        sys.stdout.write(reinstall.stdout)
    if reinstall.returncode != 0:
        sys.stderr.write(reinstall.stderr)
        return reinstall.returncode

    verify = subprocess.run(
        ["gstree", "--version"],
        capture_output=True, text=True, timeout=10,
    )
    if verify.returncode == 0:
        sys.stdout.write(f"\u2713 {verify.stdout.strip()}\n")
    else:
        sys.stdout.write("gstree: upgrade complete (verify with gstree --version)\n")

    return 0
