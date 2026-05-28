import argparse
import json
from pathlib import Path

from .renderer import render_text_report
from .scanner import scan_workspace


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gstree")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("-d", "--depth", type=int, default=2)
    parser.add_argument("-j", "--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = Path(args.path).resolve()
    repos = scan_workspace(root, args.depth)
    if args.json:
        print(json.dumps({"root": str(root), "repos": [repo.to_dict() for repo in repos]}, indent=2))
    else:
        print(render_text_report(root, repos))
    return 0
