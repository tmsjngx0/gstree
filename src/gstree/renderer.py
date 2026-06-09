from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .models import RepoStatus

_CYAN = "\033[36m"
_BLUE = "\033[34m"
_GRAY = "\033[90m"
_BOLD = "\033[1m"
_GREEN = "\033[32m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_RESET = "\033[0m"

_use_color = os.environ.get("NO_COLOR") is None


def _fmt_dir(name: str, depth: int, leaf: bool = True) -> str:
    if not _use_color:
        return f"{name}/" if leaf else name
    if depth <= 0:
        c = f"{_CYAN}{_BOLD}{name}{_RESET}"
    elif depth == 1:
        c = f"{_BLUE}{_BOLD}{name}{_RESET}"
    else:
        c = f"{_GRAY}{name}{_RESET}"
    return f"{c}/" if leaf else c


def _fmt_repo(name: str, depth: int) -> str:
    if not _use_color:
        return name
    if depth <= 0:
        return f"{_CYAN}{_BOLD}{name}{_RESET}"
    elif depth == 1:
        return f"{_BOLD}{name}{_RESET}"
    return f"{_GRAY}{name}{_RESET}"


def _green(s: str) -> str:
    return f"{_GREEN}{s}{_RESET}" if _use_color else s


def _red(s: str) -> str:
    return f"{_RED}{s}{_RESET}" if _use_color else s


def _yellow(s: str) -> str:
    return f"{_YELLOW}{s}{_RESET}" if _use_color else s


@dataclass
class _TreeNode:
    name: str
    repo: RepoStatus | None = None
    children: dict[str, _TreeNode] = field(default_factory=dict)


def render_text_report(root: Path, repos: list[RepoStatus]) -> str:
    root_name = root.name or str(root)
    tree, root_repo = _build_tree(root, repos)

    if not tree:
        summary = f"{len(repos)} repos, 0 dirty"
        return f"{root_name}\n└── (no git repos found)\n{summary}"

    header = _fmt_dir(root_name, 0, leaf=False)
    if root_repo:
        branch = _yellow(root_repo.branch) if root_repo.branch and _use_color else root_repo.branch
        state = _format_repo_state(root_repo)
        header = f"{header} [{branch}] {state}"
    lines = [header]
    _render_node(tree, 0, "", lines)

    dirty_count = sum(1 for repo in repos if repo.dirty)
    label = _red if dirty_count > 0 else _green
    summary = label(f"{len(repos)} repos, {dirty_count} dirty") if _use_color else f"{len(repos)} repos, {dirty_count} dirty"
    lines.append(summary)
    return "\n".join(lines)


def _build_tree(root: Path, repos: list[RepoStatus]) -> tuple[_TreeNode | None, RepoStatus | None]:
    root_node = _TreeNode(name=root.name or str(root))
    root_repo: RepoStatus | None = None
    root_resolved = root.resolve()
    for repo in repos:
        resolved = Path(repo.path).resolve()
        if resolved == root_resolved:
            root_repo = repo
            continue
        rel = resolved.relative_to(root_resolved)
        node = root_node
        for part in rel.parts:
            if part not in node.children:
                node.children[part] = _TreeNode(name=part)
            node = node.children[part]
        node.repo = repo
    return root_node, root_repo


def _render_node(node: _TreeNode, depth: int, prefix: str, lines: list[str]) -> None:
    items = list(node.children.items())
    for index, (name, child) in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "

        if child.repo:
            branch = _yellow(child.repo.branch) if child.repo.branch and _use_color else child.repo.branch
            state = _format_repo_state(child.repo)
            lines.append(f"{prefix}{connector}{_fmt_repo(name, depth + 1)} [{branch}] {state}")
        else:
            lines.append(f"{prefix}{connector}{_fmt_dir(name, depth + 1)}")

        child_prefix = prefix + ("    " if is_last else "│   ")
        _render_node(child, depth + 1, child_prefix, lines)


def _format_repo_state(repo: RepoStatus) -> str:
    tokens: list[str] = []
    if repo.staged:
        tokens.append(_yellow(f"+{repo.staged}"))
    if repo.modified:
        tokens.append(_red(f"~{repo.modified}"))
    if repo.untracked:
        tokens.append(_red(f"?{repo.untracked}"))
    if repo.ahead:
        tokens.append(_green(f"↑{repo.ahead}"))
    if repo.behind:
        tokens.append(_red(f"↓{repo.behind}"))
    if not tokens:
        return _green("clean")
    return " ".join(tokens)
