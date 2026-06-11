# gstree

[![CI](https://github.com/tmsjngx0/gstree/actions/workflows/ci.yml/badge.svg)](https://github.com/tmsjngx0/gstree/actions/workflows/ci.yml)

`gstree` scans a workspace directory for git repositories and shows their status as a compact tree.

```
projects
├── aurora       [main] ~2 ?1
├── bonsai       [main] +3 ~1
├── cedar        [main] clean
│   └── roots    [main] ↓2
└── drift        [feat/glow] ~1 ↑1
```

## Features

- Tree view of all git repos in a directory (including submodules)
- Compact status tokens — see at a glance what needs attention
- `--dirty` flag to show only repos with uncommitted changes
- JSON output for scripting and downstream tools
- Zero runtime dependencies
- `gstree upgrade` for self-updating installs

## Status Tokens

| Token | Meaning |
|-------|---------|
| `+N`  | N staged changes |
| `~N`  | N modified tracked files |
| `?N`  | N untracked files |
| `↑N`  | N commits ahead of upstream |
| `↓N`  | N commits behind upstream |
| `clean` | nothing to do |

## Install

**With pip:**

```bash
pip install gstree
```

**With uvx (no install, run directly):**

```bash
uvx gstree ~/source
```

**From source:**

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

# Fetch from remotes before showing status
gstree --fetch ~/source

# JSON output (for scripting)
gstree --json ~/source
gstree -j ~/source

# Limit scan depth (default: 2)
gstree --depth 3 ~/source

# Check version
gstree --version
```

## Upgrade

For source installs:

```bash
gstree upgrade
```

Override the repo path with `GSTREE_REPO_PATH` if you cloned elsewhere:

```bash
GSTREE_REPO_PATH=/custom/path/gstree gstree upgrade
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
