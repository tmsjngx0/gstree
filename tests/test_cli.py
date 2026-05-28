import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class GstreeCliJsonTest(unittest.TestCase):
    def test_json_output_lists_git_repositories_under_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo = root / "app"
            subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True, text=True)

            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
            result = subprocess.run(
                [sys.executable, "-m", "gstree", "--json", str(root)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

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


if __name__ == "__main__":
    unittest.main()
