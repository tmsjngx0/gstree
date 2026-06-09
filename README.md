# gstree

`gstree` is a Python CLI that scans a workspace for git repositories and shows
their status either as JSON or as a compact tree view.

## Current MVP

- Recursive repository discovery with depth limits
- JSON output for downstream tools
- Default text/tree output with a dirty summary
- Compact status tokens for staged, modified, untracked, ahead, and behind state
- `--dirty` filtering for attention-only views
- Branch, dirty, tracking, ahead, and behind metadata
- Zero third-party runtime dependencies
- Direct `--version` output for installed binaries

## Status Tokens

- `+N` staged changes
- `~N` modified tracked files
- `?N` untracked files
- `↑N` commits ahead of upstream
- `↓N` commits behind upstream

## Run From Checkout

```bash
uv run gstree ~/source
uv run gstree --dirty ~/source
uv run gstree --json ~/source
```

If you are not using `uv run`, the direct module path still works:

```bash
PYTHONPATH=src python3 -m gstree ~/source
PYTHONPATH=src python3 -m gstree --dirty ~/source
PYTHONPATH=src python3 -m gstree --json ~/source
```

## Install

Clone the repo into your normal source workspace:

```bash
git clone git@github.com:tmsjngx0/gstree.git ~/source/gstree
```

Install the tool from that checkout:

```bash
uv tool install ~/source/gstree
```

For an editable development install:

```bash
uv tool install --editable ~/source/gstree
```

Verify the installed binary:

```bash
gstree --version
gstree ~/source
gstree --dirty ~/source
```

If `uv` warns that the tool bin directory is not on your `PATH`, add the
reported directory to `PATH` or run `uv tool update-shell`.

## Upgrade

After pulling new changes into the checkout, reinstall the tool environment:

```bash
git -C ~/source/gstree pull
uv tool upgrade gstree --reinstall
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
