import argparse
import json
import os
import sys
from pathlib import Path

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gstree",
        description="Workspace git scanner and manager",
    )
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Maximum scan depth")
    parser.add_argument("-j", "--json", action="store_true", help="Emit JSON instead of tree output")
    parser.add_argument("--dirty", action="store_true", help="Show only dirty repositories")
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all in each repo before collecting status")
    parser.add_argument("--upgrade", action="store_true", help="Pull latest source and reinstall gstree")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> int:
    try:
        return _run()
    except KeyboardInterrupt:
        sys.stderr.write("gstree: interrupted\n")
        return 130
    except Exception as exc:
        sys.stderr.write(f"gstree: error: {exc}\n")
        return 1


def _run() -> int:
    args = build_parser().parse_args()

    if args.upgrade:
        from .upgrade import cmd_upgrade

        return cmd_upgrade()

    root = Path(args.path).resolve()

    if not root.exists():
        sys.stderr.write(f"gstree: error: directory not found: {root}\n")
        return 1
    if not root.is_dir():
        sys.stderr.write(f"gstree: error: not a directory: {root}\n")
        return 1

    from .renderer import Palette, render_text_report
    from .scanner import scan_workspace

    repos = scan_workspace(root, args.depth, args.fetch)

    if args.dirty:
        repos = [repo for repo in repos if repo.dirty]
    if args.json:
        print(json.dumps({"root": str(root), "repos": [repo.to_dict() for repo in repos]}, indent=2))
    else:
        palette = Palette(color=os.environ.get("NO_COLOR") is None)
        print(render_text_report(root, repos, palette))
    return 0
