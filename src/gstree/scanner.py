from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .models import RepoStatus
from .status import collect_repo_status


SKIP_DIRS = {'.git', '__pycache__', '.venv'}
_MAX_WORKERS = 8


def scan_workspace(root: Path, max_depth: int, fetch: bool = False) -> list[RepoStatus]:
    resolved_root = root.resolve()
    repo_paths: list[Path] = []
    _find_repos(resolved_root, 0, max_depth, repo_paths)

    repos: list[RepoStatus] = []
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
        futures = {pool.submit(_collect_safe, p, fetch): p for p in repo_paths}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                repos.append(result)

    return sorted(repos, key=lambda repo: repo.path)


def _find_repos(path: Path, depth: int, max_depth: int, repo_paths: list[Path]) -> None:
    try:
        if _is_git_repo(path):
            repo_paths.append(path)
    except OSError as exc:
        _warn_skip(path, exc)
        return

    if depth >= max_depth:
        return

    try:
        children = sorted(path.iterdir(), key=lambda candidate: candidate.name)
    except OSError as exc:
        _warn_skip(path, exc)
        return

    for child in children:
        try:
            is_dir = child.is_dir()
        except OSError as exc:
            _warn_skip(child, exc)
            continue

        if not is_dir:
            continue
        if child.name in SKIP_DIRS:
            continue
        _find_repos(child, depth + 1, max_depth, repo_paths)


def _collect_safe(path: Path, fetch: bool) -> RepoStatus | None:
    try:
        return collect_repo_status(path, fetch)
    except subprocess.TimeoutExpired:
        sys.stderr.write(f"gstree: warning: timed out reading {path}\n")
        return None
    except (subprocess.CalledProcessError, OSError, ValueError) as exc:
        _warn_skip(path, exc)
        return None


def _warn_skip(path: Path, exc: OSError | ValueError) -> None:
    sys.stderr.write(f"gstree: warning: skipped {path}: {exc}\n")


def _is_git_repo(path: Path) -> bool:
    git_entry = path / '.git'
    return git_entry.is_dir() or git_entry.is_file()
