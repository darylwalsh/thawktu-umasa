# Decisions: Python starter baseline

Decision log and open questions for [`intent.md`](intent.md). One line per
entry. Tasks propose entries in their report, and those entries get copied
here before the next task starts. Don't delete superseded entries; mark them
`superseded by Dn` or `amended by Dn`. Choices that generated projects
inherit also get an ADR in `docs/decisions/`.

## Decided

| ID | Decision | Date | Source |
| --- | --- | --- | --- |
| D0 | Intent 0001 accepted and spec approved by the owner; recorded by the bootstrap commit that adds this folder. Plan mode starts from here. | 2026-10-24 | Owner (bootstrap commit) |
| D1 | mise provisions tools and owns tasks/env; uv owns Python deps, venv and `uv.lock`. Python-env tools (ruff, pyright, pytest) in uv `dev` group; repo tooling in mise. Exact pins everywhere. | 2026-10-24 | Owner; `spec.md` → Toolchain |
| D2 | Ruff for lint + format; pytest + pytest-cov for tests. | 2026-10-24 | Owner; `spec.md` → Tool configuration |
| D3 | Type checker is **pyright** in strict mode, installed as `pyright[nodejs]` via uv (no Node in mise). Chosen for mature pydantic v2 support. ty moves to the watchlist. Answers intent Q4. | 2026-10-24 | Owner |
| D4 | Git hooks use **lefthook**, same as the TS starter's D6. hk moves to the watchlist. No requirement to stay mise-ecosystem-pure. Answers intent Q5. | 2026-10-24 | Owner |
| D5 | commitizen (`cz`) for commit-msg validation, guided commits, version bump and CHANGELOG; `version_provider = "uv"`. No PyPI publish. Generated projects inherit the setup. Answers intent Q6. *Release mechanics amended by D19.* | 2026-10-24 | TS starter D7 carried over |
| D6 | gitleaks for scanning; fnox + age for secrets at rest; starter needs no secrets for checks. Agent credentials live in GitHub Actions secrets, not fnox. | 2026-10-24 | TS starter D8 carried over |
| D7 | Agent runtime is **GitHub Agentic Workflows** with `engine: claude` on the Anthropic API (`ANTHROPIC_API_KEY`). Workflows: pr-review, tooling-watch, issue workers (see D17). Writes only via safe-outputs, through a starter-bot GitHub App. gh-aw version pinned; upgrades are their own PR. Answers intent Q1. | 2026-10-24 | Owner |
| D8 | Tooling watch runs **weekly**, Tuesday 02:00 America/Detroit (overnight Mon→Tue), plus `workflow_dispatch`, so a report is ready Tuesday morning. Supersedes the biweekly cadence in the first intent draft. Answers intent Q2. | 2026-10-24 | Owner |
| D9 | Report-only PRs **auto-merge** via a non-agent merge guard (author, branch, path, `ci` incl. `report-check`, `pr-review` status, `hold` label) using a separate report-merger App as a ruleset bypass actor, merging with `--match-head-commit`. Answers intent Q3. | 2026-10-24 | Owner; amended by design review 2026-10-24 |
| D10 | `tooling/watchlist.toml` is **human-provided**: the libraries, tools and apps (with git repos where available) the watcher must always include in every report. Agents read it and propose changes via issues, never edit it. First entries (owner to supply): emerging tools such as hk, ty, moon, proto, Vite+. | 2026-10-24 | Owner |
| D11 | Issues are worked only after a maintainer applies `agent:ready`. Bugs: failing test first. Features: `intent.md`-only PR. Answers intent Q8. *Mechanics amended by D17.* | 2026-10-24 | `spec.md` → Issue workers |
| D12 | Delivered as a GitHub template repository. A copier/cookiecutter template (to pull later updates into generated projects) is deferred to a later intent. Answers intent Q7. | 2026-10-24 | Matches TS starter task 10 |
| D13 | Public repository in the org. Answers intent Q9. | 2026-10-24 | Owner's project description |
| D14 | **Claude Code hooks** in `.claude/settings.json`: PreToolUse blocks edits to generated and human-only files (and to tracked tests in fix mode); PostToolUse formats edited Python. Stdlib Python scripts with tests. Backs the advisory rules in `AGENTS.md` for local and CI agent sessions (playbook Stage 3). | 2026-10-24 | Design review 2026-10-24 |
| D15 | **Agent eval suite** in `evals/` (pr-review and tooling-watch-review cases, seeded from task 06/07 proofs, including prompt-injection cases), run by `agent-evals.yml` on agent-config changes and monthly. Not a required check; missing or regressed evidence is a REVIEW.md **major** (playbook Stage 4). | 2026-10-24 | Design review 2026-10-24 |
| D16 | Tooling-watch **facts are collected by a script** (`collect_versions.py`: PyPI, GitHub releases, OSV) before the agent runs; the model writes narrative and verdicts only. The facts file is committed with the report, and `report-check` (offline, in `mise run check`) validates every value and link against it. Threat detection on. | 2026-10-24 | Design review 2026-10-24 (playbook Stage 6: detection stays deterministic) |
| D17 | Issue worker is **two gh-aw workflows**: `issue-worker-bug` (`allowed-files` `src/**`, `tests/**`; toolchain installed in pre-agent steps) and `issue-worker-feature` (`allowed-files` intent files only). Both use `protected-files: blocked`. Bug PRs are checked by a deterministic `test-first` CI job. | 2026-10-24 | Design review 2026-10-24 |
| D18 | Dependabot PRs skip the agent review: a deterministic job sets `pr-review` = success ("skipped: dependabot"). Missing tally sets error. gh-aw must admit `starter-bot[bot]` as an actor. | 2026-10-24 | Design review 2026-10-24 |
| D19 | **Release PR, then tag:** `release.yml` runs `cz bump --files-only` plus changelog on a `release/vX.Y.Z` branch and opens a PR with the starter-bot App; `release-tag.yml` tags and creates the GitHub Release when that PR merges. Nothing pushes to `main` directly. | 2026-10-24 | Design review 2026-10-24 |
| D20 | Compiled-workflow drift is checked by a separate `aw` CI job (`mise run check:aw`), not inside `mise run check`, so contributors and generated projects don't need gh or gh-aw. | 2026-10-24 | Design review 2026-10-24 |
| D21 | Agent workflows, `agent-evals` and the merge guard run only when repo variable `AGENTS_ENABLED == 'true'`. Repos created from the template stay green without Apps or secrets until they opt in. | 2026-10-24 | Design review 2026-10-24 |

