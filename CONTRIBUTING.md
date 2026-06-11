# Contributing

## Setup

```bash
git clone https://github.com/tmsjngx0/gstree.git
cd gstree
uv sync
```

## Running Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Making Changes

- Follow TDD: write a failing test first, then implement.
- Keep commits small and focused.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

## Submitting a PR

1. Fork the repo and create a branch from `main`.
2. Add tests for any new behaviour.
3. Ensure all tests pass.
4. Open a pull request — describe what changed and why.

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when opening an issue.
