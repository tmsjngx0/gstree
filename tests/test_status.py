import unittest

from gstree.status import parse_porcelain


class ParsePorcelainTest(unittest.TestCase):
    def test_empty_returns_zeros(self) -> None:
        self.assertEqual(parse_porcelain([]), (0, 0, 0))

    def test_untracked_file(self) -> None:
        self.assertEqual(parse_porcelain(["?? new.txt"]), (0, 0, 1))

    def test_multiple_untracked(self) -> None:
        self.assertEqual(parse_porcelain(["?? a.txt", "?? b.txt"]), (0, 0, 2))

    def test_staged_new_file(self) -> None:
        # A  = new file staged, no worktree change
        self.assertEqual(parse_porcelain(["A  file.txt"]), (1, 0, 0))

    def test_staged_modification(self) -> None:
        # M  = index modified, worktree clean
        self.assertEqual(parse_porcelain(["M  file.txt"]), (1, 0, 0))

    def test_worktree_modification_only(self) -> None:
        # ' M' = not staged, worktree modified
        self.assertEqual(parse_porcelain([" M file.txt"]), (0, 1, 0))

    def test_staged_and_worktree_modification_same_file(self) -> None:
        # MM = staged change + additional worktree change
        self.assertEqual(parse_porcelain(["MM file.txt"]), (1, 1, 0))

    def test_staged_deletion(self) -> None:
        # D  = deletion staged
        self.assertEqual(parse_porcelain(["D  file.txt"]), (1, 0, 0))

    def test_worktree_deletion(self) -> None:
        # ' D' = file deleted in worktree, not staged
        self.assertEqual(parse_porcelain([" D file.txt"]), (0, 1, 0))

    def test_mix_of_all_states(self) -> None:
        lines = [
            "M  staged.txt",      # staged
            " M modified.txt",    # worktree modified
            "MM both.txt",        # staged + worktree modified
            "?? untracked.txt",   # untracked
        ]
        staged, modified, untracked = parse_porcelain(lines)
        self.assertEqual(staged, 2)       # M  and MM
        self.assertEqual(modified, 2)     # ' M' and MM
        self.assertEqual(untracked, 1)


if __name__ == "__main__":
    unittest.main()
