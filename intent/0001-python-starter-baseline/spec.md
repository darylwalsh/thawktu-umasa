# Spec: Python starter baseline with agent-maintained tooling

Design and technical decisions for [`intent.md`](intent.md). Repo-wide
invariants live in `AGENTS.md` and are only summarized here (see
[AGENTS.md invariants](#agentsmd-invariants)). Decision IDs (D1…) refer to
[`decisions.md`](decisions.md). Items marked **(verify in NN, Qnn)** must be
confirmed by the named task in `plan.md`, with the result recorded in
`decisions.md`.

Status: **approved 2026-10-24** (owner, bootstrap commit; D0). Revised the
same day after a design review against the AI-native SDLC playbook
(D14–D21). Approval starts plan mode.

Task numbers (final, matching `plan.md`): 01 AGENTS.md + skeleton, 02
toolchain, 03 lint/type/test, 04 git hooks + Claude Code hooks + secrets +
commits, 05 CI + release + Dependabot, 06 gh-aw foundation + PR review +
evals, 07 tooling watch + merge guard, 08 issue workers, 09 docs + template +
acceptance.

## Summary

| Area | Decision | ID |
| --- | --- | --- |
| Toolchain anchors | mise (tools, tasks, env) + uv (Python deps, venv, lock) | D1 |
| Lint + format | Ruff | D2 |
| Type checker | **pyright** (strict), installed with uv as `pyright[nodejs]`; ty on the watchlist | D3 |
| Tests | pytest + pytest-cov | D2 |
| Git hooks | **lefthook** (hk on the watchlist) | D4 |
| Agent guardrails (local) | **Claude Code hooks** in `.claude/settings.json` | D14 |
| Commits + releases | commitizen (`cz`), `version_provider = "uv"`, **release PR** then tag | D5, D19 |
| Secrets | gitleaks (scan) + fnox/age (at rest), same as the TS starter | D6 |
| Agent runtime | **GitHub Agentic Workflows (`gh aw`), `engine: claude`, Anthropic API** | D7 |
| Agent switch | Agent workflows run only when repo variable `AGENTS_ENABLED == 'true'` | D21 |
| Agent config tests | **Eval suite** in `evals/`, run on agent-config changes and monthly | D15 |
| Tooling-watch cadence | **Weekly, Tuesday 02:00 America/Detroit** (overnight Mon→Tue) | D8 |
| Tooling-watch facts | **Collected by a script**, checked by `report-check`; the model writes verdicts only | D16 |
| Report PR merge | **Auto-merge** report-only PRs through a non-agent merge guard | D9 |
| Watchlist | **Human-provided** `tooling/watchlist.toml`, always included in every report | D10 |
| Issue intake | `agent:ready` label applied by maintainers | D11 |
| Issue workers | **Two workflows** (bug, feature), each path-locked; bug path checked by `test-first` | D17 |
| Dependabot and bots | Dependabot PRs skip the agent review with an explicit status | D18 |
| Compiled-workflow check | `aw` CI job, **not** part of `mise run check` | D20 |
| Template | GitHub template repository; copier deferred | D12 |
| Visibility | Public repo in the org | D13 |

## Toolchain

### Who installs what (D1)

Tools that need the project's virtualenv go in uv. Everything else goes in
mise.

| Tool | Installed by | Pinned in | Why there |
| --- | --- | --- | --- |
| Python | mise | `mise.toml` (exact patch) | One interpreter for uv, the editor and CI |
| uv | mise | `mise.toml` | Bootstraps everything Python |
| Ruff | uv (`dev` group) | `uv.lock` | Editor extension and CLI resolve the same version |
| pyright `[nodejs]` | uv (`dev` group) | `uv.lock` | Must see the project venv to resolve imports (see D3) |
| pytest, pytest-cov | uv (`dev` group) | `uv.lock` | Run against the project venv |
| lefthook | mise | `mise.toml` | Repo tooling, not Python code |
| gitleaks | mise | `mise.toml` | Same as the TS starter |
| commitizen | mise (`pipx:commitizen`, uv-backed) | `mise.toml` | Same as the TS starter; keeps it out of the project's deps |
| fnox, age | mise | `mise.toml` | Same as the TS starter (D6) |
| gh + gh-aw extension | mise, **only in the `aw` CI job and for maintainers** | `mise.toml` (optional tool group) | Compile/lint agent workflows; not needed for `mise run check` (D20) **(verify in 06, Q13)** |

Rules:

- Every version is exact. No `latest`, no ranges in `mise.toml`.
  `pyproject.toml` dev dependencies use `==` pins, and `uv.lock` is the
  source of truth.
- `mise.toml` sets `[settings] python.uv_venv_auto = true` (or the current
  equivalent) so entering the directory activates `.venv`.
  `UV_PYTHON` points uv at mise's interpreter and
  `UV_PYTHON_DOWNLOADS = "never"`, so uv never downloads its own.
  **(verify in 02: setting names on the pinned mise)**
- No Node in `mise.toml`. The `[nodejs]` extra brings a Node binary through
  `nodejs-wheel` when the package is installed, not at run time.

### Python version

- Default: the newest CPython minor that pydantic-core ships wheels for, on
  Linux x86_64/arm64 and macOS arm64. Python 3.15.0 was released on
  2026-10-09. Task 02 checks pydantic-core wheel availability and pins 3.15
  if it's there, otherwise 3.14. The tooling watch tracks the gap.
  **(verify in 02, Q10)**
- `requires-python` = `>=<chosen minor>`. One version in CI, no matrix in
  0001. A matrix is a later intent if generated projects need it.

### Project layout

```
.
├── AGENTS.md                 # repo rules for humans and agents (source of truth, ≤ ~80 lines)
├── CLAUDE.md                 # "@AGENTS.md" pointer only
├── REVIEW.md                 # PR review policy
├── README.md
├── CHANGELOG.md              # written by `cz bump`
├── mise.toml                 # tools, env, tasks (canonical commands)
├── pyproject.toml            # metadata, deps, ruff/pyright/pytest/commitizen config
├── uv.lock
├── lefthook.yml
├── .gitleaks.toml
├── fnox.toml                 # age recipients; no secrets required for checks
├── .claude/
│   ├── settings.json         # Claude Code hooks + permissions (D14)
│   └── hooks/
│       ├── guard_paths.py    # PreToolUse: block human-only / generated files
│       └── format_edited.py  # PostToolUse: ruff format + ruff check --fix on edited .py
├── src/python_starter/
│   ├── __init__.py           # __version__ from importlib.metadata
│   ├── __main__.py           # `python -m python_starter` prints name + version
│   └── models.py             # tiny pydantic model: proves pyright + pydantic in strict mode
├── tests/
│   ├── test_main.py
│   ├── test_models.py
│   └── scripts/              # tests for everything under scripts/ and .claude/hooks/
├── scripts/
│   ├── check_fnox.py         # secrets:check (04)
│   ├── check_watchlist.py    # watchlist schema (07)
│   ├── collect_versions.py   # tooling-watch facts collector (07, D16)
│   ├── check_report.py       # report-check (07, D16)
│   ├── report_guard.py       # merge guard decision logic (07, D9)
│   └── check_test_first.py   # test-first check for bug PRs (08, D17)
├── evals/                    # agent-config regression suite (06, 07; D15)
│   ├── README.md
│   ├── run_evals.py
│   └── cases/
│       ├── pr-review/*.yml
│       └── tooling-watch/*.yml
├── tooling/
│   └── watchlist.toml        # HUMAN-PROVIDED always-include list (D10)
├── reports/tooling-watch/
│   ├── README.md             # index, newest first
│   ├── YYYY-MM-DD.md         # one report per run date
│   └── YYYY-MM-DD.facts.json # collector output the report was written from
├── docs/
│   ├── github-setup.md       # rulesets, Apps, secrets, variables
│   └── decisions/            # ADRs for choices generated projects inherit
├── intent/                   # README.md, _template/, NNNN-slug/ work folders
└── .github/
    ├── workflows/
    │   ├── ci.yml                         # jobs: ci, aw, test-first
    │   ├── release.yml                    # opens the release PR (D19)
    │   ├── release-tag.yml                # tags + GitHub Release when the release PR merges
    │   ├── agent-evals.yml                # D15
    │   ├── report-merge-guard.yml         # deterministic, no model (D9)
    │   ├── pr-review.md      (+ .lock.yml)          # gh-aw, engine: claude
    │   ├── tooling-watch.md  (+ .lock.yml)          # gh-aw, engine: claude
    │   ├── issue-worker-bug.md     (+ .lock.yml)    # gh-aw, engine: claude (D17)
    │   └── issue-worker-feature.md (+ .lock.yml)    # gh-aw, engine: claude (D17)
    ├── aw/shared/common.md                # shared gh-aw frontmatter fragment
    ├── dependabot.yml
    ├── CODEOWNERS
    └── ISSUE_TEMPLATE/{bug.yml, feature.yml, config.yml}
```

- `src/` layout, built with uv's build backend (`uv_build`). Package name
  `python_starter`. Renaming is a documented step for template users.
- Demo code stays deliberately tiny. Framework scaffolds are out of scope
  (intent → Non-goals).
- All scripts are stdlib-only Python run with `uv run`, so they work on Linux
  and macOS and are unit-tested like the package.

### Tool configuration (in `pyproject.toml`)

**Ruff (D2)**
- `ruff format` is the formatter, and `ruff check` the linter.
- Start from an explicit rule set (pyflakes, pycodestyle, isort, pyupgrade,
  bugbear, simplify, Ruff-specific and similar), not `ALL`. Task 03 lists the
  exact selection and its reasons in `decisions.md` (Q11).
- `target-version` matches `requires-python`.
- Per-file ignores only for `tests/` (for example assert use), each with a
  comment.

**pyright (D3)**
- `[tool.pyright]`: `typeCheckingMode = "strict"`, `pythonVersion` matching
  the pin, `venvPath = "."`, `venv = ".venv"`,
  `include = ["src", "tests", "scripts", ".claude/hooks", "evals"]`.
- pydantic v2 is understood through `dataclass_transform`, so no plugin is
  needed. `models.py` and `test_models.py` exist to prove this.
- `reportUnnecessaryTypeIgnoreComment = true`, so stale ignores fail.
- The ignore style is `# pyright: ignore[ruleName]  # reason`. A bare
  `# type: ignore` is rejected (REVIEW.md).
- Invoked as `uv run pyright`, never through a hook-managed isolated env.

**pytest**
- `testpaths = ["tests"]`, `--strict-markers`, `--strict-config`,
  `-p no:cacheprovider` in CI.
- Coverage via pytest-cov on `src/` and `scripts/`, `fail_under` set in task
  03 from the baseline (target ≥ 90% for the demo package) (Q11).
- No network in tests. Task 03 decides between a socket-blocking fixture in
  `conftest.py` and `pytest-socket` **(verify in 03, Q12)**.

**commitizen (D5)**
- `[tool.commitizen]`: `name = "cz_conventional_commits"`,
  `version_provider = "uv"` (updates `pyproject.toml` **and** `uv.lock`),
  `tag_format = "v$version"`, `update_changelog_on_bump = true`,
  `major_version_zero = true` until 1.0, and
  `bump_message = "chore(release): v$current_version → v$new_version"`.
  **(verify each key against the pinned commitizen in 04)**

## Tasks (mise.toml)

mise tasks are the only command surface. Hooks, CI and agents all call
them.

| Task | Runs | Notes |
| --- | --- | --- |
| `setup` | `uv sync --locked` → `lefthook install` | Safe to re-run; hook install no-ops in CI |
| `run` | `uv run python -m python_starter` | Demo entry point |
| `fmt` | `ruff format` | Writes |
| `fmt:check` | `ruff format --check` | |
| `lint` | `ruff check` | `lint:fix` adds `--fix` |
| `typecheck` | `uv run pyright` | |
| `test` | `uv run pytest` | |
| `lock:check` | `uv lock --check` | Fails if `uv.lock` is stale |
| `secrets` | gitleaks, full history + tracked tree | |
| `secrets:check` | every `fnox.toml` value is age ciphertext | |
| `watchlist:check` | `scripts/check_watchlist.py` | From 07 |
| `report:check` | `scripts/check_report.py` on every report + facts pair | From 07; offline |
| `check` | `fmt:check` `lint` `typecheck` `test` `lock:check` `secrets` `secrets:check` `watchlist:check` `report:check` | What CI's `ci` job runs. Needs no secrets, no gh, no network beyond package install |
| `check:aw` | `gh aw compile` + `git diff --exit-code .github/workflows/*.lock.yml` | CI `aw` job and maintainers only (D20) |
| `evals` | `uv run evals/run_evals.py` | Needs `ANTHROPIC_API_KEY`; never part of `check` (D15) |
| `commit` | `cz commit` | Guided commit |
| `bump` | `cz bump` | Used by `release.yml`; `--dry-run` locally |
| `labels` | `scripts/labels.sh` | One-time label setup (admin `gh auth`) |
| `watch:preview` | `gh workflow run tooling-watch` | Manual report run (needs `gh auth`) |

## Git hooks: lefthook (D4)

`lefthook.yml`:

- **pre-commit** (parallel, staged files only, target under 3 seconds):
  - `ruff format` on staged `*.py` with `stage_fixed: true`
  - `ruff check --fix` on staged `*.py` with `stage_fixed: true`
  - `gitleaks` on staged changes
  - `mise run secrets:check` when `fnox.toml` is staged
- **commit-msg**: `cz check --commit-msg-file {1}`
- **pre-push**: `mise run typecheck` and `mise run test`

Hooks call mise tasks or pinned tools, never hand-copied command lines.
`hk.pkl` is not created. hk is on the watchlist (D4, D10).

## Claude Code hooks (D14)

Git hooks guard commits. Claude Code hooks guard what an agent session does
*before* anything is committed, on a developer's machine as well as in CI.
They are the playbook's Stage 3 build-time guardrails and back up the
advisory rules in `AGENTS.md`.

`.claude/settings.json` (committed, protected by REVIEW.md):

- **PreToolUse**, matcher `Edit|Write|MultiEdit|NotebookEdit` →
  `.claude/hooks/guard_paths.py`. Exit 2 with a reason on:
  - generated files: `uv.lock`, `.github/workflows/*.lock.yml`,
    `CHANGELOG.md`, `reports/tooling-watch/*.facts.json`;
  - human-only files: `tooling/watchlist.toml`, `fnox.toml`;
  - **fix mode:** when `STARTER_FIX_MODE=1` is set (the bug path), any edit
    to a file under `tests/` that is tracked at `HEAD`. New test files are
    allowed; the reproducing test is committed before fix mode is turned on.
- **PostToolUse**, same matcher → `.claude/hooks/format_edited.py`: runs
  `ruff format` and `ruff check --fix` on the edited file if it is `*.py`.
  Fast and scoped to one file; the full suite stays in `mise run check`.
- `permissions.deny`: `Read(.env*)`, `Read(**/*.age)`, `Read(fnox.local.toml)`.
  `permissions.allow`: `Bash(mise run *)`, `Bash(uv run *)`, `Bash(git *)`
  so routine checks don't prompt.
- Hook scripts read the hook JSON from stdin, are stdlib-only Python, run
  through `uv run --no-project`, and have unit tests in `tests/scripts/`.
- **Known limit:** a Bash command such as `sed -i` can still change a
  blocked file. Task 04 decides whether to add a `Bash` matcher that refuses
  obvious in-place edits of blocked paths, or to accept the gap with CI and
  review as the backstop **(verify in 04, Q21)**.

## Secrets (D6)

- **gitleaks:** `.gitleaks.toml` extends the default rules. Allow-list
  entries are scoped by path *and* pattern (for example age ciphertext in
  `fnox.toml` only), each with a comment.
- **fnox + age:** same model as the TS starter. `fnox.toml` holds age
  recipients and any secret a developer adds. The starter itself needs **no**
  secrets, so `setup`, `check` and CI never decrypt. `fnox.local.toml` and
  `mise.local.toml` are gitignored.
- **Agent credentials are not in fnox.** `ANTHROPIC_API_KEY` and the GitHub
  App private keys live in GitHub Actions secrets and are only referenced by
  the agent workflows, `agent-evals`, `release.yml` and the merge guard.

## CI and release

**`ci.yml`** (push to `main`, every PR). Three jobs:

- **`ci`** (required check): `actions/checkout` with `fetch-depth: 0` →
  `jdx/mise-action` → `mise run setup` → `mise run check`, plus `cz check`
  over the PR's commit range. `permissions: contents: read`. No secrets.
- **`aw`** (required check from task 06): runs `mise run check:aw` when
  `.github/workflows/*.md` exist; otherwise succeeds with "no agentic
  workflows". Keeps gh/gh-aw out of `mise run check` (D20).
- **`test-first`** (from task 08): runs only on PRs labelled `type:bug` that
  were opened by `issue-worker-bug`; otherwise succeeds as "not applicable".
  See Issue workers.
- All third-party actions pinned by commit SHA with a version comment. mise
  and uv caches enabled. Target runtime under 5 minutes.

**Release: release PR, then tag (D19).** `cz bump` would push a commit
straight to `main`, which the ruleset forbids. Instead:

- **`release.yml`** (`workflow_dispatch` on `main`): setup → `mise run check`
  → `cz bump --files-only --yes` (version in `pyproject.toml` + `uv.lock`)
  and the CHANGELOG update → commit on `release/vX.Y.Z` → open a PR with the
  starter-bot App token so `ci` and `pr-review` run. The release PR merges
  through normal human approval. **(verify in 05, Q20: that `--files-only`
  plus changelog generation gives the same result as a full bump)**
- **`release-tag.yml`** (push to `main` where the head commit is
  `chore(release): …`): creates tag `vX.Y.Z` and a GitHub Release from the
  new CHANGELOG section. The only workflow with `contents: write` via
  `GITHUB_TOKEN`; tags aren't covered by the branch ruleset.
- No PyPI publish (intent → Non-goals).

**`dependabot.yml`**:
- Ecosystems `github-actions` and `uv`, weekly, with commit prefixes
  `ci(deps)` and `build(deps)`.
- Dependabot does the mechanical bumps. The tooling watch covers what
  Dependabot can't (mise-pinned tools, alternatives, context) and links to
  open Dependabot PRs rather than duplicating them.

**Branch protection (ruleset on `main`):**
- PRs only, no direct pushes, linear history (squash).
- Required checks: `ci`, `aw`, `test-first`, `pr-review`.
- One approving review from a code owner (`CODEOWNERS`:
  `* @<org>/<maintainers-team>`).
- One bypass actor: the **report-merger GitHub App**, in pull-request-only
  mode (D9).
- Squash merge removes the per-commit history from `main`. The test-first
  evidence for bug fixes therefore lives in the PR and its `test-first`
  check, which is why that check is mechanical.

## Agent runtime (D7)

All agents are **GitHub Agentic Workflows**: markdown files in
`.github/workflows/` compiled with `gh aw compile` into `.lock.yml` Actions
workflows, with `engine: claude` calling the Anthropic API through
`ANTHROPIC_API_KEY`.

Common frontmatter (shared fragment `.github/aw/shared/common.md`, imported
by every agent workflow):

- `engine: claude` and an explicit `model:` pin, so a model change is a
  reviewed diff **(verify in 06, Q14)**.
- **Agent switch (D21):** every agent workflow, `agent-evals` and the merge
  guard run only when `vars.AGENTS_ENABLED == 'true'`. A repo created from
  the template has no such variable, so its CI is green without any Apps or
  secrets.
- The agent job is read-only (`permissions: contents: read, issues: read,
  pull-requests: read`). All writes go through declared `safe-outputs`.
- `timeout-minutes` and `max-turns` set per workflow (starting values
  below).
- `network:` is an explicit allowlist. Changing it means changing a protected
  file, which needs human approval (REVIEW.md).
- `safe-outputs.github-app` uses the **starter-bot GitHub App**. PRs opened
  by an App identity trigger `ci.yml`, which `GITHUB_TOKEN`-created PRs
  don't. The App has `contents: write`, `pull-requests: write`,
  `issues: write` on this repo only.
- **Threat detection** on safe outputs is enabled for every workflow that
  reads untrusted text (issue bodies, release notes, diffs).
- **protected-files:** valid values are `request_review` (current default),
  `blocked`, `fallback-to-issue` and `allowed`. Every workflow here uses
  `blocked`: no agent in 0001 has a legitimate reason to touch protected
  files, and the decline paths say so.
- **Bot actors:** gh-aw's role check must admit `starter-bot[bot]` (whose PRs
  must be reviewed) and recognise `dependabot[bot]` (whose PRs are skipped,
  see D18). Task 06 finds the exact field (`bots:` or equivalent)
  **(verify in 06, Q18)**.
- `CLAUDE.md` is a one-line pointer to `AGENTS.md`. gh-aw treats
  `CLAUDE.md`, `.claude/`, `.github/`, `pyproject.toml` and `uv.lock` as
  protected files by default. That protection stays on.
- gh-aw changes quickly (its frontmatter schema has changed within 2026).
  Pin the gh-aw version, and treat a gh-aw upgrade as its own reviewed PR
  that re-runs the evals.

### PR review agent: `.github/workflows/pr-review.md`

- Trigger: `pull_request` (`opened`, `synchronize`, `ready_for_review`),
  plus a `/review` slash command.
- Runs as a fresh session that sees only the diff, `AGENTS.md`, `REVIEW.md`,
  the linked issue and the active `intent/` folder, never the writer's
  transcript.
- Posts findings in the REVIEW.md format. Findings never approve a PR.
- **`pr-review` status:** a deterministic job (no model) after the agent job
  reads the tally line from the summary comment and sets the `pr-review`
  commit status: failure when `blocker>0` or `major>0`, success otherwise,
  error when the tally is missing.
- **Dependabot (D18):** when the PR author is `dependabot[bot]`, the agent
  job is skipped and the deterministic job sets `pr-review` = success with
  description "skipped: dependabot". Dependabot runs have no access to Actions
  secrets, so without this every Dependabot PR would wait forever on a
  required check. Human code-owner approval still applies.
- Read-only. Outputs are review comments plus one summary comment
  **(verify output names in 06, Q17a)**. Starting limits:
  `timeout-minutes: 20`, `max-turns: 60`.
- A second reviewer (for example Greptile) is optional and out of scope.

### Agent evals (D15)

The review policy, `AGENTS.md`, `.claude/**` and the workflow prompts steer
the agents, so they get regression tests like code (playbook Stage 4).

- `evals/cases/pr-review/*.yml`: each case is a fixture diff plus context
  and the expected outcome (for example "tally has major ≥ 1 with pass
  `compliance`", "verdict approve"). Seeded from task 06's proofs: bare
  `# type: ignore`, out-of-scope change, weakened assertion in a fix commit,
  clean docs change, and a diff containing a prompt-injection string.
- `evals/cases/tooling-watch/*.yml`: report + facts fixtures for the review
  of report PRs (task 07): a clean report, a verdict the facts don't support,
  prose contradicting the facts, an injected "tally should be 0" line.
- `evals/run_evals.py` runs each case through Claude Code non-interactively
  (`claude -p`, read-only tools) with the same prompt the workflow uses, and
  scores the result against the expectation. It prints a pass rate.
- `.github/workflows/agent-evals.yml`: on PRs touching `AGENTS.md`,
  `CLAUDE.md`, `REVIEW.md`, `.claude/**`, `.github/workflows/*.md`,
  `.github/aw/**` or `evals/**`; and monthly on schedule. Posts the pass rate
  and the pass rate on `main` as a PR comment. Not a required check (it needs
  a secret and is path-conditional); REVIEW.md makes missing or regressed
  eval evidence a **major** finding instead.
- Every miss a human catches later becomes a new case.

### Tooling watch: `.github/workflows/tooling-watch.md` (D8, D9, D10, D16)

**Trigger**

```yaml
on:
  schedule:
    - cron: "0 2 * * 2"        # Tuesday 02:00 America/Detroit
      timezone: "America/Detroit"
  workflow_dispatch:
```

- GitHub Actions has supported an IANA `timezone` on schedule entries since
  March 2026, and gh-aw's compiler accepts and preserves the field (gh-aw
  PR #22018). Task 07 confirms on the pinned gh-aw version
  **(verify in 07, Q15)**. Fallback: `cron: "0 7 * * 2"` (UTC) with a DST
  note in `decisions.md`.
- Scheduled runs can start late; 02:00 leaves plenty of room before Tuesday
  morning.
- **Dating:** a report is dated by the run's date in America/Detroit. If
  `reports/tooling-watch/<date>.md` already exists on `main`, the run calls
  `noop`, so a same-day rerun can't produce a duplicate. A manual run on a
  Thursday produces a Thursday-dated report; the next scheduled Tuesday
  report compares against it.

**Two phases: facts by script, judgment by model (D16).**
Detection stays deterministic (playbook Stage 6). The model never
originates a version number, date or advisory.

1. **Collect (pre-agent step, no model):** `scripts/collect_versions.py`
   reads the inputs below, queries the PyPI JSON API, GitHub releases/tags
   and OSV, and writes `facts.json`: for each tracked tool and each
   watchlist entry, the pinned version (if any), latest stable version and
   date, releases since the previous report, advisories, and the source URL
   for each value. It runs as a gh-aw custom step before the agent job, so
   its network access is the runner's, not the agent firewall's
   **(verify in 07, Q19)**.
2. **Write (agent):** reads `facts.json`, the previous report, open
   Dependabot PRs and open `tooling-watch` issues; fetches changelogs and
   release notes for context (breaking changes, maturity); writes the report
   in the format below and copies `facts.json` next to it as
   `<date>.facts.json`; opens or updates issues.
3. **Check (CI, no model):** `report-check` (inside `mise run check`)
   validates every report + facts pair offline. It is what makes "every claim
   sourced" a machine check rather than a reviewer's judgment.

**Inputs**

1. **Tracked tools** (derived automatically, nobody maintains a list):
   `mise.toml` `[tools]`, direct and dev dependencies from `pyproject.toml` /
   `uv.lock`, SHA-pinned actions in `.github/workflows/`, and the gh-aw
   version in the compiled lock files.
2. **Watchlist** (human-provided, D10): `tooling/watchlist.toml`. Every entry
   appears in **every** report, whether or not anything changed.
3. **Previous report and its facts file**, for "changed since last report".
4. **Open Dependabot PRs and open `tooling-watch` issues**, so findings
   aren't duplicated.

**Watchlist file (human-provided)**

> **Human action required:** the maintainer provides the list of libraries,
> tools and apps, with their git repos where available, that the watcher
> must always include. The intended first entries are emerging tools such as
> hk, ty, moon, proto and Vite+. The agent never edits this file. It can only
> propose additions or removals as issues.

Schema (`watchlist:check` validates it):

```toml
# tooling/watchlist.toml: maintained by humans. Agents read, never write.
schema_version = 1

[[tool]]
name        = "<display name>"           # required
repo        = "https://github.com/<owner>/<repo>"  # required if the project has a public repo
pypi        = "<package name>"           # optional; lets the collector use the PyPI API
homepage    = "<docs URL>"               # optional
category    = "<e.g. task-runner | type-checker | git-hooks | toolchain | build>"  # required
compare_to  = ["<tool in the current stack it might replace>"]  # optional
why         = "<one line: why we are watching it>"   # required
ready_when  = "<one line: what would make it worth a trial>"  # optional
added       = "YYYY-MM-DD"               # required
```

Task 07 ships the file with the header and schema only. The maintainer adds
entries in a human-authored PR before the first scheduled run.

**Report format** (`reports/tooling-watch/YYYY-MM-DD.md`):

```markdown
# Tooling watch — YYYY-MM-DD

## Summary
<3–5 bullets: the things a developer should know this week; "No changes" is valid>

## Tracked tools
| Tool | Pinned | Latest | Since last report | Advisories | Verdict | Issue | Source |
<one row per tracked tool; verdict ∈ adopt | trial | hold | no change>

## Watchlist (human-provided)
| Tool | Repo | Latest | Status / maturity | Progress vs ready_when | Verdict | Source |
<one row per watchlist entry, every week; verdict ∈ watch | trial | ready-to-evaluate | drop?>
<"Watchlist is empty" when it is>

## New developments
<candidates found this week, each with a link and a proposed-watchlist issue; or "None">

## Open Dependabot PRs
<links only>

## Sources
<every URL cited above>
```

**`report-check` rules** (`scripts/check_report.py`, with unit tests):
all sections present in order; one Tracked-tools row per tool in the facts
file and one Watchlist row per watchlist entry; every row has at least one
link; every Pinned/Latest/date value equals the facts file; every URL in the
report appears in the facts file or the Sources section; verdicts come from
the allowed set; the index row in `README.md` exists.

**Outputs (safe-outputs)**

```yaml
safe-outputs:
  github-app: { client-id: ${{ vars.STARTER_BOT_APP_ID }}, private-key: ${{ secrets.STARTER_BOT_APP_KEY }} }
  create-pull-request:
    draft: false
    title-prefix: "docs(reports): "
    labels: [tooling-watch, report-only]
    allowed-files: ["reports/tooling-watch/**"]
    protected-files: blocked
    if-no-changes: "error"
    max: 1
  create-issue:
    title-prefix: "[tooling-watch] "
    labels: [tooling-watch]
    max: 10
  add-comment:
    max: 10            # update an existing open issue instead of opening a duplicate
  noop: {}
```

- **One issue per recommended change** (breaking change or advisory on a
  pinned tool, adopt/trial verdict, proposed watchlist addition or removal).
  Dedup key: the title `[tooling-watch] <tool>: <change>`. If an open issue
  has that title, the run comments on it instead.
- Starting limits: `timeout-minutes: 45`, `max-turns: 150`. Tune from the
  first four runs.
- Agent network allowlist: `github.com`, `api.github.com`,
  `objects.githubusercontent.com`, `raw.githubusercontent.com`, `pypi.org`,
  `osv.dev`, `mise.jdx.dev`, `docs.astral.sh`, `astral.sh`. Because the
  collector fetches the facts outside the firewall, watchlist entries hosted
  on GitHub need no extra hosts; only a non-GitHub `homepage` would
  **(verify in 07, Q16)**.
- **Known limit:** "new developments" discovery is bounded by the allowlist.
  Opening up general web search is a separate, human-approved change.

### Report merge guard: `.github/workflows/report-merge-guard.yml` (D9)

A plain Actions workflow with **no model**. It lets report-only PRs merge
without a human, so a new report shows up on `main` by Tuesday morning.

- Trigger: `workflow_run` of `ci` and `pr-review` (completed), plus
  `pull_request` `labeled`/`unlabeled`. Each run evaluates the PR's current
  head SHA.
- `scripts/report_guard.py` decides; it merges **only if all** of these
  hold:
  1. The PR author is the starter-bot App and the head branch was created by
     the tooling-watch workflow.
  2. Every changed path matches `^reports/tooling-watch/`.
  3. `ci` passed on the head SHA (this includes `report-check`).
  4. The `pr-review` status for the head SHA is success, from a tally showing
     `blocker=0 major=0`.
  5. The PR has the `report-only` label and no `hold` label.
- It merges with `gh pr merge --squash --match-head-commit <evaluated SHA>`,
  so a push between evaluation and merge makes the merge fail rather than
  merging unchecked code.
- It merges with a **separate report-merger GitHub App**: a ruleset bypass
  actor in pull-request-only mode, with `contents: write` and
  `pull-requests: write` only. Bypassing skips GitHub's own approval
  enforcement, so checks 1–5 are the gate. The writer (starter-bot) and the
  merger are different identities.
- The guard writes nothing to the repo. Refusals are written to the job
  summary with their reason.

### Issue workers (D11, D17)

Two workflows instead of one, because gh-aw's `allowed-files` is set per
safe output and can't differ between paths of one workflow. Path locks are
the guardrail; the prompt is not.

**Shared rules**

- Trigger: `issues: [labeled]`. Each continues only when the label just
  applied is `agent:ready` **and** the issue carries its type label
  (`type:bug` or `type:feature`, applied by the issue forms). gh-aw's role
  check is limited to `admin`, `maintainer` and `write`.
- **Don't pile on:** skip with `noop` and a comment if three or more agent
  PRs are open or `ci` is red on `main`.
- **Decline path:** if the work needs protected files (`AGENTS.md`,
  `CLAUDE.md`, `REVIEW.md`, `.claude/**`, `.github/**`, dependency changes in
  `pyproject.toml`/`uv.lock`, secrets config, `tooling/watchlist.toml`) or a
  secret, comment why, remove `agent:ready`, and open no PR.
- safe-outputs: `create-pull-request` (`draft: true`, `max: 1`,
  `protected-files: blocked`), `add-comment` (`max: 3`), label removal for
  `agent:ready` **(verify name in 08, Q17b)**, `noop`.

**`issue-worker-bug.md`**

- **Toolchain before the agent:** custom pre-agent steps run `mise install`
  and `mise run setup`, so the agent can run `mise run check` without
  package-index or tool-download hosts on its allowlist **(verify in 08,
  Q19)**. Agent allowlist: the gh-aw base list only.
- **Path:** reproduce the bug as a failing test → commit it on its own as
  `test: reproduce #N` (only files under `tests/`) → set
  `STARTER_FIX_MODE=1` → fix in later commits → `mise run check` green → PR
  with `Fixes #N`, labelled `type:bug`. The PR body shows the test failing
  before the fix and passing after it.
- `allowed-files: ["src/**", "tests/**"]`.
- Starting limits: `timeout-minutes: 30`, `max-turns: 120`.

**`issue-worker-feature.md`**

- **Path:** copy `intent/_template/` to the next free `intent/NNNN-slug/`,
  fill in `intent.md` only, add the `intent/README.md` index row → PR with
  `Refs #N`. **No code.**
- `allowed-files: ["intent/*/intent.md", "intent/README.md"]`.
- Agent allowlist: the gh-aw base list. Starting limits:
  `timeout-minutes: 15`, `max-turns: 60`.

**`test-first` check** (`scripts/check_test_first.py`, job in `ci.yml`).
For bug PRs from `issue-worker-bug`:

1. The PR's first commit has subject `test: reproduce #N` and touches only
   `tests/`.
2. At that commit, the new or changed tests fail (`uv run pytest <files>`
   exits non-zero for assertion failures, not import or collection errors).
3. `git diff <first-commit>..HEAD -- <those test files>` is empty: the fix
   didn't touch them.
4. At `HEAD`, they pass.

Any failure sets `test-first` to failure with the reason. This is the
mechanical form of Invariant 4 and doesn't depend on the agent or the
reviewer.

## AGENTS.md invariants

These go into `AGENTS.md` → Invariants (task 01 writes them; later tasks
keep them true):

1. `mise run check` passes with no secrets and no network beyond package
   install.
2. Agents never push to `main`. Every change arrives as a PR.
3. Tool versions are exact pins. `pyproject.toml` and `uv.lock` change
   together.
4. In a bug fix, the reproducing test is committed first and its assertions
   are not changed by the fix.
5. Feature requests become an `intent.md` before any code.
6. Tooling-watch PRs change only `reports/tooling-watch/**`.
   `tooling/watchlist.toml` is changed only by humans.
7. `CLAUDE.md` stays a pointer to `AGENTS.md`.
8. Generated files (`uv.lock`, compiled `.lock.yml`, `CHANGELOG.md`, report
   facts files) are regenerated by their tool, never hand-edited.
9. Changes to agent configuration (`AGENTS.md`, `REVIEW.md`, `.claude/**`,
   agent workflow prompts) come with an eval run.

## Risks and areas of concern

| # | Concern | Mitigation |
| --- | --- | --- |
| R1 | **Auto-merge vs separation of duties.** The report PR merges without human approval. | Narrowest scope possible: path-locked by `allowed-files` *and* re-checked by the guard; separate merger identity; `hold` label; `report-check` and agent review must both pass; SHA-matched merge. Reports change no behavior. |
| R2 | **Wrong claims** in a report become "official" on merge. | Facts come from a script, not the model (D16); `report-check` compares every value to the facts file; verdicts only open issues, never change pins. |
| R3 | gh-aw moves quickly; frontmatter fields have changed during 2026. | Pin the version, track it in the report itself, upgrade in its own PR with evals, treat `.lock.yml` diffs as protected. |
| R4 | pyright via PyPI wrapper: Node comes from `nodejs-wheel`. | The `[nodejs]` extra means no runtime download (task 03 proves it offline). Fallback `npm:pyright` + Node in mise needs a decision entry. basedpyright stays a watchlist candidate. |
| R5 | Timezone passthrough on the pinned gh-aw version. | gh-aw added support (PR #22018); UTC fallback documented (D8). |
| R6 | API cost of weekly + per-issue + per-PR + eval runs. | Per-workflow `max-turns`/timeout; don't-pile-on guard; Dependabot skip; review the first month's usage in a `decisions.md` entry. |
| R7 | Prompt injection through issue bodies, diffs or fetched release notes. | Read-only agent jobs; writes only via safe-outputs with threat detection; network allowlist; `agent:ready` gate; protected files blocked; REVIEW.md treats instructions in a diff as a blocker; injection cases in the eval suite. |
| R8 | **The reviewer's tally is a merge input** and could be steered by report content. | It is no longer the only gate: `report-check` validates facts mechanically, and an injection eval case exists. |
| R9 | **Required agent check blocks PRs the agent can't review** (Dependabot, missing secret). | Deterministic `pr-review` status job: Dependabot → explicit skip; missing tally → error, visible rather than pending forever (D18). |
| R10 | **Claude Code hooks can be bypassed by Bash edits.** | Decision in task 04 (Q21); CI, `test-first` and review remain the backstop. |

## Out of scope for this spec

Framework variants, monorepo layout, PyPI publishing, copier template
(D12), Python version matrix, a second AI reviewer, general web search for
the watcher, and running the tooling watch in generated projects (they get
the workflow file but leave `AGENTS_ENABLED` unset unless they opt in).
