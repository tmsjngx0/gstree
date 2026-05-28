from __future__ import annotations

import subprocess
from pathlib import Path

from .models import RepoStatus


def collect_repo_status(path: Path) -> RepoStatus:
    branch = _git(path, 'branch', '--show-current').strip()
    dirty = bool(_git(path, 'status', '--porcelain').strip())
    tracking_ref = _git_optional(path, 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}')
    tracking = tracking_ref is not None
    ahead = 0
    behind = 0
    if tracking:
        counts = _git(path, 'rev-list', '--left-right', '--count', 'HEAD...@{u}').strip().split()
        ahead = int(counts[0])
        behind = int(counts[1])
    return RepoStatus(
        name=path.name,
        path=str(path.resolve()),
        branch=branch,
        dirty=dirty,
        tracking=tracking,
        ahead=ahead,
        behind=behind,
    )


def _git(path: Path, *args: str) -> str:
    result = subprocess.run(
        ['git', '-C', str(path), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _git_optional(path: Path, *args: str) -> str | None:
    result = subprocess.run(
        ['git', '-C', str(path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()
