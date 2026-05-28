from pathlib import Path

from .models import RepoStatus


def scan_workspace(root: Path, max_depth: int) -> list[RepoStatus]:
    return []
