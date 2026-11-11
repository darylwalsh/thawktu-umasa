# Task 04 guardrail evidence

Linux verification, 2026-11-10. Branch `build/hooks`, targeting `dev` per
User Prompt 04. Task 03 merged in PR #3 before implementation began.

## Pins and references

`mise latest` selected the following stable versions; installation and version
commands succeeded. Existing Python, uv, and project dependency pins are unchanged.

```text
$ mise exec -- cz version
4.19.3
$ mise exec -- lefthook version
2.2.2
$ mise exec -- gitleaks version
8.30.1
$ mise exec -- fnox --version
fnox 1.48.0
$ mise exec -- age --version
v1.3.2
```

- [lefthook 2.2.2](https://github.com/evilmartians/lefthook/releases/tag/v2.2.2),
  [jobs and groups](https://lefthook.dev/configuration/jobs/),
  [stage_fixed](https://lefthook.dev/configuration/stage_fixed/).
- [gitleaks 8.30.1 defaults](https://github.com/gitleaks/gitleaks/blob/v8.30.1/config/gitleaks.toml)
  and [configuration](https://github.com/gitleaks/gitleaks#configuration).
- [commitizen 4.19.3](https://github.com/commitizen-tools/commitizen/releases/tag/v4.19.3)
  and [bump configuration](https://commitizen-tools.github.io/commitizen/config/bump/):
  all seven configured keys verified, including the `uv` version provider.
  Mise's supported `pipx:` compatibility prefix uses uv with `uvx = true`:
  [backend reference](https://mise.jdx.dev/dev-tools/backends/pypi.html).
- [fnox 1.48.0](https://github.com/jdx/fnox/releases/tag/v1.48.0),
  [age provider](https://fnox.jdx.dev/providers/age),
  [configuration](https://fnox.jdx.dev/reference/configuration),
  [age 1.3.2](https://github.com/FiloSottile/age/releases/tag/v1.3.2).
  Verified `recipients`, `type`, `default_provider` and the base64 age envelope
  against actual encryption of a non-secret proof value using the public recipient.
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks),
  [settings](https://code.claude.com/docs/en/settings), and
  [permissions](https://code.claude.com/docs/en/permissions): verified the
  `hooks`, event, `matcher`, `type`, `command`, `timeout`, `permissions.allow`
  and `permissions.deny` keys. Native host: Claude Code 2.1.312.

`uv lock` was regenerated after the tool configuration changes in
`pyproject.toml`; dependency metadata is unchanged, so the generated `uv.lock`
has no diff. `uv lock --check` succeeds. No generated file was hand-edited.

## Hook matrix

| Boundary | Command/script | Behavior |
| --- | --- | --- |
| pre-commit, staged Python | `hooks:lint`, then `hooks:format` | Safe Ruff fixes, formatting, `stage_fixed: true` on both jobs |
| pre-commit | `secrets:staged` | Pinned gitleaks scans the index, with redacted output |
| pre-commit, staged fnox | `secrets:staged-fnox` | Validates the index, including profiles and defaults |
| commit-msg | `cz check --commit-msg-file` | Rejects non-conventional messages |
| pre-push | `typecheck`, `test` | Strict typing and offline tests, in parallel |
| PreToolUse, Edit/Write/MultiEdit/NotebookEdit | `guard_paths.py` | Blocks generated/human-owned paths; fix mode protects tests at HEAD |
| PostToolUse, same matchers | `format_edited.py` | Project Ruff fixes then formats Python; residual findings are advisory |

The two Ruff writers share a sequential group inside the parallel pre-commit
hook. Lefthook preserves partial staging. Hook commands use canonical mise tasks
or pinned tools. Claude scripts are stdlib-only and invoked with
`uv run --no-project`; PostToolUse uses `.venv/bin/ruff` from the project.
The guard handles absolute paths, relative paths with `cwd`, symlink aliases,
notebook paths, and multi-target edits. Malformed guard events and git failures
are denied; formatter failures are advisory.

## History findings and exclusions

The first full-history scan reported three findings in imported skill
documentation at commit `fe357dc0bea4114811ec2706b08e0916948b1082`:

| Rule | Historical file | Line |
| --- | --- | --- |
| generic-api-key | `.agents/skills/fnox-security-best-practices/SKILL.md` | 26 |
| generic-api-key | `.agents/skills/mise-environment-management/SKILL.md` | 403 |
| curl-auth-header | `.agents/skills/github/SKILL.md` | 74 |

Implementation stopped as required. The owner explicitly authorized exact
fingerprint exclusions for these apparent documentation examples. The seven-line
`.gitleaksignore` records only those three commit/path/rule/line fingerprints and
their reasons. No path or commit was excluded wholesale; history was not rewritten.

```text
$ gitleaks git --redact --log-opts=--all --no-banner
13 commits scanned.
no leaks found
```

The only custom rule allowlist extends `generic-api-key` with `condition = "AND"`,
root path `^fnox\.toml$`, and secret prefix
`^YWdlLWVuY3J5cHRpb24ub3JnL3Yx`. It does not exempt other rule types or an entire
line. Directory scans use root-relative paths. A global path allowlist was rejected
because directory traversal skipped the matching file even with a pattern condition.

Actual gitleaks positive/negative proofs:

```text
encrypted payload in fnox.toml: exit 0, no leaks
same payload in other.toml: exit 1, 1 finding
plaintext synthetic GitHub token alongside encrypted fnox payload: exit 1, 1 finding
```

Offline regression tests also check `nested/fnox.toml` is not exempt. Tests use
synthetic envelopes and token shapes created at runtime, never real credentials.
`secrets` scans every ref and a snapshot of tracked working-tree contents only;
deleted files are omitted and symlinks are scanned as link text without following
their targets. Untracked local secrets and ignored local configuration are not
copied into the snapshot.

## Git hook proofs

A disposable clone at `/tmp/task04-proof`, branch `task04-proof`, installed hooks
using `mise run setup` twice, then passed `mise run check` with no secrets.
The proofs used actual `git commit` invocations with no hook bypass.

```text
reject update stuff: exit 1
  commit validation: failed
reject synthetic credential: exit 1
  [secrets:staged] ERROR task failed
reject staged plaintext despite clean working copy: exit 1
  fnox.secrets.PROOF: require age ciphertext and no plaintext default;
  use `fnox set PROOF --provider age` (hidden prompt)
accept conventional commit and format/restage: exit 0
  1 file reformatted
  Commit validation: successful!
$ git show HEAD:proof.py
PROOF_VALUE = {"answer": 42}
accept partial staging: exit 0
$ git show HEAD:proof.py
PROOF_VALUE = {"answer": 43}
```

For the last proof, `LOCAL_ONLY = 5` stayed in the working tree and was absent
from the commit. Synthetic credentials were removed from the scratch index before
any successful commit. The scratch branch was deleted after the proofs. No proof commits were pushed. The complete output is in [04-git-hooks.txt](04-git-hooks.txt).

## Native Claude Code hook evaluation

After explicit owner approval for disclosure of these repository files to the
configured Claude service, a fresh Claude Code 2.1.312 session ran in the
disposable clone with `STARTER_FIX_MODE=1`, file tools only, hooks enabled, and
no permission bypass. Session `6fa69191-344e-403e-8cff-7d753343571a` completed
without a host error. The initial implementation was `93ad096`; subsequent
final-code re-evaluation passed all four cases in session
`6a71b082-27bd-49d2-bfbd-0817821699b8` (16.882 s); the complete extracted
[final native transcript](04-native-hooks.txt) records actual tool results.

Extracted native tool transcript:

```text
Edit /tmp/task04-proof/uv.lock
PreToolUse:Edit hook error:
Blocked uv.lock: generated lockfile; regenerate with `uv lock`.

Write /tmp/task04-proof/tooling/watchlist.toml
PreToolUse:Write hook error:
Blocked tooling/watchlist.toml: human-only watchlist; propose the change in an issue.

Edit /tmp/task04-proof/tests/test_models.py
PreToolUse:Edit hook error:
Blocked tests/test_models.py: fix mode protects tests tracked at HEAD;
preserve the reproducing assertion and fix the implementation. New test files are allowed.

Write /tmp/task04-proof/tests/test_native_hook_proof.py
Allowed. PostToolUse formatted the file. Read-back and independent disk inspection:
NATIVE_PROOF = {"formatted": True}
```

The host warned that the disposable directory had not been interactively trusted:
its three `permissions.allow` entries were ignored. Explicit file-tool permissions
were supplied on the CLI for this bounded proof. The registered project hooks
still executed, as the actual tool-result denials above demonstrate. No trust
file or existing user hooks were modified.

Unit evaluations feed actual hook JSON through stdin to both `main` entrypoints;
they exercise all four matchers, both sides of fix mode, git failures, symlinks,
malformed events, multiple targets, Ruff command arguments, residual lint output,
timeouts, and missing tools. These are local evaluations, not the hosted suite.
`mise run evals` and the hosted `agent-evals` status are unavailable until task 06;
no hosted run or head-SHA status is claimed. Human code-owner approval is required.

## Bump and timing proofs

```text
$ mise run bump -- --dry-run
[bump] $ cz bump --dry-run --yes --dry-run
chore(release): v0.1.0 → v0.2.0
tag to create: v0.2.0
increment detected: MINOR

## v0.2.0 (2026-11-10)

### Feat

- **guardrails**: enforce local hooks and encrypted configuration
```

No version, tag, or changelog was written in the working branch. Since dry-run
does not list file writes, an additional disposable-clone `cz bump --files-only
--yes` proof confirmed `pyproject.toml` and the `python-starter` entry in `uv.lock`
both became `0.2.0`, and `CHANGELOG.md` was generated. These scratch outputs were
restored/removed afterward. The pending `.gitleaks.toml` correction was excluded
from the before/after changed-file comparison. Release mechanics remain task 05.

Measured on this Linux machine with installed tools:

- Typical pre-commit: **0.34 s** (target under 3 s).
- Registered PostToolUse command, including mise/uv startup and both Ruff passes:
  **0.111 s** (target under 1 s).

`mise doctor` reported no problems, with existing global PATH/backend warnings
unrelated to the project pins. No global tool configuration was changed.

## Independent review correction

Independent review found that normalizing `..` before resolving a directory
symlink could miss the actual protected target. The reproducing test was committed
first in `8272beb`, then passed unchanged after fix `c764c8d`. See the
[red output](04-symlink-red.txt) and [green output](04-symlink-green.txt).
The fix checks both the normalized lexical path and the original resolved target.
The independent reviewer rechecked the correction and final native transcript;
the remaining finding is the unavailable hosted head-SHA eval. See the
[review](04-review.md). The PR remains a draft unless the owner grants a temporary
exception; native/offline evidence is not represented as a hosted run.

## Q21 and inherited decisions

D26 accepts the documented Bash-write gap: file-tool hooks do not intercept
`sed`, redirection, `tee`, or arbitrary interpreter writes. A token denylist would
be incomplete and would also obstruct legitimate generators. Git checks and
independent/human review are backstops; these hooks are not a sandbox.

D27 chooses stdlib Python instead of Bash for portable TOML validation. D28
records the narrowly scoped exceptions and the owner's approval. D29 records the
pins, deterministic Ruff order, and dry-run-only local bump. See [ADR 0002](../../../docs/decisions/0002-local-guardrails.md). These are proposed
inherited choices for the code-owner review of this PR.

## Final verification

Saved terminal logs normalize ANSI colors and trailing whitespace only.

Final result: **90 tests passed, 96.98% coverage**, with strict types and both
secret checks green. Local Markdown links resolved and lefthook validation passed.

The complete `mise run check` output is saved in [04-check.txt](04-check.txt).
It includes both secrets tasks and hook script coverage. Whitespace, local links,
external references, lefthook validation, and the absence of `hk.pkl`, pre-commit,
and commitlint configuration are checked separately. macOS execution remains the
task 09 platform acceptance gate; it was not available in this Linux workspace.
