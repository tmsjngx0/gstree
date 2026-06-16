# gstree

[![CI](https://github.com/tmsjngx0/gstree/actions/workflows/ci.yml/badge.svg)](https://github.com/tmsjngx0/gstree/actions/workflows/ci.yml)

`gstree` scans a workspace directory for Git repositories and shows their status
as a compact tree.

```text
projects
├── aurora [main] ~2 ?1
├── bonsai [main] +3 ~1
├── cedar [main] clean
│   └── roots [main] ↓2
└── drift [feat/glow] ~1 ↑1
```

## Features

- Tree view for all Git repos in a directory, including submodules
- Compact status tokens for staged, modified, untracked, ahead, and behind state
- `--dirty` flag to show only repositories with uncommitted changes
- JSON output for downstream scripting
- Zero runtime dependencies beyond Python stdlib and `git`
- `gstree upgrade` for source-installed checkouts

## Status Tokens

| Token | Meaning |
|-------|---------|
| `+N` | N staged changes |
| `~N` | N modified tracked files |
| `?N` | N untracked files |
| `↑N` | N commits ahead of upstream |
| `↓N` | N commits behind upstream |
| `clean` | Nothing to do |

## Install

**Published release (PyPI):**

```bash
pip install gstree
```

**Published release with `uvx` (no install):**

```bash
uvx gstree ~/source
```

**From source (current checkout / unreleased main):**

```bash
git clone https://github.com/tmsjngx0/gstree.git ~/.local/share/gstree
uv tool install ~/.local/share/gstree
```

## Usage

```bash
# Show all repos
gstree ~/source

# Show only repos with changes
gstree --dirty ~/source

# Fetch remotes before showing status
gstree --fetch ~/source

# JSON output for scripting
gstree --json ~/source
gstree -j ~/source

# Limit scan depth (default: 2)
gstree --depth 3 ~/source

# Check version
gstree --version
```

## Upgrade

For source installs from a cloned checkout:

```bash
gstree upgrade
```

Override the repo path with `GSTREE_REPO_PATH` if you cloned elsewhere:

```bash
GSTREE_REPO_PATH=/custom/path/gstree gstree upgrade
```

## Release

Tagged releases publish to PyPI through GitHub Actions Trusted Publishing.
Use the publish workflow's manual dispatch to test against TestPyPI before
pushing a release tag.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