## Open

| ID | Question | Decided in | Answer |
| --- | --- | --- | --- |
| Q10 | Python 3.15 or 3.14? 3.15.0 shipped 2026-10-09; depends on pydantic-core wheels for 3.15 on all three platforms. | task 02 | — |
| Q11 | Exact Ruff rule selection and coverage `fail_under`. | task 03 | — |
| Q12 | Network blocking in tests: conftest fixture or `pytest-socket`? | task 03 | — |
| Q13 | gh/gh-aw install method via mise, and the pinned gh-aw version. | task 06 | — |
| Q14 | Claude model pin for each agent workflow (suggested start: a Sonnet-class model for review and the watch, a stronger model for the bug worker; revisit with month-one cost data). | task 06 | — |
| Q15 | Does the pinned gh-aw pass `timezone` through on `schedule`? Expected yes (gh-aw PR #22018). Otherwise use the UTC fallback `0 7 * * 2`. | task 07 | — |
| Q16 | With facts collected outside the firewall, does any watchlist entry still need its host added to the agent allowlist? Expected: only non-GitHub homepages. | task 07 | — |
| Q17a | Exact gh-aw safe-output names for PR review comments and the summary comment. | task 06 | — |
| Q17b | Exact gh-aw safe-output name for removing the `agent:ready` label. | task 08 | — |
| Q18 | gh-aw field for admitting bot actors (`starter-bot[bot]`) and how to skip `dependabot[bot]` while still producing the `pr-review` status. | task 06 | — |
| Q19 | gh-aw custom pre-agent steps: do they run outside the agent firewall, and can they pass files (facts.json, installed toolchain) to the agent job? | task 07 (spike), used in 08 | — |
| Q20 | commitizen release-PR mechanics: does `cz bump --files-only` (plus changelog) give the same result as a full bump, and does `release-tag.yml` derive the tag reliably from the merged commit? | task 05 | — |
| Q21 | Claude Code hooks vs Bash edits: add a `Bash` matcher that refuses in-place edits of blocked paths, or accept the gap with CI and review as backstop? | task 04 | — |
