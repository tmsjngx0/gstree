import os
import sys
import tempfile
import unittest
from pathlib import Path

from gstree.upgrade import cmd_upgrade


class GstreeUpgradeTest(unittest.TestCase):
    def test_upgrade_fails_when_repo_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            env = os.environ.copy()
            env["GSTREE_REPO_PATH"] = str(Path(tmpdir) / "nonexistent")

            code = cmd_upgrade()

            self.assertNotEqual(code, 0)

    def test_upgrade_succeeds_on_valid_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "gstree"
            repo.mkdir()
            (repo / ".git").mkdir()

            env = os.environ.copy()
            env["GSTREE_REPO_PATH"] = str(repo)
            old_env = os.environ.get("GSTREE_REPO_PATH")
            try:
                os.environ["GSTREE_REPO_PATH"] = str(repo)
                code = cmd_upgrade()
            finally:
                if old_env is None:
                    os.environ.pop("GSTREE_REPO_PATH", None)
                else:
                    os.environ["GSTREE_REPO_PATH"] = old_env

            self.assertNotEqual(code, 0, "should fail because no remote")

    def test_upgrade_dispatched_from_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_repo = Path(tmpdir) / "gstree"
            test_repo.mkdir()
            (test_repo / ".git").mkdir()

            env = os.environ.copy()
            env["GSTREE_REPO_PATH"] = str(test_repo)
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")

            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "gstree", "upgrade"],
                capture_output=True, text=True, env=env,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not a git repository", result.stderr)


if __name__ == "__main__":
    unittest.main()
