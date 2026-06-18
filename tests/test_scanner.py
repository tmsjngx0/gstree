import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from gstree.scanner import scan_workspace

from helpers import create_tracking_repo, init_repo


class GstreeScannerTest(unittest.TestCase):
    def test_scan_workspace_honors_depth_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "workspace"
            root.mkdir()
            init_repo(root / "app")
            init_repo(root / "nested" / "service")

            repos = scan_workspace(root, max_depth=1)

            self.assertEqual([repo.name for repo in repos], ["app"])

    def test_scan_workspace_collects_dirty_and_tracking_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace, tracked = create_tracking_repo(Path(tmpdir))

            repos = scan_workspace(workspace, max_depth=2)

            self.assertEqual(len(repos), 1)
            repo = repos[0]
            self.assertEqual(repo.name, "tracked")
            self.assertEqual(repo.path, str(tracked.resolve()))
            self.assertEqual(repo.branch, "main")
            self.assertTrue(repo.dirty)
            self.assertTrue(repo.tracking)
            self.assertEqual(repo.ahead, 1)
            self.assertEqual(repo.behind, 1)

    def test_scan_workspace_includes_nested_repo_inside_repo_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "workspace"
            root.mkdir()
            init_repo(root / "app")
            init_repo(root / "app" / "vendor" / "module")

            repos = scan_workspace(root, max_depth=4)

            self.assertEqual(
                [repo.path for repo in repos],
                [
                    str((root / "app").resolve()),
                    str((root / "app" / "vendor" / "module").resolve()),
                ],
            )

    def test_scan_workspace_skips_unreadable_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "workspace"
            root.mkdir()
            init_repo(root / "app")
            blocked = root / "blocked"
            blocked.mkdir()
            blocked.chmod(0)

            stderr = io.StringIO()
            try:
                with contextlib.redirect_stderr(stderr):
                    repos = scan_workspace(root, max_depth=2)
            finally:
                blocked.chmod(0o755)

            self.assertEqual([repo.name for repo in repos], ["app"])
            self.assertIn("warning: skipped", stderr.getvalue())
            self.assertIn(str(blocked), stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
