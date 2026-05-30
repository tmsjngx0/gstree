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


def create_tracking_repo(tmp_root: Path) -> tuple[Path, Path]:
    workspace = tmp_root / "workspace"
    workspace.mkdir()

    remote = tmp_root / "remote.git"
    git("init", "--bare", str(remote))

    seed = tmp_root / "seed"
    init_repo(seed)
    commit_file(seed, "README.md", "seed\n", "initial commit")
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

    (tracked / "dirty.txt").write_text("dirty\n")
    return workspace, tracked


def create_repo_with_status_tokens(tmp_root: Path) -> tuple[Path, Path]:
    workspace = tmp_root / "workspace"
    workspace.mkdir()

    remote = tmp_root / "remote.git"
    git("init", "--bare", str(remote))

    seed = tmp_root / "seed"
    init_repo(seed)
    commit_file(seed, "README.md", "seed\n", "initial commit")
    commit_file(seed, "tracked.txt", "tracked\n", "tracked baseline")
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

    tracked_file = tracked / "tracked.txt"
    tracked_file.write_text("tracked staged change\n")
    git("add", "tracked.txt", cwd=tracked)

    readme = tracked / "README.md"
    readme.write_text("seed modified\n")

    (tracked / "untracked.txt").write_text("untracked\n")
    return workspace, tracked
