# gstree

`gstree` is a Python CLI that scans a workspace for git repositories and shows
their status either as JSON or as a compact tree view.

## Current MVP

- Recursive repository discovery with depth limits
- JSON output for downstream tools
- Default text/tree output with a dirty summary
- Branch, dirty, tracking, ahead, and behind metadata
- Zero third-party runtime dependencies

## Usage

```bash
PYTHONPATH=src python3 -m gstree --json ~/source
PYTHONPATH=src python3 -m gstree ~/source
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
