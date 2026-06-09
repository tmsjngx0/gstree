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
        print(f"gstree: error: gstree repo not found at {repo}", file=sys.stderr)
        print(f"gstree: set {_GSTREE_REPO_ENV} to override the default path", file=sys.stderr)
        return 1

    print(f"gstree: pulling latest from {repo}...")
    pull = subprocess.run(
        ["git", "-C", str(repo), "pull"],
        capture_output=True, text=True,
    )
    if pull.stdout:
        print(pull.stdout, end="")
    if pull.returncode != 0:
        print(pull.stderr, file=sys.stderr, end="")
        return pull.returncode

    print("gstree: reinstalling tool...")
    reinstall = subprocess.run(
        ["uv", "tool", "upgrade", "gstree", "--reinstall"],
        capture_output=True, text=True,
    )
    if reinstall.stdout:
        print(reinstall.stdout, end="")
    if reinstall.returncode != 0:
        print(reinstall.stderr, file=sys.stderr, end="")
        return reinstall.returncode

    verify = subprocess.run(
        ["gstree", "--version"],
        capture_output=True, text=True,
    )
    if verify.returncode == 0:
        print(f"\u2713 {verify.stdout.strip()}")
    else:
        print("gstree: upgrade complete (verify with gstree --version)")

    return 0
