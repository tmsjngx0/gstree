from __future__ import annotations

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


@dataclass(frozen=True)
class Palette:
    color: bool = True

    def green(self, s: str) -> str:
        return f"{_GREEN}{s}{_RESET}" if self.color else s

    def red(self, s: str) -> str:
        return f"{_RED}{s}{_RESET}" if self.color else s

    def yellow(self, s: str) -> str:
        return f"{_YELLOW}{s}{_RESET}" if self.color else s

    def repo(self, name: str, depth: int) -> str:
        if not self.color:
            return name
        if depth <= 0:
            return f"{_CYAN}{_BOLD}{name}{_RESET}"
        if depth == 1:
            return f"{_BOLD}{name}{_RESET}"
        return f"{_GRAY}{name}{_RESET}"

    def dir(self, name: str, depth: int, leaf: bool = True) -> str:
        if not self.color:
            return f"{name}/" if leaf else name
        if depth <= 0:
            c = f"{_CYAN}{_BOLD}{name}{_RESET}"
        elif depth == 1:
            c = f"{_BLUE}{_BOLD}{name}{_RESET}"
        else:
            c = f"{_GRAY}{name}{_RESET}"
        return f"{c}/" if leaf else c


@dataclass
class _TreeNode:
    name: str
    repo: RepoStatus | None = None
    children: dict[str, _TreeNode] = field(default_factory=dict)


def render_text_report(
    root: Path,
    repos: list[RepoStatus],
    palette: Palette = Palette(),
) -> str:
    root_name = root.name or str(root)
    tree, root_repo = _build_tree(root, repos)

    if not tree:
        summary = f"{len(repos)} repos, 0 dirty"
        return f"{root_name}\n└── (no git repos found)\n{summary}"

    header = palette.dir(root_name, 0, leaf=False)
    if root_repo:
        branch = root_repo.branch or ""
        branch_fmt = palette.yellow(branch) if branch else branch
        state = _format_repo_state(root_repo, palette)
        header = f"{header} [{branch_fmt}] {state}"
    lines = [header]
    _render_node(tree, 0, "", lines, palette)

    dirty_count = sum(1 for repo in repos if repo.dirty)
    summary_text = f"{len(repos)} repos, {dirty_count} dirty"
    summary = palette.red(summary_text) if dirty_count > 0 else palette.green(summary_text)
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


def _render_node(node: _TreeNode, depth: int, prefix: str, lines: list[str], palette: Palette) -> None:
    items = list(node.children.items())
    for index, (name, child) in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "

        if child.repo:
            branch = child.repo.branch or ""
            branch_fmt = palette.yellow(branch) if branch else branch
            state = _format_repo_state(child.repo, palette)
            lines.append(f"{prefix}{connector}{palette.repo(name, depth + 1)} [{branch_fmt}] {state}")
        else:
            lines.append(f"{prefix}{connector}{palette.dir(name, depth + 1)}")

        child_prefix = prefix + ("    " if is_last else "│   ")
        _render_node(child, depth + 1, child_prefix, lines, palette)


def _format_repo_state(repo: RepoStatus, palette: Palette) -> str:
    tokens: list[str] = []
    if repo.staged:
        tokens.append(palette.yellow(f"+{repo.staged}"))
    if repo.modified:
        tokens.append(palette.red(f"~{repo.modified}"))
    if repo.untracked:
        tokens.append(palette.red(f"?{repo.untracked}"))
    if repo.ahead:
        tokens.append(palette.green(f"↑{repo.ahead}"))
    if repo.behind:
        tokens.append(palette.red(f"↓{repo.behind}"))
    if not tokens:
        return palette.green("clean")
    return " ".join(tokens)
