# Changelog

All notable changes to `gstree` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and `gstree` adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2026-06-17

### Added

- GitHub Actions workflow for Trusted Publisher-based TestPyPI and PyPI releases

### Changed

- `gstree --upgrade` now routes through the right path for source checkouts and published `pip` and `uv` installs
- README now distinguishes PyPI, `uv tool install`, `uvx`, and source-checkout upgrade flows

### Fixed

- Skip unreadable directories during workspace scans instead of exiting with a permission error

## [0.1.2] - 2026-06-09

### Added

- `--fetch` flag runs `git fetch --all` in the repo before collecting status
- Parallel status collection via `ThreadPoolExecutor` for multi-repo speedups

### Fixed

- HTTPS remotes no longer hang on credential prompts (`GIT_TERMINAL_PROMPT=0`)
- Ctrl+C prints a clean `gstree: interrupted` instead of a traceback
- Git subprocesses time out after 30 seconds instead of hanging indefinitely

## [0.1.1] - 2026-06-09

### Added

- Version management policy defined in ADR-001 (SemVer, changelog, bump workflow)
- `gstree upgrade` command for `git pull` plus `uv tool upgrade --reinstall`
- Source path defaults to `~/source/gstree`, overridable via `GSTREE_REPO_PATH`

## [0.1.0] - 2026-05-28

### Added

- Initial MVP release
- Recursive repository discovery with depth limits
- Tree-like text output with branch status tokens
- JSON output mode for downstream tooling
- `--dirty` filter to show only repositories with changes
- `--version` flag for the installed binary
- Status tokens: staged (`+N`), modified (`~N`), untracked (`?N`), ahead (`↑N`), behind (`↓N`)
- Zero third-party runtime dependencies (Python stdlib only)
- `uv tool install` / `uv tool upgrade` packaging

[Unreleased]: https://github.com/tmsjngx0/gstree/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.4
[0.1.2]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.2
[0.1.1]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.1
[0.1.0]: https://github.com/tmsjngx0/gstree/releases/tag/v0.1.0
