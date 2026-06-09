# Changelog

All notable changes to gstree are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and gstree adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [0.1.1] - 2026-06-09

### Added

- Version management policy defined in ADR-001 (SemVer, changelog, bump workflow)
- `gstree upgrade` command — `git pull` + `uv tool upgrade --reinstall` in one step
  - Source path defaults to `~/source/gstree`, overridable via `GSTREE_REPO_PATH`

## [0.1.0] - 2026-05-28

### Added

- Initial MVP release
- Recursive git repository discovery with depth limits
- Tree-like text output with branch and status tokens
- JSON output mode for downstream tooling
- `--dirty` filter to show only repositories with changes
- `--version` flag for installed binary
- Status tokens: staged (`+N`), modified (`~N`), untracked (`?N`), ahead (`↑N`), behind (`↓N`)
- Zero third-party runtime dependencies (Python stdlib only)
- `uv tool install` / `uv tool upgrade` packaging

[Unreleased]: https://github.com/tmsjngx0/gstree/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.1
[0.1.0]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.0
