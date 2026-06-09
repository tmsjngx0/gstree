import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gstree import __version__
from helpers import create_repo_with_status_tokens, init_repo


class GstreeCliJsonTest(unittest.TestCase):
    def _run_gstree(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
        env["NO_COLOR"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "gstree", *args],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_version_output_reports_current_package_version(self) -> None:
        result = self._run_gstree("--version")

        self.assertEqual(result.stdout, f"gstree {__version__}\n")

    def test_json_output_lists_git_repositories_under_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = init_repo(root / "app")

            result = self._run_gstree("--json", str(root))

            payload = json.loads(result.stdout)
            self.assertEqual(payload["root"], str(root.resolve()))
            self.assertEqual(
                payload["repos"],
                [
                    {
                        "name": "app",
                        "path": str(repo.resolve()),
                        "branch": "main",
                        "dirty": False,
                        "tracking": False,
                        "ahead": 0,
                        "behind": 0,
                    }
                ],
            )

    def test_text_output_renders_tree_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "workspace"
            root.mkdir()
            init_repo(root / "app")
            dirty_repo = init_repo(root / "nested" / "service")
            (dirty_repo / "dirty.txt").write_text("dirty\n")

            result = self._run_gstree(str(root))

            self.assertEqual(
                result.stdout.strip().splitlines(),
                [
                    "workspace",
                    "├── app [main] clean",
                    "└── nested/",
                    "    └── service [main] ?1",
                    "2 repos, 1 dirty",
                ],
            )

    def test_text_output_includes_compact_status_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace, _tracked = create_repo_with_status_tokens(Path(tmpdir))

            result = self._run_gstree(str(workspace))

            self.assertEqual(
                result.stdout.strip().splitlines(),
                [
                    "workspace",
                    "└── tracked [main] +1 ~1 ?1 ↑1 ↓1",
                    "1 repos, 1 dirty",
                ],
            )

    def test_dirty_flag_hides_clean_repositories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "workspace"
            root.mkdir()
            init_repo(root / "app")
            dirty_repo = init_repo(root / "nested" / "service")
            (dirty_repo / "dirty.txt").write_text("dirty\n")

            result = self._run_gstree("--dirty", str(root))

            self.assertEqual(
                result.stdout.strip().splitlines(),
                [
                    "workspace",
                    "└── nested/",
                    "    └── service [main] ?1",
                    "1 repos, 1 dirty",
                ],
            )


if __name__ == "__main__":
    unittest.main()
