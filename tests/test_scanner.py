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


if __name__ == "__main__":
    unittest.main()
