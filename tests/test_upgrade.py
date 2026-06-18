import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from importlib import metadata
from pathlib import Path
from unittest import mock

import gstree.upgrade as upgrade


def _completed(
    args: list[str],
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=args,
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class _FakeDistribution:
    def __init__(self, installer: str | None) -> None:
        self.installer = installer

    def read_text(self, name: str) -> str | None:
        if name == "INSTALLER":
            return self.installer
        return None


class GstreeUpgradeTest(unittest.TestCase):
    def test_upgrade_uses_source_checkout_when_repo_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "gstree"
            repo.mkdir()
            (repo / ".git").mkdir()
            resolved_repo = repo.resolve()

            stdout = io.StringIO()
            with (
                mock.patch.dict(os.environ, {upgrade._GSTREE_REPO_ENV: str(repo)}, clear=True),
                mock.patch.object(
                    upgrade.subprocess,
                    "run",
                    side_effect=[
                        _completed(["git"], stdout="Already up to date.\n"),
                        _completed(["uv"], stdout="Reinstalled gstree.\n"),
                        _completed(["gstree", "--version"], stdout="gstree 0.1.4\n"),
                    ],
                ) as run,
                contextlib.redirect_stdout(stdout),
            ):
                code = upgrade.cmd_upgrade()

            self.assertEqual(code, 0)
            self.assertEqual(run.call_args_list[0].args[0], ["git", "-C", str(resolved_repo), "pull"])
            self.assertEqual(
                run.call_args_list[1].args[0],
                ["uv", "tool", "upgrade", "gstree", "--reinstall"],
            )
            self.assertIn("gstree 0.1.4", stdout.getvalue())

    def test_upgrade_delegates_to_pip_for_pypi_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch.object(upgrade, "_detect_repo_path", return_value=None),
                mock.patch.object(upgrade, "_GSTREE_REPO_DEFAULT", str(Path(tmpdir) / "missing")),
                mock.patch.object(
                    metadata,
                    "distribution",
                    return_value=_FakeDistribution("pip\n"),
                ),
                mock.patch.object(
                    upgrade.subprocess,
                    "run",
                    side_effect=[
                        _completed(
                            [sys.executable, "-m", "pip", "install", "--upgrade", "gstree"],
                            stdout="Successfully installed gstree-0.1.4\n",
                        ),
                        _completed(["gstree", "--version"], stdout="gstree 0.1.4\n"),
                    ],
                ) as run,
                contextlib.redirect_stdout(stdout),
                contextlib.redirect_stderr(stderr),
            ):
                code = upgrade.cmd_upgrade()

            self.assertEqual(code, 0)
            self.assertEqual(
                run.call_args_list[0].args[0],
                [sys.executable, "-m", "pip", "install", "--upgrade", "gstree"],
            )
            self.assertNotIn("repo not found", stderr.getvalue())
            self.assertIn("gstree 0.1.4", stdout.getvalue())

    def test_upgrade_delegates_to_uv_tool_for_uv_install(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stdout = io.StringIO()
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch.object(upgrade, "_detect_repo_path", return_value=None),
                mock.patch.object(upgrade, "_GSTREE_REPO_DEFAULT", str(Path(tmpdir) / "missing")),
                mock.patch.object(
                    metadata,
                    "distribution",
                    return_value=_FakeDistribution("uv\n"),
                ),
                mock.patch.object(
                    upgrade.subprocess,
                    "run",
                    side_effect=[
                        _completed(
                            ["uv", "tool", "upgrade", "gstree"],
                            stdout="Resolved 1 package in 10ms\n",
                        ),
                        _completed(["gstree", "--version"], stdout="gstree 0.1.4\n"),
                    ],
                ) as run,
                contextlib.redirect_stdout(stdout),
            ):
                code = upgrade.cmd_upgrade()

            self.assertEqual(code, 0)
            self.assertEqual(run.call_args_list[0].args[0], ["uv", "tool", "upgrade", "gstree"])
            self.assertIn("gstree 0.1.4", stdout.getvalue())

    def test_upgrade_prints_manual_guidance_when_install_method_is_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            stderr = io.StringIO()
            with (
                mock.patch.dict(os.environ, {}, clear=True),
                mock.patch.object(upgrade, "_detect_repo_path", return_value=None),
                mock.patch.object(upgrade, "_GSTREE_REPO_DEFAULT", str(Path(tmpdir) / "missing")),
                mock.patch.object(
                    metadata,
                    "distribution",
                    side_effect=metadata.PackageNotFoundError,
                ),
                contextlib.redirect_stderr(stderr),
            ):
                code = upgrade.cmd_upgrade()

            self.assertEqual(code, 1)
            self.assertIn("uv tool upgrade gstree", stderr.getvalue())
            self.assertIn("-m pip install --upgrade gstree", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
