import subprocess
from pathlib import Path


def git(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def configure_identity(repo: Path) -> None:
    git("config", "user.name", "Test User", cwd=repo)
    git("config", "user.email", "test@example.com", cwd=repo)


def init_repo(repo: Path) -> Path:
    git("init", "-b", "main", str(repo))
    configure_identity(repo)
    return repo


def commit_file(repo: Path, relative_path: str, contents: str, message: str) -> None:
    file_path = repo / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(contents)
    git("add", relative_path, cwd=repo)
    git("commit", "-m", message, cwd=repo)


def _make_tracking_base(
    tmp_root: Path,
    extra_seed_files: dict[str, str] | None = None,
) -> tuple[Path, Path]:
    """Create a workspace with one repo at ↑1 ↓1 tracking state.

    extra_seed_files: additional files committed to the seed before cloning.
    Returns (workspace, tracked_repo_path).
    """
    workspace = tmp_root / "workspace"
    workspace.mkdir()

    remote = tmp_root / "remote.git"
    git("init", "--bare", "-b", "main", str(remote))

    seed = tmp_root / "seed"
    init_repo(seed)
    commit_file(seed, "README.md", "seed\n", "initial commit")
    for name, content in (extra_seed_files or {}).items():
        commit_file(seed, name, content, f"add {name}")
    git("remote", "add", "origin", str(remote), cwd=seed)
    git("push", "-u", "origin", "main", cwd=seed)

    tracked = workspace / "tracked"
    git("clone", str(remote), str(tracked))
    configure_identity(tracked)

    other = tmp_root / "other"
    git("clone", str(remote), str(other))
    configure_identity(other)

    commit_file(tracked, "local.txt", "local\n", "local change")
    commit_file(other, "remote.txt", "remote\n", "remote change")
    git("push", cwd=other)
    git("fetch", "origin", cwd=tracked)

    return workspace, tracked


def create_tracking_repo(tmp_root: Path) -> tuple[Path, Path]:
    workspace, tracked = _make_tracking_base(tmp_root)
    (tracked / "dirty.txt").write_text("dirty\n")
    return workspace, tracked


def create_repo_with_status_tokens(tmp_root: Path) -> tuple[Path, Path]:
    workspace, tracked = _make_tracking_base(
        tmp_root, extra_seed_files={"tracked.txt": "tracked\n"}
    )
    (tracked / "tracked.txt").write_text("tracked staged change\n")
    git("add", "tracked.txt", cwd=tracked)
    (tracked / "README.md").write_text("seed modified\n")
    (tracked / "untracked.txt").write_text("untracked\n")
    return workspace, tracked
