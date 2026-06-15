import unittest
from pathlib import Path

from gstree.models import RepoStatus
from gstree.renderer import Palette, _format_repo_state, render_text_report

P = Palette(color=False)


def _repo(**kwargs) -> RepoStatus:
    defaults = dict(
        name="repo", path="/ws/repo", branch="main",
        dirty=False, tracking=False, ahead=0, behind=0,
    )
    return RepoStatus(**{**defaults, **kwargs})


class PaletteTest(unittest.TestCase):
    def test_color_false_returns_plain_string(self) -> None:
        p = Palette(color=False)
        self.assertEqual(p.green("ok"), "ok")
        self.assertEqual(p.red("err"), "err")
        self.assertEqual(p.yellow("warn"), "warn")

    def test_color_true_wraps_with_ansi(self) -> None:
        p = Palette(color=True)
        self.assertIn("\033[", p.green("ok"))
        self.assertIn("\033[", p.red("err"))
        self.assertIn("\033[", p.yellow("warn"))

    def test_repo_depth_zero_no_color(self) -> None:
        self.assertEqual(P.repo("aurora", 0), "aurora")

    def test_repo_depth_one_no_color(self) -> None:
        self.assertEqual(P.repo("aurora", 1), "aurora")

    def test_dir_leaf_adds_slash(self) -> None:
        self.assertEqual(P.dir("src", 1, leaf=True), "src/")

    def test_dir_non_leaf_no_slash(self) -> None:
        self.assertEqual(P.dir("src", 0, leaf=False), "src")


class FormatRepoStateTest(unittest.TestCase):
    def test_clean_repo(self) -> None:
        self.assertEqual(_format_repo_state(_repo(), P), "clean")

    def test_staged_only(self) -> None:
        self.assertEqual(_format_repo_state(_repo(staged=2), P), "+2")

    def test_modified_only(self) -> None:
        self.assertEqual(_format_repo_state(_repo(modified=1), P), "~1")

    def test_untracked_only(self) -> None:
        self.assertEqual(_format_repo_state(_repo(untracked=3), P), "?3")

    def test_ahead_behind(self) -> None:
        self.assertEqual(_format_repo_state(_repo(ahead=1, behind=2), P), "↑1 ↓2")

    def test_all_tokens(self) -> None:
        repo = _repo(staged=1, modified=2, untracked=3, ahead=1, behind=1)
        self.assertEqual(_format_repo_state(repo, P), "+1 ~2 ?3 ↑1 ↓1")


class RenderTextReportTest(unittest.TestCase):
    def _root(self) -> Path:
        return Path("/ws")

    def test_single_clean_repo(self) -> None:
        repos = [_repo(name="aurora", path="/ws/aurora", branch="main")]
        out = render_text_report(self._root(), repos, P)
        self.assertIn("aurora", out)
        self.assertIn("[main]", out)
        self.assertIn("clean", out)
        self.assertIn("1 repos, 0 dirty", out)

    def test_dirty_summary_count(self) -> None:
        repos = [
            _repo(name="a", path="/ws/a", dirty=True, untracked=1),
            _repo(name="b", path="/ws/b", dirty=False),
        ]
        out = render_text_report(self._root(), repos, P)
        self.assertIn("2 repos, 1 dirty", out)

    def test_empty_branch_renders_brackets(self) -> None:
        repos = [_repo(name="detached", path="/ws/detached", branch="")]
        out = render_text_report(self._root(), repos, P)
        self.assertIn("[]", out)

    def test_nested_repo_indented(self) -> None:
        repos = [
            _repo(name="parent", path="/ws/parent"),
            _repo(name="child", path="/ws/parent/child"),
        ]
        out = render_text_report(self._root(), repos, P)
        lines = out.splitlines()
        parent_line = next(ln for ln in lines if "parent" in ln and "child" not in ln)
        child_line = next(ln for ln in lines if "child" in ln)
        self.assertLess(lines.index(parent_line), lines.index(child_line))
        self.assertIn("└──", child_line)


if __name__ == "__main__":
    unittest.main()
