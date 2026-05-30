import argparse
import json
from pathlib import Path

from . import __version__
from .renderer import render_text_report
from .scanner import scan_workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gstree")
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Maximum scan depth")
    parser.add_argument("-j", "--json", action="store_true", help="Emit JSON instead of tree output")
    parser.add_argument("--dirty", action="store_true", help="Show only dirty repositories")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.path).resolve()
    repos = scan_workspace(root, args.depth)
    if args.dirty:
        repos = [repo for repo in repos if repo.dirty]
    if args.json:
        print(json.dumps({"root": str(root), "repos": [repo.to_dict() for repo in repos]}, indent=2))
    else:
        print(render_text_report(root, repos))
    return 0
