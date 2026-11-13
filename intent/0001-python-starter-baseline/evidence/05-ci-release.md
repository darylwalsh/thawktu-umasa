# Task 05: CI and release evidence

Implementation branch: `task-05-ci-release`, based on task 04's merge
`6f8b9b7634a009ccd30833b1b194c6b8b8ba0d98`, targeting `dev` in
[PR #5](https://github.com/darylwalsh/thawktu-umasa/pull/5).

## Workflow behavior and permissions

- `ci.yml`: push to `main` and every PR, job ID/name `ci`, full checkout,
  mise 2026.11.6, mise/uv caches, `mise run setup`, `mise run check`, and
  PR-only `cz check --rev-range "$BASE_SHA..$HEAD_SHA"`. Contents read only;
  no repository secrets. Future `aw`/`test-first` jobs have a marker.
- `release.yml`: dispatch on `main` only, check the event SHA, generate
  version files/changelog, commit on `release/vX.Y.Z`, push and open a PR
  with a repository-scoped App token. Built-in token remains Contents read.
  The App token requests only Contents/Pull requests write.
- `release-tag.yml`: only a `chore(release):` head subject on `main` runs
  tagging. Reads the version/newest changelog section at the event SHA;
  creates the tag there and a GitHub Release. Contents write only.
- Every action added in task 05 has a verified full commit SHA and version
  comment. gh 2.104.0 is installed through mise only in release jobs (D32).
- The pre-existing `pr-agent.yml` separately has Issues/Pull requests write
  and an unpinned action; task 05 leaves that workflow unchanged. The
  task-05 workflow permission claims do not imply otherwise.

The [owner setup guide](../../../docs/github-setup.md) contains the exact
ruleset and App setup instructions. It requires PRs, squash/linear history,
`ci`, one code-owner approval and no bypass; only `main` is targeted, leaving
release branches and tags writable. CODEOWNERS uses the explicitly approved
`@darylwalsh` identity for this personal repository. No ruleset was applied.

## Hosted CI

| Case | Evidence | Observed result |
| --- | --- | --- |
| First green, `bca8634` | [CI run](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43355435278/attempts/1) | All steps passed; 30 seconds, 02:55:17–02:55:47 UTC on 2026-11-13 |
| Warm-cache green, `bca8634` | [CI attempt 2](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43355435278/attempts/2) | 19 seconds, 03:01:34–03:01:53 UTC on 2026-11-13; logs confirm exact-key mise and uv cache hits |
| Lint failure | [CI run](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43355594006), [closed PR #6](https://github.com/darylwalsh/thawktu-umasa/pull/6) | `mise run check` failed with Ruff F821 for the deliberately undefined name |
| Invalid commit message | [CI run](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43355816226), [closed PR #7](https://github.com/darylwalsh/thawktu-umasa/pull/7) | Quality gate passed; `Check PR commit messages` failed |

The lint and invalid-message branches were deleted after recording their runs.
D33 explains why these isolated PRs replace task 05's proposed revert method:
reverts preserve the invalid message and fake secret in checked history.
No local hook was disabled and no delivery-branch history was rewritten.

The hosted fake-key proof is pending explicit owner approval after automatic
approval review rejected publishing credential-shaped test data to a public
branch/PR. No fake credential was published by that attempt. The first local sequential
alphabet fixture was not detected. A replacement is constructed from SHA-256
of the public label `task05-public-nonfunctional-fixture`, truncated to 36 hex
characters with the provider prefix. It was never issued by a provider, and
pinned gitleaks rejected it locally (exit 1, one finding, redacted output).
That is a local proof only; public publication still awaits approval.
Final-head CI evidence is being collected.

## Q20: files-only equals full bump

Two independent disposable clones started at `6f8b9b7`, each on `proof/q20`.
One ran `mise exec -- cz bump --files-only --yes --changelog`, the other ran
`mise exec -- cz bump --yes --changelog`. Commitizen 4.19.3 used the existing
`version_provider = "uv"` configuration. Both printed:

```text
chore(release): v0.1.0 → v0.2.0
tag to create: v0.2.0
increment detected: MINOR
```

Byte comparisons passed for all three outputs:

```text
pyproject.toml IDENTICAL
uv.lock IDENTICAL
CHANGELOG.md IDENTICAL
```

Files-only left HEAD at `6f8b9b7`, no tags, two modified version files and
one untracked generated changelog. Full bump created commit `484cbfb` and
tag `v0.2.0` in its disposable clone. Neither clone was pushed. There is no
need to run a second changelog command or hand-edit generated files. The
current CLI deprecates `--files-only` in favor of `--version-files-only`, but
the requested spelling is supported at the exact pin. D31 answers Q20.

`mise run bump` on the delivery checkout remained a non-mutating preview:

```text
[bump] $ cz bump --dry-run --yes
chore(release): v0.1.0 → v0.2.0
tag to create: v0.2.0
increment detected: MINOR

## v0.2.0 (2026-11-12)

### Feat

- **guardrails**: enforce local hooks and encrypted configuration

### Fix

- **guardrails**: scope ciphertext exceptions to scanned findings
- **guardrails**: preserve protected targets through symlink traversal

### Refactor

- **lefthook**: Run the pre-commit jobs sequentially
```

## Local validation

`mise run setup` succeeds with hooks installed. [Full check output](05-check.txt)
records 90 passing tests, 96.98% coverage, zero typing diagnostics, fresh
lockfile and clean history/tree/fnox scans. No project dependency changed.
Pinned actionlint 1.7.7 (download checksum verified) accepts all three new
workflows. Whitespace and documentation links are checked before commit.

The actual inline release parser was extracted from the workflow and executed
against generated fixture files. It selected only the newest section and
rejected mismatched/missing/empty sections and an unchanged version. Ordinary
merge subjects and release-looking text only in a body do not trigger tagging.

The actual publication shell was executed with a disposable local bare Git
remote and a recording gh stub. These cases passed:

```text
new tag and publication PASS
same-SHA retry does not republish PASS
retry after publication failure PASS
conflicting tag fails without mutation PASS
```

The remote tag resolved to the expected commit; publication used
`--verify-tag` and the extracted notes file. These are local behavior proofs,
not a claim that an App-authenticated release was dispatched. Cutting a real
release is explicitly outside task 05.

## Independent review and remaining gates

Separate standards and spec review sessions approved the first CI increment.
Full review found a constant tag-concurrency group could let an ordinary push
replace a queued release. It now includes `${{ github.sha }}` so only retries
of the same commit share the group. D31–D33 and the plan record the implementation
and scope adjustments.

The AGENTS.md change lacks a hosted head-SHA `agent-evals` run: task 06 supplies
that workflow. D30 exempts PR #4 only, so this remains a REVIEW.md major until
the owner grants a separate exception or eval evidence is available.
Starter-bot installation and Actions variable/secret confirmation are pending.
Human approval is still required; this evidence is not merge authorization.
