# 02 — Toolchain: mise + uv + package skeleton

## Context
Task 01 added `AGENTS.md` and the skeleton. Read `AGENTS.md`, then
`../spec.md` → Toolchain (who installs what, Python version, project layout)
and D1 in `../decisions.md`. This task answers **Q10** (Python 3.15 or 3.14).

Decided, don't revisit: mise provisions Python and uv; uv owns dependencies,
the venv and `uv.lock` (D1).

## Goal
`mise install && mise run setup && mise run run` works on a clean clone and
prints the package name and version, using mise's Python and a uv-managed
`.venv`.

## Scope
In:
- **Q10 spike first:** Python 3.15.0 was released on 2026-10-09. Check PyPI
  for `pydantic-core` wheels on CPython 3.15 for linux x86_64, linux aarch64
  and macOS arm64, and confirm the latest `pydantic` declares 3.15 support.
  Use 3.15 if all are present, otherwise 3.14. Record the evidence (wheel
  filenames, release links).
- **`mise.toml`**:
  - `[tools]`: `python` (exact patch) and `uv` (exact). Later tasks add
    their own tools.
  - `[settings]`: auto-activate `.venv` (`python.uv_venv_auto` or the
    pinned mise's equivalent).
  - `[env]`: `UV_PYTHON` points at mise's interpreter, and
    `UV_PYTHON_DOWNLOADS = "never"` so uv never fetches its own Python.
  - `[tasks]`: `setup` (`uv sync --locked`) and `run`
    (`uv run python -m python_starter`). No placeholder tasks.
- **`pyproject.toml`** from `uv init --package --build-backend uv` (or the
  pinned uv's equivalent):
  - name `python-starter`, import package `python_starter`,
    `version = "0.1.0"`.
  - `requires-python = ">=<chosen minor>"`.
  - runtime dependency `pydantic` with a compatible range (`>=2.N,<3`);
    `uv.lock` holds the exact version.
- **`src/python_starter/`**:
  - `__init__.py`: `__version__` from `importlib.metadata`.
  - `__main__.py`: prints `python-starter <version>` and exits 0.
  - `models.py`: one small pydantic v2 model with typed fields, one
    validator, and a `from_dict` helper using `model_validate`. Fully
    annotated, so task 03 can prove pyright strict.
- Commit `uv.lock`. Add `.python-version` only if the pinned uv needs it
  alongside mise (report which).
- Update `AGENTS.md` → Commands: remove the "(from 02)" mark on `setup` and
  `run`.

Out:
- Ruff, pyright, pytest and their config (03). Git hooks, Claude Code hooks,
  secrets, commitizen (04). CI (05).
- Any dependency beyond `pydantic`.

## Steps
1. Run the Q10 spike and choose the version.
2. Write `mise.toml`. Run `mise install`, then
   `mise exec -- python --version` and confirm the exact pin.
3. Generate `pyproject.toml` and the package. Run `uv lock`, then
   `mise run setup`.
4. Prove the wiring:
   - `uv run python -c "import sys; print(sys.executable, sys.version)"`
     shows `.venv` built from mise's interpreter.
   - With mise's Python temporarily removed from `PATH`, uv fails instead of
     downloading one. That shows `UV_PYTHON_DOWNLOADS=never` works.
   - `mise run run` prints `python-starter 0.1.0`.
5. Do a fresh clone into a temp directory and repeat
   `mise install && mise run setup && mise run run`.

## Acceptance
- The clean-clone sequence passes. Paste the output.
- `uv sync --locked` succeeds, and `uv lock --check` reports up to date.
- No `latest` or ranges in `mise.toml`.
- Q10 answered with evidence, ready to paste into `decisions.md`.

## Stop and ask if
- pydantic-core has no wheels for 3.15 *or* 3.14 on any of the three
  platforms.
- uv downloads a Python despite the settings, or mise and uv disagree on the
  interpreter.
- The pinned mise has no venv auto-activation setting.

## Report
Pins (python, uv, pydantic), Q10 evidence and answer, the exact mise
settings used, clean-clone output, and proposed `decisions.md` entries.
