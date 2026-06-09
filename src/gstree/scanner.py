from __future__ import annotations

from pathlib import Path

from .models import RepoStatus
from .status import collect_repo_status


SKIP_DIRS = {'.git', '__pycache__', '.venv'}


def scan_workspace(root: Path, max_depth: int, fetch: bool = False) -> list[RepoStatus]:
    resolved_root = root.resolve()
    repos: list[RepoStatus] = []
    _scan_directory(resolved_root, 0, max_depth, repos, fetch)
    return sorted(repos, key=lambda repo: repo.path)


def _scan_directory(path: Path, depth: int, max_depth: int, repos: list[RepoStatus], fetch: bool = False) -> None:
    is_repo = _is_git_repo(path)
    if is_repo:
        repos.append(collect_repo_status(path, fetch))

    if depth >= max_depth:
        return

    for child in sorted(path.iterdir(), key=lambda candidate: candidate.name):
        if not child.is_dir():
            continue
        if child.name in SKIP_DIRS:
            continue
        _scan_directory(child, depth + 1, max_depth, repos, fetch)


def _is_git_repo(path: Path) -> bool:
    git_entry = path / '.git'
    return git_entry.is_dir() or git_entry.is_file()
