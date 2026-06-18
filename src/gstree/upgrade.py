from __future__ import annotations

import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path

_GSTREE_REPO_ENV = "GSTREE_REPO_PATH"
_GSTREE_REPO_DEFAULT = "~/.local/share/gstree"
_PACKAGE_NAME = "gstree"


def _detect_repo_path() -> Path | None:
    from . import __file__ as package_file

    candidate = Path(package_file).resolve().parent.parent.parent
    if (candidate / ".git").exists():
        return candidate
    return None


def cmd_upgrade() -> int:
    env_repo = os.environ.get(_GSTREE_REPO_ENV)
    if env_repo is not None:
        repo = Path(env_repo).expanduser().resolve()
        if not (repo / ".git").exists():
            sys.stderr.write(f"gstree: error: gstree repo not found at {repo}\n")
            sys.stderr.write(
                f"gstree: unset {_GSTREE_REPO_ENV} to use package-manager upgrades instead\n"
            )
            return 1
        return _upgrade_from_source_checkout(repo)

    detected_repo = _detect_repo_path()
    if detected_repo is not None:
        return _upgrade_from_source_checkout(detected_repo)

    default_repo = Path(_GSTREE_REPO_DEFAULT).expanduser().resolve()
    if (default_repo / ".git").exists():
        return _upgrade_from_source_checkout(default_repo)

    return _upgrade_installed_package()


def _upgrade_from_source_checkout(repo: Path) -> int:
    sys.stderr.write(f"gstree: pulling latest from {repo}...\n")
    pull = _run_command(["git", "-C", str(repo), "pull"], timeout=60)
    if pull.returncode != 0:
        return pull.returncode

    sys.stderr.write("gstree: reinstalling tool...\n")
    reinstall = _run_command(
        ["uv", "tool", "upgrade", _PACKAGE_NAME, "--reinstall"],
        timeout=120,
    )
    if reinstall.returncode != 0:
        return reinstall.returncode

    return _verify_upgrade()


def _upgrade_installed_package() -> int:
    installer = _detect_installer()
    if installer == "pip":
        sys.stderr.write("gstree: upgrading installed gstree with pip...\n")
        result = _run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", _PACKAGE_NAME],
            timeout=120,
        )
        if result.returncode != 0:
            return result.returncode
        return _verify_upgrade()

    if installer == "uv":
        sys.stderr.write("gstree: upgrading installed gstree with uv...\n")
        result = _run_command(["uv", "tool", "upgrade", _PACKAGE_NAME], timeout=120)
        if result.returncode != 0:
            return result.returncode
        return _verify_upgrade()

    sys.stderr.write(
        "gstree: no source checkout or known installer metadata found.\n"
    )
    sys.stderr.write("gstree: upgrade manually with one of:\n")
    sys.stderr.write(f"  uv tool upgrade {_PACKAGE_NAME}\n")
    sys.stderr.write(
        f"  {sys.executable} -m pip install --upgrade {_PACKAGE_NAME}\n"
    )
    sys.stderr.write(
        f"gstree: for source checkouts, set {_GSTREE_REPO_ENV}=/path/to/gstree\n"
    )
    return 1


def _detect_installer() -> str | None:
    try:
        dist = metadata.distribution(_PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return None

    installer = dist.read_text("INSTALLER")
    if installer is None:
        return None

    normalized = installer.strip().lower()
    return normalized or None


def _run_command(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.returncode != 0 and result.stderr:
        sys.stderr.write(result.stderr)
    return result


def _verify_upgrade() -> int:
    verify = subprocess.run(
        ["gstree", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    if verify.returncode == 0:
        sys.stdout.write(f"✓ {verify.stdout.strip()}\n")
    else:
        sys.stdout.write("gstree: upgrade complete (verify with gstree --version)\n")
    return 0
