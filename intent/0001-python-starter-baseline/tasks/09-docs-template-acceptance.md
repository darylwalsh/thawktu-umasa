# 09 — Docs, template readiness, end-to-end acceptance

## Context
Everything in `../spec.md` is built (01–08). Read `../intent.md` → Done
criteria, `../plan.md` → Done-criteria traceability, and `../decisions.md`.

## Goal
Someone new can use the repo as a template from the README alone, and a
generated repo is green without any agent setup. Every intent done criterion
has evidence, and 0001 can be marked `shipped` once two scheduled Tuesday
reports have landed.

## Scope
In:
- **`README.md`**:
  - What this is, and the stack table (mise, uv, Ruff, pyright, pytest,
    lefthook, Claude Code hooks, gitleaks, fnox/age, commitizen, gh-aw +
    Claude).
  - **Using this template:** "Use this template" on GitHub, then the rename
    steps (`python-starter` / `python_starter` in `pyproject.toml`, `src/`,
    tests, README), then reset the version and `CHANGELOG.md`, then replace
    the `fnox.toml` recipient.
  - **Agent workflows are opt-in (D21):** a generated repo's CI is green
    with no Apps or secrets. To turn agents on: create the Apps, add the
    secrets, set `AGENTS_ENABLED = true`, update the ruleset. Say which
    workflows a generated project would usually keep (pr-review, issue
    workers) and which it would usually delete (tooling watch, merge
    guard), and what each one needs.
  - **Commands:** link to `AGENTS.md` → Commands rather than duplicating it.
  - **Agent workflows in this repo:**
    - The weekly report lands on `main` every Tuesday morning in
      `reports/tooling-watch/`; its facts are script-collected and
      machine-checked.
    - Recommended changes arrive as `[tooling-watch]` issues.
    - `hold` stops an auto-merge.
    - **The watchlist is human-maintained**: how to add an entry and, if
      Q16 needs it, its network host.
    - How to hand an issue to the agent (`agent:ready`), and what comes
      back for bugs and for features.
    - Changing the agents' configuration: run or link the evals.
  - **How this repo is developed:** intent → spec → plan → reviewed PR, with
    links to `intent/` and `REVIEW.md`.
- **ADRs in `docs/decisions/`** (MADR) for choices generated projects
  inherit, linked from the `decisions.md` Source column:
  - `0001` toolchain (D1–D3);
  - `0002` git hooks, Claude Code hooks, commits, releases, secrets (D4–D6,
    D14, D19);
  - `0003` agent workflows, evals, report auto-merge and the agent switch
    (D7–D11, D15–D18, D20, D21).
- `intent/README.md` and the 0001 `intent.md` status.
- Close out `decisions.md`: every Q answered or explicitly deferred to a
  named future intent (for example copier template, Python version matrix,
  second reviewer).

Out:
- New features or tooling changes. If you find a defect, file an issue and
  don't fix it here.

## Steps
1. Write the README and ADRs.
2. **Clean-clone verification:**
   - On Linux, in a fresh clone: `mise install`, `mise run setup`,
     `mise run check`, `mise run run`, with no secrets present.
   - On macOS: the same. If the agent can't run macOS, write the exact
     commands into the report and ask the owner to run them and paste the
     output into the PR.
3. **Template dry run:** create a throwaway repo from the template (after
   the owner turns on "Template repository"), follow the README rename
   steps literally, push, and confirm CI is green with no secrets and no
   `AGENTS_ENABLED`. Note every step that wasn't obvious and fix the README.
   Delete the throwaway repo afterwards.
4. Fill in the evidence column of the traceability table in `../plan.md`
   with links to runs and PRs.
5. List the scheduled tooling-watch runs since 07 merged. Once two
   consecutive Tuesdays have auto-merged, set the 0001 status to `shipped`
   in `intent.md` and `intent/README.md`. Until then, set it to `active`
   with a note "awaiting second scheduled report".

## Acceptance
- The README alone gets a template user to a green `mise run check` and a
  green CI run with no agent setup (proven by the dry run).
- Linux and macOS clean-clone outputs are attached to the PR.
- Every row of the traceability table has evidence.
- No open Q in `decisions.md` without an answer or a named deferral.
- Status updated in both `intent.md` and `intent/README.md` in the same
  commit.

## Stop and ask if
- Any done criterion can't be evidenced.
- The template dry run needs a step the README can't reasonably explain
  (that probably means a design gap, so propose a follow-up intent).

## Report
Traceability table with evidence, OS outputs, template dry-run notes, the
list of scheduled run links, the final status, and suggested next intents
(for example a copier template, framework variants such as FastAPI or
Quart, or a second reviewer).
