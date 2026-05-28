from __future__ import annotations

from pathlib import Path

from .models import RepoStatus


def render_text_report(root: Path, repos: list[RepoStatus]) -> str:
    root_name = root.name or str(root)
    lines = [root_name]

    if repos:
        for index, repo in enumerate(repos):
            connector = "└──" if index == len(repos) - 1 else "├──"
            relative_path = Path(repo.path).resolve().relative_to(root.resolve())
            state = "dirty" if repo.dirty else "clean"
            lines.append(f"{connector} {relative_path.as_posix()} [{repo.branch}] {state}")
    else:
        lines.append("└── (no git repos found)")

    dirty_count = sum(1 for repo in repos if repo.dirty)
    lines.append(f"{len(repos)} repos, {dirty_count} dirty")
    return "\n".join(lines)
