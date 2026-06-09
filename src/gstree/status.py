from __future__ import annotations

import subprocess
from pathlib import Path

from .models import RepoStatus


def collect_repo_status(path: Path, fetch: bool = False) -> RepoStatus:
    if fetch:
        _git_optional(path, 'fetch', '--all')
    status_lines = _git(path, 'status', '--porcelain').splitlines()
    staged, modified, untracked = _count_worktree_changes(status_lines)
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
        branch=_git(path, 'branch', '--show-current').strip(),
        dirty=bool(status_lines),
        tracking=tracking,
        ahead=ahead,
        behind=behind,
        staged=staged,
        modified=modified,
        untracked=untracked,
    )


def _count_worktree_changes(status_lines: list[str]) -> tuple[int, int, int]:
    staged = 0
    modified = 0
    untracked = 0
    for line in status_lines:
        if line.startswith('??'):
            untracked += 1
            continue
        index_status = line[0]
        worktree_status = line[1]
        if index_status not in {' ', '?'}:
            staged += 1
        if worktree_status != ' ':
            modified += 1
    return staged, modified, untracked


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
