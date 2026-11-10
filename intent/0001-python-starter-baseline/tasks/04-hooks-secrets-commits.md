# 04 — Git hooks, Claude Code hooks, secrets, commitizen

## Context
`mise run check` covers formatting, lint, types, tests and the lockfile
(02–03). Read `AGENTS.md` (Invariants, Git conventions), `../spec.md` → Git
hooks, Claude Code hooks, Secrets, Tool configuration → commitizen, and
D4/D5/D6/D14. This task answers **Q21** (Claude Code hooks vs Bash edits).

Decided, don't revisit: **lefthook** (D4, no `hk.pkl`); **Claude Code
hooks** in `.claude/settings.json` (D14); **commitizen** with
`version_provider = "uv"` (D5); **gitleaks** + **fnox/age** (D6).

The owner provides the **age public key** (see `../plan.md` → Human gates).
Never generate, request or handle a private key.

## Goal
Bad changes are stopped before they leave the machine. Git hooks stop bad
commits: unformatted or unlinted staged Python, secrets, plaintext
`fnox.toml` values, and non-conventional messages. Claude Code hooks stop an
agent session from editing generated or human-only files, and keep edited
Python formatted.

## Scope
In:
- `mise.toml` `[tools]`, exact pins: `lefthook`, `gitleaks`,
  `pipx:commitizen` (uv-backed), `fnox`, `age`.
- **`lefthook.yml`**, as in `../spec.md` → Git hooks:
  - pre-commit (parallel, staged only): `ruff format` and `ruff check --fix`
    with `stage_fixed: true`, gitleaks on staged changes, and
    `mise run secrets:check` when `fnox.toml` is staged.
  - commit-msg: `cz check --commit-msg-file {1}`.
  - pre-push: `mise run typecheck`, `mise run test`.
- `setup` now also runs `lefthook install`, which must be safe to re-run.
- **Claude Code hooks (D14)**, as in `../spec.md` → Claude Code hooks:
  - `.claude/settings.json`: PreToolUse and PostToolUse hooks on
    `Edit|Write|MultiEdit|NotebookEdit`, plus the `permissions` allow/deny
    lists from the spec. Verify every key against the current Claude Code
    hooks and settings reference.
  - `.claude/hooks/guard_paths.py`: blocks `uv.lock`,
    `.github/workflows/*.lock.yml`, `CHANGELOG.md`,
    `reports/tooling-watch/*.facts.json`, `tooling/watchlist.toml`,
    `fnox.toml`; and, when `STARTER_FIX_MODE=1`, edits to files under
    `tests/` that are tracked at `HEAD`. Exit 2 with a message naming the
    rule and the way forward (for example "regenerate with `uv lock`").
  - `.claude/hooks/format_edited.py`: runs `ruff format` and
    `ruff check --fix` on the edited file when it is `*.py`; never fails the
    session on a lint finding it can't fix (it reports it).
  - Both stdlib-only, run with `uv run --no-project`, unit-tested in
    `tests/scripts/` by feeding hook JSON on stdin. Add `.claude/hooks` to
    pyright `include` and `scripts`/`.claude/hooks` to coverage.
  - **Q21:** decide whether to add a `Bash` matcher that refuses commands
    that write in place to a blocked path (`sed -i`, `>` redirection,
    `tee`), or to accept the gap. Record the choice and its reason.
  - `AGENTS.md`: one line under Git conventions on fix mode
    (`STARTER_FIX_MODE=1` after the reproducing test is committed).
- **`.gitleaks.toml`**: extends the default rules. Allow-list only with
  justification: age ciphertext in `fnox.toml`, scoped by path **and** the
  age payload prefix.
- **`fnox.toml`**: `default_provider = "age"`, the owner's recipient, and no
  secrets. Document how to add one in `AGENTS.md` (one line, linking to
  fnox docs).
- **`secrets:check`**: `scripts/check_fnox.py` (stdlib `tomllib`, run with
  `uv run`) fails on any non-ciphertext value, with unit tests. A Python
  script instead of the TS starter's Bash checker so it works on macOS
  (proposed decision).
- **`secrets`** task: gitleaks on full history plus the tracked working
  tree.
- **commitizen** in `[tool.commitizen]`, keys from `../spec.md`. Verify each
  key against the pinned version's docs.
- mise tasks: `commit` (`cz commit`), `bump` (`cz bump`; `--dry-run` only in
  this task).
- Add `secrets` and `secrets:check` to `check`. Update `AGENTS.md` →
  Commands.

Out:
- CI and the release workflows (05).
- Real secrets of any kind.

## Steps
1. Pin and install the tools, then check `mise exec -- cz version`,
   `lefthook version`, `gitleaks version` and `fnox --version`.
2. Write `lefthook.yml` and wire `lefthook install` into `setup`.
3. Write the Claude Code hook scripts and their tests first, then
   `.claude/settings.json`. Settle Q21.
4. Configure gitleaks and run a full-history scan. Report findings. Don't
   rewrite history.
5. Write `fnox.toml` and `scripts/check_fnox.py` with tests.
6. Configure commitizen and the commit-msg hook.
7. **Git hook proofs**, on a scratch branch:
   - message `update stuff` → rejected;
   - a file containing a fake key (for example `sk-proj-` + 40 random
     chars) → rejected;
   - a plaintext `value = "not-encrypted"` entry in `fnox.toml` → rejected;
   - an unformatted `.py` file staged → hook reformats it and re-stages it;
   - a correct conventional commit → accepted.
8. **Claude Code hook proofs**, in a fresh Claude Code session in this repo:
   - ask it to edit `uv.lock` by hand → blocked, with the message;
   - ask it to add a line to `tooling/watchlist.toml` → blocked;
   - with `STARTER_FIX_MODE=1`, ask it to change an assertion in
     `tests/test_models.py` → blocked; creating a new test file → allowed;
   - ask it to write a badly formatted `.py` file → the file on disk is
     formatted afterwards.

   Delete the scratch branch afterwards.
9. Run `mise run bump -- --dry-run` and confirm it would update both
   `pyproject.toml` and `uv.lock`.
10. Time the pre-commit hook on a typical change (target under 3 seconds)
    and a PostToolUse hook run (target under 1 second).

## Acceptance
- `mise run setup` installs the git hooks on a fresh clone.
- All git hook and Claude Code hook proofs behave as stated. Paste the
  outputs (session transcripts for the Claude Code ones).
- The bump dry-run shows the next version, the changelog section, and both
  files touched.
- `mise run check` passes and includes both secrets tasks and the hook
  script tests.
- No `hk.pkl`, `.pre-commit-config.yaml` or commitlint config in the repo.
- Q21 answered.

## Stop and ask if
- The owner hasn't provided the age recipient.
- gitleaks finds anything in history.
- The `fnox.toml` allow-list can't be scoped tighter than the whole file.
- `version_provider = "uv"` doesn't update `uv.lock`.
- pre-commit takes more than about 10 seconds, or a Claude Code hook more
  than about 2 seconds.
- A hook you need isn't expressible with the current Claude Code hook
  events.

## Report
Pins, hook matrix (git hook → commands; Claude Code event → script → rules),
allow-list entries with reasons, proof outputs, bump dry-run output, hook
timings, the Q21 answer, and proposed `decisions.md` entries (including
"Python secrets checker instead of Bash").
