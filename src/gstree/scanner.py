from __future__ import annotations

from pathlib import Path

from .models import RepoStatus
from .status import collect_repo_status


SKIP_DIRS = {'.git', '__pycache__', '.venv'}


def scan_workspace(root: Path, max_depth: int) -> list[RepoStatus]:
    resolved_root = root.resolve()
    repos: list[RepoStatus] = []
    _scan_directory(resolved_root, 0, max_depth, repos)
    return sorted(repos, key=lambda repo: repo.path)


def _scan_directory(path: Path, depth: int, max_depth: int, repos: list[RepoStatus]) -> None:
    is_repo = _is_git_repo(path)
    if is_repo:
        repos.append(collect_repo_status(path))

    if depth >= max_depth:
        return

    for child in sorted(path.iterdir(), key=lambda candidate: candidate.name):
        if not child.is_dir():
            continue
        if child.name in SKIP_DIRS:
            continue
        _scan_directory(child, depth + 1, max_depth, repos)


def _is_git_repo(path: Path) -> bool:
    git_entry = path / '.git'
    return git_entry.is_dir() or git_entry.is_file()
