# Repository Guidelines

## Project Structure & Module Organization
- `boxes/`: core library (geometry helpers, joints, QR/gear/pulley utilities) plus CLI entry points in `boxes/scripts` and generator definitions in `boxes/generators` (one module per generator, snake_case file + CamelCase class).
- `scripts/`: operational tooling such as `boxesserver`, `boxes_proxy.py`, `boxes2inkscape`, translation helpers, and container assets (`Dockerfile`).
- `examples/`: canonical SVG outputs for each generator; treated as golden files.
- `tests/`: pytest suite (`tests/test_svg.py`) writes rendered SVGs to `tests/data/` and compares them to `examples/*.svg`.
- `documentation/src`: Sphinx sources; built HTML lands in `documentation/build/html`. Static art lives in `static/`, translations in `po/` and `locale/`.

## Setup, Build & Development Commands
- Activate the project's virtualenv before running any `python`/`pip` commands.
- Install with dev extras: `python -m pip install -e ".[dev]"`.
- Inspect or regenerate SVGs: `boxes --list` to enumerate generators; `boxes --examples` refreshes `examples/*.svg` for all defaults.
- Serve the web UI: run `scripts/boxesserver` (or `docker-compose up` for hot reload at http://localhost:4455/).
- Build docs: `make html` from `documentation/src`; output goes to `documentation/build/html`.

## Testing Guidelines
- Run `pytest` from the repo root; tests validate SVG XML via `lxml` and expect silent stdout/stderr.
- Intentional generator changes should also refresh `examples/*.svg` (use `boxes --examples`) and commit the updated files alongside code.
- Add focused coverage for new generators by extending `tests/test_svg.py` and placing expected outputs in `examples/`.

## Coding Style & Naming Conventions
- Target Python 3.10+, 4-space indentation, and pervasive type annotations; mypy runs via pre-commit with strict checks over `boxes/` and key scripts.
- Run `pre-commit run --all-files` before pushing (trailing whitespace, YAML/TOML sanity, pyupgrade, autoflake, codespell, rstcheck, shellcheck).
- Generator modules use snake_case filenames; generator classes use CamelCase matching example names (e.g., `angledbox.py` → `AngledBox` with `examples/AngledBox.svg`).

## Commit & Pull Request Guidelines
- Keep commits small and imperative; recent history favors messages like `Fix ...` or `build(deps): ...`. Rebase on `master`/`main` before opening a PR.
- PRs should summarize intent, link issues, and call out any regenerated examples or static assets; include photos for new generators in `static/samples`.
- Keep feature branches focused and update documentation/tests/examples together for each change set.

## Security & Configuration Tips
- Avoid new dependencies unless necessary; when required, update `requirements.txt`, `pyproject.toml`, and relevant install docs.
- Use `BOXES_GENERATOR_PATH` to load local custom generators without modifying the repository.
