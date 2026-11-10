# Plan: Python starter baseline with agent-maintained tooling

How [`intent.md`](intent.md) gets built, following [`spec.md`](spec.md).
Decisions D0–D21 and open questions Q10–Q21 are in
[`decisions.md`](decisions.md).

## Rules

- Each prompt in [`tasks/`](tasks/) is **one fresh agent session, one branch,
  one PR**. Start Claude Code in **plan mode**, give it the task prompt, let it
  read the repo and interview you, and approve its plan before it writes
  anything. Put anything the plan-mode session changes about the task into
  the task's PR (this file, the task prompt, or `decisions.md`).
- Tasks run in order, and each PR merges before the next task starts. No
  stacked PRs unless the owner asks for them in writing (record it here
  under "Current run").
- Every task ends with `mise run check` green, or the subset that exists at
  that point. Each task adds its own tasks to `check`.
- **Review:** every PR is reviewed against `REVIEW.md` by a session that did
  not write it. Until task 06 ships the `pr-review` agent, start that
  session by hand: a fresh Claude Code session given only the diff,
  `AGENTS.md`, `REVIEW.md` and this folder. From task 06 on, the agent does
  it, and its status is a required check.
- **Guardrails:** from task 04 on, Claude Code hooks in `.claude/settings.json`
  apply to every session in this repo (D14). Don't disable them for a task;
  if one gets in the way, stop and ask.
- **Human approval:** almost every task touches a protected file
  (`AGENTS.md`, `.claude/`, hooks, CI, workflows, secrets config), so a human
  approves every PR in this plan. The only exception is report PRs, which
  arrive after task 07 and auto-merge through the guard (D9).
- **Decisions:** each task's report proposes `decisions.md` entries. Copy
  them in, and answer any Q it closes, before the next task starts.
