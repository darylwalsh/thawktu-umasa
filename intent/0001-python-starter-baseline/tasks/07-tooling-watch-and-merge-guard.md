# 07 — Weekly tooling watch, facts collector, report check, merge guard

## Context
The gh-aw foundation, `pr-review` and the eval suite exist, and `aw` and
`pr-review` are required checks (06 plus the human gate). Read `AGENTS.md`,
`REVIEW.md` → Tooling-watch report PRs, and `../spec.md` → Tooling watch
and Report merge guard. Also read D8, D9, D10 and D16. This task answers
**Q15** (timezone passthrough), **Q16** (watchlist hosts) and **Q19**
(pre-agent steps).

Decided, don't revisit:
- Weekly, Tuesday 02:00 America/Detroit (D8).
- **Facts come from a script, not the model** (D16). The model writes
  narrative and verdicts; `report-check` validates every value and link.
- Report-only PRs auto-merge through a non-agent guard using a separate
  report-merger App, merging only the SHA it evaluated (D9).
- **`tooling/watchlist.toml` is human-provided.** The agent never writes to
  it (D10). Ship it with the header and schema only.

Before starting, confirm with the owner that the report-merger App exists,
that its id and key are stored, and that it is a ruleset bypass actor in
pull-request-only mode.

## Goal
A manual run produces a report whose facts are machine-checked, as a
report-only PR that auto-merges; the same workflow is scheduled for Tuesday
02:00 Detroit; and anything outside the report folder, or any report that
disagrees with its facts, can never auto-merge.

