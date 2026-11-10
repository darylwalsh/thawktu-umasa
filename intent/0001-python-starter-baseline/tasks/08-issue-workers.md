# 08 — Issue workers (bug and feature) and the test-first check

## Context
The PR review agent, evals and tooling watch are live (06–07). Read
`AGENTS.md` (Invariants 2, 4, 5), `REVIEW.md` → Issue-worker PRs,
`../spec.md` → Issue workers, and D11/D14/D17. Use the Q19 answer from task
07 for pre-agent steps. This task answers **Q17b** (label-removal output).

Decided, don't revisit: an agent acts only on issues where a maintainer
applied `agent:ready`. Bugs get a failing test first, then the fix; features
get an `intent.md`-only PR (D11). There are **two workflows**, each
path-locked with `allowed-files` and `protected-files: blocked`, and bug PRs
are checked by a deterministic `test-first` job (D17).

## Goal
A maintainer can label a triaged issue `agent:ready` and get back a PR that
follows the bug or feature path, or a comment explaining why the agent
declined. The bug path's test-first rule is proven by CI, not by trust.

## Scope
In:
- **Issue forms:** `.github/ISSUE_TEMPLATE/bug.yml` (auto-label `type:bug`;
  fields for steps to reproduce, expected, actual, version) and
  `feature.yml` (auto-label `type:feature`; fields for problem, desired
  outcome, out of scope). `config.yml` with `blank_issues_enabled: false`.
- **Shared** (both workflows, via the 06 fragment plus an issue-worker
  fragment if useful):
  - Trigger `issues: [labeled]`; continue only when the label just applied
    is `agent:ready` and the issue has the workflow's type label. Roles
    limited to admin, maintainer and write.
  - Don't-pile-on pre-check: `noop` and a comment if three or more agent PRs
    are open or `ci` is red on `main`.
  - Decline path: protected files (per spec) or a secret needed → comment
    why, remove `agent:ready` (Q17b), no PR.
  - safe-outputs: `create-pull-request` (`draft: true`, `max: 1`,
    `protected-files: blocked`, workflow-specific `allowed-files`),
    `add-comment` (`max: 3`), label removal, `noop`.
- **`.github/workflows/issue-worker-bug.md`**:
  - Pre-agent steps: `mise install` and `mise run setup`, so the agent can
    run `mise run check` with only the base network allowlist (Q19).
  - Path: commit 1 is `test: reproduce #N`, touching only `tests/`, with a
    failing test → set `STARTER_FIX_MODE=1` (the Claude Code hook then
    blocks edits to tracked tests) → fix in later commits → `mise run check`
    green → PR labelled `type:bug`, body says `Fixes #N` and shows the
    failing output before the fix and the passing output after.
  - `allowed-files: ["src/**", "tests/**"]`.
  - `timeout-minutes: 30`, `max-turns: 120`.
- **`.github/workflows/issue-worker-feature.md`**:
  - Path: next free `intent/NNNN-slug/` from `_template/`, with `intent.md`
    filled from the issue form, plus the `intent/README.md` index row. PR
    body says `Refs #N`, not `Fixes`.
  - `allowed-files: ["intent/*/intent.md", "intent/README.md"]`.
  - `timeout-minutes: 15`, `max-turns: 60`.
- **`scripts/check_test_first.py`** with tests, and a **`test-first` job**
  in `ci.yml`: for PRs labelled `type:bug` opened by the starter-bot App,
  apply the four rules in `../spec.md` → `test-first` check; for every other
  PR, succeed with "not applicable". Tests use small throwaway git repos
  built in a temp directory.
- `AGENTS.md`: a short "Working an issue" section that matches the three
  paths and mentions fix mode.
- `docs/github-setup.md`: "add `test-first` to required checks after this
  merges".

Out:
- Auto-triage or auto-labelling of new issues. A human always applies
  `agent:ready`.
- Changes to `pr-review` or the merge guard.

## Steps
1. Write the issue forms.
2. Write `check_test_first.py` and its tests, then the `test-first` job.
3. Write and compile both issue-worker workflows. Settle Q17b.
4. **Proofs**, using real issues and closing them afterwards:
   - **Bug:** pick an actual edge case (for example
     `python -m python_starter --bogus` should exit 2 with a usage message),
     file it with `bug.yml`, label it `agent:ready`. Expect a PR whose first
     commit is a failing test, a later fix commit, the test unchanged, and
     `ci`, `test-first` and `pr-review` green.
   - **Test-first negative:** on a throwaway branch, push a "bug PR" whose
     fix commit also edits the reproducing test's assertion. Expect
     `test-first` = failure with the reason.
   - **Feature:** file "add a `--json` output flag" with `feature.yml`.
     Expect a PR containing only `intent/NNNN-json-output/intent.md` plus
     the index row.
   - **Path lock:** confirm from the feature workflow's compiled config (or
     a scratch run with a prompt that asks for code) that a change under
     `src/` is refused by `allowed-files`, not just avoided by the prompt.
   - **Decline:** file "change REVIEW.md nit cap to 10". Expect a comment,
     the label removed, and no PR.
   - **Pile-on:** with three draft agent PRs open, label a fourth issue.
     Expect `noop` and a comment.
5. Confirm `pr-review` reviewed both proof PRs.

## Acceptance
- All proofs behave as stated, with links.
- The bug PR's commit list shows the test commit first, and `test-first`
  passed on it; the negative case failed `test-first`.
- The feature PR's diff contains only the intent file and the index row,
  and the path lock is shown to be enforced by gh-aw.
- Q17b answered.

## Stop and ask if
- The agent needs write permission on its own job, or a secret.
- Pre-agent steps can't install the toolchain for the agent (Q19), and the
  only alternative is widening the agent's network allowlist.
- The don't-pile-on check can't read PR or CI state with read-only
  permissions.

## Report
Workflow summaries, safe-output names, `test-first` rule table, proof
links, the bug PR commit list, per-run cost, and proposed `decisions.md`
entries.