- **Drift:** if implementation departs from this plan or the spec, update
  `plan.md` (and `decisions.md` if it's a decision) **in the same commit**.
- **Pins:** each task pins the current stable version of every tool it adds,
  as of the day it runs, and reports the pins. No version numbers are
  decided in advance.
- Commit messages follow Conventional Commits from the first commit. The
  hook only enforces them after task 04.

## Before task 01 (human, one time)

- [ ] Create the **public** repository in the org (for example
      `<org>/python-starter`), default branch `main`, with no generated
      README.
- [ ] Choose a license (for example MIT or Apache-2.0) and note it for
      task 01.
- [ ] **Bootstrap commit** on `main`: `REVIEW.md` at the root and this folder
      at `intent/0001-python-starter-baseline/` (`intent.md`, `spec.md`,
      `plan.md`, `decisions.md`, `tasks/`). This commit is the owner's
      acceptance of the intent and approval of the spec (D0). Message:

      ```
      docs(intent): add 0001 python starter baseline

      Intent 0001 accepted and spec approved by the owner (D0).
      ```
- [ ] Have mise and Claude Code installed locally, with access to the repo.

## Phases and tasks

| Phase | Outcome | Task | Branch | Status |
| --- | --- | --- | --- | --- |
| 1. Foundation | Agent context, repo skeleton, ADR habit | [`01`](tasks/01-agents-md-and-skeleton.md) | `docs/agents-md` | todo |
| | mise + uv toolchain, package skeleton, Python version (Q10) | [`02`](tasks/02-toolchain-mise-uv.md) | `build/toolchain` | todo |
| | Ruff, pyright strict + pydantic, pytest (Q11, Q12) | [`03`](tasks/03-lint-typecheck-test.md) | `build/quality` | todo |
| | lefthook, Claude Code hooks, gitleaks, fnox/age, commitizen (Q21) | [`04`](tasks/04-hooks-secrets-commits.md) | `build/hooks` | todo |
| 2. Pipeline | CI, release PR flow, Dependabot, ruleset doc (Q20) | [`05`](tasks/05-ci-release.md) | `ci/pipeline` | todo |
| 3. Agents | gh-aw foundation, PR review agent, eval suite (Q13, Q14, Q17a, Q18) | [`06`](tasks/06-gh-aw-pr-review-evals.md) | `ci/pr-review` | todo |
| | Weekly tooling watch, facts collector, report check, merge guard (Q15, Q16, Q19) | [`07`](tasks/07-tooling-watch-and-merge-guard.md) | `ci/tooling-watch` | todo |
| | Bug and feature issue workers, test-first check (Q17b) | [`08`](tasks/08-issue-workers.md) | `ci/issue-workers` | todo |
| Wrap-up | README, ADRs, template readiness, end-to-end acceptance | [`09`](tasks/09-docs-template-acceptance.md) | `docs/template` | todo |

Status values: `todo` · `in progress` · `in review` · `done` · `blocked`.

```
01 → 02 → 03 → 04 → 05 ─┬─> 06 → 07 → 08 → 09
                        └─ human: ruleset (after 05)
```

## Human gates

Things only the owner can do: org settings, credentials, identities and
taste. The task that needs each one stops and asks if it isn't done yet.

| When | Action | Needed by |
| --- | --- | --- |
| Before 01 | Bootstrap commit (above) and license choice. | 01 |
| Before 04 | Provide the **age public key** (recipient) for `fnox.toml`. Keep the private key outside the repo. | 04 |
| Before 05 | Name the maintainers team for `CODEOWNERS`. | 05 |
| Before 05 | Create and install the **starter-bot** GitHub App (contents/pull-requests/issues: write, this repo only). Store `STARTER_BOT_APP_ID` (variable) and `STARTER_BOT_APP_KEY` (secret). `release.yml` uses it to open release PRs (D19). | 05 |
| After 05 merges | Apply the `main` ruleset from `docs/github-setup.md` (PRs only, squash, required check `ci`, 1 code-owner approval). | 06 |
| Before 06 | Add the `ANTHROPIC_API_KEY` Actions secret (with a spend limit on the Anthropic account). Set repo variable **`AGENTS_ENABLED = true`** (D21). Run `mise run labels` once task 06 lands it. | 06 |
| After 06 merges | Add `aw` and `pr-review` to the ruleset's required checks. | 07 |
| Before 07 | Create the **report-merger** GitHub App (contents + pull-requests: write), store `REPORT_MERGER_APP_ID` / `REPORT_MERGER_APP_KEY`, and add the App as a ruleset **bypass actor, pull-request-only mode**. | 07 |
| After 07 merges, before the first Tuesday | **Populate `tooling/watchlist.toml`** with the libraries, tools and apps (and git repos) the watcher must always include, for example hk, ty, moon, proto, Vite+. Do it in a human-authored PR. | first scheduled run |
| After 08 merges | Add `test-first` to the ruleset's required checks. | 09 |
| During 09 | Turn on "Template repository" in repo settings. Run the clean-clone check on macOS if the agent can't. | 09 |

## Done-criteria traceability

| `intent.md` done criterion | Proven in | Evidence |
| --- | --- | --- |
| Clean clone: `mise install` / `setup` / `check` on Linux + macOS, no secrets | 02–04 (built), 09 (verified on both OSes) | |
| CI runs `mise run check` and is a required check | 05 + ruleset gate | |
| Non-conventional commit rejected (locally + CI) | 04 (hook), 05 (CI) | |
| Fake key-shaped string rejected (locally + CI) | 04, 05 | |
| Lockfile committed; CI fails if stale | 03 (`lock:check`), 05 | |
| `AGENTS.md`, `REVIEW.md`, `intent/README.md`, `_template/` exist | 01 | |
| Local Claude Code session blocked from generated / human-only files | 04 | |
| Manual tooling-watch run → report PR, every tracked + watchlist entry, `report-check` passes, issues opened | 07 | |
| Scheduled run two Tuesdays in a row, both merged without a human | 07 (wired), 09 (observed) | |
| Report PR touching a path outside the report folder is refused | 07 | |
| Test bug issue → failing-test-first PR, checked by `test-first` | 08 | |
| Test feature issue → `intent.md`-only PR | 08 | |
| Every agent PR has an independent REVIEW.md review | 06 | |
| Agent-config change runs the eval suite and reports a pass rate | 06 (suite), 07 (report cases) | |
| Watchlist is human-only; agent proposes via issues | 07 | |
| Repo created from the template passes CI with no agent secrets | 09 | |
| README explains template use, commands, agent workflows and the switch | 09 | |
| Every `decisions.md` question answered or deferred | 09 | |

## Current run

Not started. Record each task's merged PR link, pins and surprises here as
it completes, the same way the TS starter's plan does.
