# gstree

`gstree` is a Python CLI that scans a workspace for git repositories and shows
their status either as JSON or as a compact tree view.

## Current MVP

- Recursive repository discovery with depth limits
- JSON output for downstream tools
- Default text/tree output with a dirty summary
- Branch, dirty, tracking, ahead, and behind metadata
- Zero third-party runtime dependencies
- Direct `--version` output for installed binaries

## Run From Checkout

```bash
uv run gstree ~/source
uv run gstree --json ~/source
```

If you are not using `uv run`, the direct module path still works:

```bash
PYTHONPATH=src python3 -m gstree ~/source
PYTHONPATH=src python3 -m gstree --json ~/source
```

## Install

Install the tool from the local checkout:

```bash
uv tool install /data/source/gstree-mgmt/gstree
```

For an editable development install:

```bash
uv tool install --editable /data/source/gstree-mgmt/gstree
```

Verify the installed binary:

```bash
gstree --version
gstree ~/source
```

If `uv` warns that the tool bin directory is not on your `PATH`, add the
reported directory to `PATH` or run `uv tool update-shell`.

## Upgrade

After pulling new changes into the checkout, reinstall the tool environment:

```bash
uv tool upgrade gstree --reinstall
```

## Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