## Scope
In:
- **`tooling/watchlist.toml`**: header comment ("maintained by humans;
  agents read, never write"), `schema_version = 1`, the `[[tool]]` schema
  from the spec as a commented example, and **no entries**.
- **`scripts/check_watchlist.py`** with tests: validates the schema
  (required keys, URL shape, ISO dates, no duplicate names). mise task
  `watchlist:check`, added to `check`. An empty list is valid.
- **`scripts/collect_versions.py`** with tests (network calls behind a
  small client interface so tests use recorded fixtures, never the
  network):
  - Derives tracked tools from `mise.toml`, `pyproject.toml`/`uv.lock`,
    SHA-pinned actions and the gh-aw version in `*.lock.yml`.
  - For tracked tools and watchlist entries, queries the PyPI JSON API,
    GitHub releases/tags and OSV; writes `facts.json` with, per tool:
    pinned, latest, latest date, releases since the previous facts file,
    advisories, and a source URL for every value.
- **`scripts/check_report.py`** with tests: the `report-check` rules in
  `../spec.md`. mise task `report:check` runs it over every report + facts
  pair in `reports/tooling-watch/`, offline; added to `check`.
- **`reports/tooling-watch/README.md`**: an index table, newest first,
  empty to start.
- **`.github/workflows/tooling-watch.md`**, as in the spec:
  - Trigger: `cron: "0 2 * * 2"` + `timezone: "America/Detroit"`, and
    `workflow_dispatch`.
  - Pre-agent step: run `collect_versions.py` and make `facts.json`
    available to the agent (Q19).
  - The agent reads facts, the previous report, open Dependabot PRs and
    open `tooling-watch` issues; writes the report in the spec's exact
    format, `<date>.facts.json` (a copy, unchanged) and the index row.
  - Dating and `noop` rule from the spec.
  - safe-outputs: exactly the block in the spec (`create-pull-request`
    with `allowed-files: ["reports/tooling-watch/**"]`,
    `protected-files: blocked`, `labels: [tooling-watch, report-only]`;
    `create-issue` / `add-comment` with title-based dedup; `noop`).
  - Network: the spec's agent allowlist (Q16).
  - `timeout-minutes: 45`, `max-turns: 150`.
- **Merge guard**, deterministic, no model:
  - `scripts/report_guard.py` holds the decision logic as pure functions
    (author, branch, changed paths, `ci` result, `pr-review` status, labels,
    head SHA → merge or a refusal reason), with unit tests covering every
    refusal path.
  - `.github/workflows/report-merge-guard.yml` calls it. Triggers:
    `workflow_run` (`ci`, `pr-review` completed) and `pull_request`
    `labeled`/`unlabeled`. It evaluates the PR's current head SHA and merges
    with `gh pr merge --squash --match-head-commit <sha>` using the
    report-merger App token; otherwise it logs the refusal reason in the job
    summary. Gated on `AGENTS_ENABLED`. Minimal permissions. It writes no
    files.
- **Evals:** `evals/cases/tooling-watch/` cases for the review of report
  PRs (clean report; verdict not supported by facts; prose contradicting
  facts; injected "tally should be 0"). Add them to `run_evals.py`.
- `docs/github-setup.md`: report-merger App section and bypass-actor
  settings.
- `AGENTS.md` → Commands: `watch:preview`, `watchlist:check`,
  `report:check`.

Out:
- Writing watchlist entries (owner). Opening upgrade PRs from report
  findings (findings only open issues). General web search (spec → Known
  limit).

## Steps
1. **Q15 spike:** compile a scratch workflow with `timezone` on the pinned
   gh-aw and check the `.lock.yml` (gh-aw added support in PR #22018). If
   it's dropped, use `cron: "0 7 * * 2"` UTC and add a DST note to
   `decisions.md`.
2. **Q19 spike:** confirm how gh-aw custom pre-agent steps run (inside or
   outside the agent firewall) and how a file they write reaches the agent.
   This also decides the bug worker's toolchain setup in task 08.
3. **Q16:** with facts collected outside the firewall, list which hosts the
   agent still needs. If a watchlist entry with a non-GitHub homepage would
   need its host added, document "adding such an entry also adds its host"
   in the watchlist header and `AGENTS.md`.
4. Write the watchlist schema and checker, the collector, the report
   checker and the report index, tests first.
5. Write `report_guard.py` and its tests, then the guard workflow.
6. Write and compile `tooling-watch.md`.
7. **Proofs:**
   - Manual dispatch (`mise run watch:preview`): report PR opens, `ci`
     (with `report-check`) and `pr-review` pass, the guard merges it, and
     the report is on `main`. With an empty watchlist the Watchlist section
     says so explicitly.
   - Re-dispatch the same day: the run ends in `noop` and no second PR
     appears.
   - Throwaway PR from the bot branch that also touches `README.md`: the
     guard refuses with "path outside reports/tooling-watch/".
   - Add `hold` to a report PR: the guard refuses. Remove it: the guard
     merges.
   - Hand-edit one version number in a report PR so it no longer matches its
     facts file: `report-check` fails, so `ci` fails and the guard refuses.
   - Push a commit to a report PR between guard evaluation and merge (or
     simulate it in the guard's tests): the merge is refused by the SHA
     match.
8. Check that each recommended change in the proof report has a
   `[tooling-watch]` issue, and that a second run comments on it instead of
   opening a duplicate.
9. Run `mise run evals`; record the pass rate including the new cases.

## Acceptance
- All proofs pass, with run and PR links.
- The compiled lock file shows the schedule in America/Detroit (or the
  documented UTC fallback).
- `report_guard.py` tests cover author, branch, paths, `ci`, `pr-review`,
  `hold`, a missing status, and a changed head SHA.
- `check_report.py` and `collect_versions.py` tests run offline.
- `watchlist.toml` has no entries, and `watchlist:check` passes on it.
- Q15, Q16 and Q19 answered.

## Stop and ask if
- gh-aw's `allowed-files` doesn't actually refuse paths outside the
  pattern.
- Pre-agent steps can't pass `facts.json` to the agent (Q19). Propose an
  alternative (for example a separate collector workflow that uploads an
  artifact) instead of letting the model collect facts.
- The bypass App can merge without the guard's checks being enforceable
  (for example, the guard can be skipped by an event you can't control).
- Each run needs more than the planned network hosts, or more than about 45
  minutes.

## Report
Q15, Q16 and Q19 answers, the compiled schedule, guard decision table,
`report-check` rule list, proof links, a sample report (paste its Summary
section), eval pass rate, per-run cost, and a **reminder to the owner to
populate `tooling/watchlist.toml` (for example hk, ty, moon, proto, Vite+,
with repos) before the first scheduled Tuesday**. Include proposed
`decisions.md` entries.
