# Python starter

A Python starter for reproducible tooling, shared local and CI quality checks,
and agent-maintained development workflows. The accepted design uses mise for
tools and tasks, uv for Python dependencies, and reviewed intent-driven changes.
The baseline provides a small typed pydantic package, quality checks, repository
guidance, planning templates, local git/Claude Code hooks, and CI with a
reviewed release PR flow. Agent workflows arrive in later tasks.

Status: under construction, see [`intent/0001-python-starter-baseline/`](intent/0001-python-starter-baseline/).

## Local setup

Install [mise](https://mise.jdx.dev/getting-started.html), review the repository
configuration, and trust it with `mise trust`. Then run:

```sh
mise install
mise run setup
mise run run
mise run check
```

The demo prints `python-starter 0.1.0`. Mise provisions Python, uv, lefthook,
gitleaks, commitizen, fnox, and age; uv installs
locked dependencies in `.venv`. Python downloads by uv are disabled. See the
[task 02 evidence](intent/0001-python-starter-baseline/evidence/02-toolchain.md)
for verified pins and interpreter ownership.

## Quality checks

`mise run check` runs formatting, lint, strict typing, tests, and lockfile
verification, history/tree secret scanning, and fnox ciphertext validation in
order, stopping at the first failure. It needs no secrets or decryption keys.

| Command | Purpose |
| --- | --- |
| `mise run fmt` / `mise run fmt:check` | Format Python / check formatting |
| `mise run lint` / `mise run lint:fix` | Lint Python / apply safe fixes |
| `mise run typecheck` | Run strict pyright against package, tests, scripts, and Claude hooks |
| `mise run test` | Run pytest with branch coverage and a 95% minimum |
| `mise run lock:check` | Reject dependency metadata that disagrees with `uv.lock` |
| `mise run secrets` | Scan all refs and tracked working-tree contents |
| `mise run secrets:check` | Reject shared fnox values that are not age ciphertext |
| `mise run commit` | Create a guided Conventional Commit |
| `mise run bump` | Preview the next version and changelog without writing or tagging |

The pinned dev tools come from `uv.lock`. Pyright's Node binary is installed
with its `nodejs` extra during setup; typing works offline afterward. Pytest
blocks Python socket calls and treats unexpected warnings as errors. The socket
guard applies inside the pytest process; subprocess tests must use local commands.
CI can disable pytest's cache with `mise run test -- -p no:cacheprovider`.
See [task 03 evidence](intent/0001-python-starter-baseline/evidence/03-quality.md)
for the rule selection, coverage baseline, and negative proofs.

## Local guardrails

`mise run setup` installs lefthook safely on repeated runs; with `CI=true` it
only syncs dependencies. Pre-commit fixes and formats staged Python, re-stages
the fixes, scans staged changes for secrets, and checks staged `fnox.toml`.
Unstaged hunks are preserved. Commit-msg enforces Conventional Commits;
pre-push runs typing and tests. Pre-commit jobs run sequentially so secret
scanning sees the index after the Python writers finish.

Claude Code file-tool hooks block direct edits to generated files and the
human-owned watchlist and fnox configuration. Set `STARTER_FIX_MODE=1` after
committing a reproducing test to protect tests already tracked at HEAD; new
test files remain allowed. After a Python edit, the pinned project Ruff applies
safe fixes and formatting. Residual lint findings are reported without stopping
the session. Bash writes remain outside the file-tool guard: use the documented
generators and retain the human review gate (Q21).

The shared `fnox.toml` contains only the owner's public age recipient, with no
secrets. Owners can add encrypted values using
`mise exec -- fnox set NAME --provider age`, which prompts without echoing the
value. See the [age provider documentation](https://fnox.jdx.dev/providers/age).
Private identities stay outside the repository; local override files are ignored.
The checker validates every profile and rejects plaintext fallback defaults.

The only custom scanner exceptions are age payloads in root `fnox.toml` for the
generic API key rule, three exact historical documentation fingerprints, and
the single reverted task 05 fake-key fixture fingerprint, all approved by the
owner. See [task 04 evidence](intent/0001-python-starter-baseline/evidence/04-guardrails.md)
for versions, transcripts, timings, and the Bash coverage limit.

## CI and releases

Every PR and push to `main` runs `mise run setup` and `mise run check` in the
`ci` job. PRs also validate their commit messages with Commitizen. Ordinary
CI requires no repository secrets. Dependabot proposes weekly GitHub Actions
and uv updates.

After the workflows reach `main` and the owner configures the starter-bot
App, dispatch **Prepare release PR** on `main`. It checks the code, generates
version files and the changelog, and opens a release PR. After code-owner
approval, squash merge with the `chore(release):` title unchanged; the next
workflow tags the merged SHA and creates a GitHub Release. Nothing is
published to PyPI. See [GitHub setup](docs/github-setup.md) for the exact
ruleset, App permissions, settings, and retry instructions.
