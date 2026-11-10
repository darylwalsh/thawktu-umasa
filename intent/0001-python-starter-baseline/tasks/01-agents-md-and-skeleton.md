# 01 — AGENTS.md and repo skeleton

## Context
The repo contains only `REVIEW.md` and this work folder (bootstrap commit,
D0). Read `../intent.md`, `../spec.md` (especially Project layout and
AGENTS.md invariants) and `../decisions.md`. No tooling exists yet. Tasks
02–09 build it.

## Goal
Give every later agent session the context it needs: `AGENTS.md` as the
single source of repo rules, `CLAUDE.md` as a pointer to it, the `intent/`
conventions, and a minimal skeleton of non-code files.

## Scope
In:
- **`AGENTS.md`**, about one page (target ≤ 80 lines; the agent reads all of
  it at the start of every session, so anything stale costs context).
  Sections:
  - Purpose (2–3 lines).
  - **Commands**: one line per mise task from `spec.md` → Tasks, marked
    "(from NN)" until the task that ships it removes the mark. Keep it to
    the command and a few words; details live in the spec.
  - **Verifying your work**: run `mise run check` before reporting any task
    complete and paste the output; if a test fails, fix the code, not the
    test. (Becomes runnable in 02–03.)
  - **Conventions**: Python (src layout, strict typing, ignore-comment
    style, no network in tests); commits (Conventional Commits, allowed
    types `feat fix docs style refactor perf test build ci chore revert`;
    scopes optional).
  - **Invariants**: the nine items from `spec.md` → AGENTS.md invariants,
    word for word in meaning.
  - **Active work**: `intent/0001-python-starter-baseline/`.
  - **Git conventions**: never `--no-verify`; never force-push `main`; one
    task per branch/PR; never disable Claude Code hooks.
  - **Things agents get wrong**: an empty list, kept for the REVIEW.md
    feedback loop.
- **`CLAUDE.md`**: exactly `@AGENTS.md` plus one comment line saying why.
- **`intent/README.md`**: index table with row 0001 (`accepted`), status
  values (`draft | accepted | active | shipped | superseded | abandoned`) and
  folder conventions, including how each stage's artifact triggers the next
  (accepted intent → spec; approved spec → plan mode; merged PR → pipeline).
  Adapt the TS starter's version.
- **`intent/_template/`**: `intent.md`, `spec.md`, `plan.md`,
  `decisions.md`, `tasks/00-task-template.md`. Adapt the TS starter's
  templates. The intent template has the playbook's sections: Problem,
  Outcome, Affected users and systems, Constraints, Open questions, plus
  Done criteria and Non-goals. Its guidance says intent stays in the
  originator's words (what and why); tool choices belong in the spec. The
  spec template has a "Risks and areas of concern" section.
- **`.gitignore`**: `.venv/`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`,
  `.ruff_cache/`, `.coverage*`, `htmlcov/`, `dist/`, `build/`, `.env`,
  `mise.local.toml`, `fnox.local.toml`, `.claude/settings.local.json`.
- **`.editorconfig`** (UTF-8, LF, final newline; 4 spaces for `*.py`, 2 for
  `*.{toml,yml,yaml,md,json}`).
- **`README.md`** stub: one paragraph plus "Status: under construction, see
  `intent/0001-python-starter-baseline/`".
- **`LICENSE`** using the license the owner chose (see `../plan.md` → Before
  task 01).
- **`docs/decisions/0000-use-adrs.md`** (MADR format): why this repo keeps
  ADRs for choices that generated projects inherit.

Out:
- `mise.toml`, `pyproject.toml`, any Python code, git hooks, `.claude/`
  settings, CI (02–05).
- Changing `REVIEW.md` or this work folder, except the `plan.md` status row.

## Steps
1. Draft `AGENTS.md` from the spec. Check every invariant against
   `spec.md` and flag any you had to reword.
2. Create `CLAUDE.md`, `intent/README.md` and `intent/_template/`.
3. Create the remaining skeleton files.
4. Set this task's row in `plan.md` to `in review`.

## Acceptance
- Every file listed under Scope → In exists. No other files changed.
- `AGENTS.md` lists all nine invariants and every planned mise task, and is
  80 lines or fewer (or the report explains the overrun).
- `CLAUDE.md` contains nothing beyond the pointer and its comment.
- `intent/README.md` links to the 0001 folder and the template.
- Commits are conventional (for example `docs(agents): add AGENTS.md`).

## Stop and ask if
- An invariant in `spec.md` conflicts with `REVIEW.md` or `intent.md`.
- The license wasn't provided.
- `AGENTS.md` can't fit the required content in about 100 lines.

## Report
File list, `AGENTS.md` line count, any invariant you reworded (before and
after), and proposed `decisions.md` entries (none expected).
