import tempfile
import unittest
from pathlib import Path

from gstree.status import collect_repo_status
from helpers import commit_file, configure_identity, git, init_repo


class CollectRepoStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp()
        self.repo = Path(self._tmp) / "repo"
        init_repo(self.repo)
        commit_file(self.repo, "README.md", "hello\n", "initial commit")

    def test_clean_repo(self) -> None:
        status = collect_repo_status(self.repo)
        self.assertEqual(status.branch, "main")
        self.assertFalse(status.dirty)
        self.assertEqual(status.staged, 0)
        self.assertEqual(status.modified, 0)
        self.assertEqual(status.untracked, 0)

    def test_untracked_file(self) -> None:
        (self.repo / "new.txt").write_text("new\n")
        status = collect_repo_status(self.repo)
        self.assertTrue(status.dirty)
        self.assertEqual(status.untracked, 1)

    def test_staged_file(self) -> None:
        (self.repo / "new.txt").write_text("new\n")
        git("add", "new.txt", cwd=self.repo)
        status = collect_repo_status(self.repo)
        self.assertTrue(status.dirty)
        self.assertEqual(status.staged, 1)

    def test_modified_file(self) -> None:
        (self.repo / "README.md").write_text("modified\n")
        status = collect_repo_status(self.repo)
        self.assertTrue(status.dirty)
        self.assertEqual(status.modified, 1)

    def test_detached_head_branch_is_empty(self) -> None:
        log = git("log", "--format=%H", cwd=self.repo)
        sha = log.stdout.strip().splitlines()[0]
        git("checkout", "--detach", sha, cwd=self.repo)
        status = collect_repo_status(self.repo)
        self.assertEqual(status.branch, "")

    def test_no_tracking_when_no_remote(self) -> None:
        status = collect_repo_status(self.repo)
        self.assertFalse(status.tracking)
        self.assertEqual(status.ahead, 0)
        self.assertEqual(status.behind, 0)

    def test_ahead_behind_with_remote(self) -> None:
        remote = Path(self._tmp) / "remote.git"
        git("init", "--bare", "-b", "main", str(remote))
        git("remote", "add", "origin", str(remote), cwd=self.repo)
        git("push", "-u", "origin", "main", cwd=self.repo)

        commit_file(self.repo, "local.txt", "local\n", "local commit")

        other = Path(self._tmp) / "other"
        git("clone", str(remote), str(other))
        configure_identity(other)
        commit_file(other, "remote.txt", "remote\n", "remote commit")
        git("push", cwd=other)
        git("fetch", "origin", cwd=self.repo)

        status = collect_repo_status(self.repo)
        self.assertTrue(status.tracking)
        self.assertEqual(status.ahead, 1)
        self.assertEqual(status.behind, 1)


if __name__ == "__main__":
    unittest.main()
