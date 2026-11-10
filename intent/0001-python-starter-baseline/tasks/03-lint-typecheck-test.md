# 03 — Lint, format, type check, tests

## Context
Task 02 delivered mise + uv and the `python_starter` package with a pydantic
model. Read `AGENTS.md`, `../spec.md` → Tool configuration and Tasks, and
D2/D3. This task answers **Q11** (Ruff rules, coverage threshold) and
**Q12** (how to block network in tests).

Decided, don't revisit: Ruff for lint + format (D2); **pyright strict**,
installed as `pyright[nodejs]` through uv, not Node in mise (D3); pytest +
pytest-cov (D2).

## Goal
`mise run check` runs format check, lint, strict type check, tests with
coverage, and the lockfile check, all passing with zero warnings.

## Scope
In:
- uv `dev` dependency group, each with an `==` pin: `ruff`,
  `pyright[nodejs]`, `pytest`, `pytest-cov`, plus `pytest-socket` if Q12
  goes that way.
- `pyproject.toml` config:
  - `[tool.ruff]`: `target-version` matching `requires-python`, an explicit
    `lint.select` list (not `ALL`), and per-file ignores for `tests/` only,
    each with a comment.
  - `[tool.pyright]`: as in the spec (`strict`, `venvPath`/`venv`,
    `reportUnnecessaryTypeIgnoreComment = true`). `include` lists the
    directories that exist now (`src`, `tests`); later tasks add `scripts`,
    `.claude/hooks` and `evals` as they create them.
  - `[tool.pytest.ini_options]`: `testpaths`, `--strict-markers`,
    `--strict-config`, coverage on `src/`.
  - `[tool.coverage.report]`: `fail_under` (Q11), `show_missing = true`.
    Later tasks add `scripts/` to coverage when they add scripts.
- **Tests:** `tests/test_main.py` (output and exit code of
  `python -m python_starter`, via subprocess or `runpy`) and
  `tests/test_models.py` (valid input, validation error, validator
  behavior, round-trip).
- **Network blocking (Q12):** pick a `conftest.py` socket guard or
  `pytest-socket`, and prove that a test opening a socket fails.
- mise tasks: `fmt`, `fmt:check`, `lint`, `lint:fix`, `typecheck`, `test`,
  `lock:check`, and `check`, which runs them in that order and fails fast.
- Update `AGENTS.md` → Commands (remove the "(from 03)" marks).

Out:
- Git hooks and Claude Code hooks (04), CI (05).
- Changing `models.py` behavior. Typing fixes are fine; behavior changes
  are not.

## Steps
1. Add the dev dependencies with `uv add --dev` and pin them exactly.
2. Configure Ruff. Choose the rule set by running it on the package, and
   write one line of reasoning per selected family.
3. Configure pyright and run `mise run typecheck`.
4. **Pydantic proof:** on a scratch branch, add deliberate misuses and
   confirm pyright strict reports each one: a wrong field type in the
   constructor, a missing required field, and attribute access on a
   non-existent field. Paste the diagnostics, then delete the branch.
5. **Offline proof:** after `mise run setup`, run `mise run typecheck` with
   networking disabled (for example `unshare -rn` on Linux, or an invalid
   `HTTPS_PROXY`). It must pass, which shows pyright downloads nothing at
   run time.
6. Write the tests and set `fail_under` from the measured baseline (target
   ≥ 90).
7. Run `mise run check` on a fresh clone.

## Acceptance
- `mise run check` passes with zero warnings. Paste the output.
- The pydantic misuse diagnostics and the offline typecheck run are shown in
  the report.
- No `# type: ignore` or `# pyright: ignore` in `src/`. Any in `tests/`
  name the rule and give a reason.
- A deliberately stale `uv.lock` (bump a pin in `pyproject.toml` without
  locking, on a scratch branch) makes `lock:check` fail.
- Q11 and Q12 answered.

## Stop and ask if
- pyright tries to download Node or npm packages at run time, even with
  `[nodejs]`. Fallback per spec R4: `npm:pyright` + Node in mise. That needs
  a decision entry and owner approval.
- Strict mode forces ignores in `src/` because of pydantic.
- Coverage can't reach 90% without testing trivia.

## Report
Pins, the Ruff rule list with reasons, Q11 and Q12 answers, the pydantic and
offline proofs, `mise run check` output, and proposed `decisions.md`
entries.
