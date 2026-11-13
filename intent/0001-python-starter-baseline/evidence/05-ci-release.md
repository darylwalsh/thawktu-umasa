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
D33 explains their isolated-PR method: reverts preserve the invalid message
in checked history. Those proofs disabled no local hooks. D34 below supersedes
D33 for the fake-key proof only; no delivery-branch history was rewritten.

The owner subsequently authorized one generic fake-key proof directly on PR #5
(D34), overriding the isolated-branch method for that case. Commit
`53460693ce332f2814cfd29c92267b0cb2fa7584` contained one freshly invented,
never-valid random hex value assigned to `api_key` in `ci-secret-proof.txt`.
It used no provider-specific format. Its commit message labels it a test
fixture, and the single explicitly permitted `git commit --no-verify` was
used only for that commit. Pre-push checks remained enabled.

[Hosted CI run 43363169017](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43363169017)
passed format/lint/types/tests/lock, then failed in `mise run secrets` with
one leak and exit 1. The fixture was immediately reverted and pushed in
`22246f4`; no fixture file remains in the working tree. All three hosted
negative proofs now have run links. No real credential was used.

After the revert, the all-history scan correctly still detected this exact
historical finding:

```text
53460693ce332f2814cfd29c92267b0cb2fa7584:ci-secret-proof.txt:generic-api-key:2
```

D36 records the owner's subsequent explicit approval for this exact fingerprint
only. `.gitleaksignore` now excludes that one commit/path/rule/line; no path,
rule or value-wide exception was added. The historical scan passes, and
reintroducing the same fixture in a working-tree scan still fails. The
[post-revert check output](05-post-proof-check.txt) preserves the earlier red
state; [the full check output](05-check.txt) records validation after D36.

The implementation before the proof was green in
[CI run 43361875700](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43361875700)
at `d911435` (32 seconds). This is historical evidence, not a current-head pass.

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

D35 records the owner's temporary hosted head-SHA `agent-evals` exception for
PR #5 until after task 06 completes. Offline evidence remains required, no
hosted eval pass is claimed, and all other review requirements still apply.
The owner confirmed starter-bot creation with public App ID `5738669` and
added it to `mise.toml`. Read-only GitHub CLI metadata checks confirmed:

```text
Actions variable STARTER_BOT_APP_ID = 5738669
Actions secret STARTER_BOT_APP_KEY is present
```

No secret value was accessed. The workflow already reads these Actions
settings. The owner confirmed the App is installed on this repository only
in Prompt 06. The earlier API lookup was unavailable (HTTP 403); installation
is owner-confirmed, not independently API-verified. No authenticated release
run is claimed. The owner reaffirmed `@darylwalsh` for CODEOWNERS.
Human approval is still required; this evidence is not merge authorization.

The [final implementation review](https://github.com/darylwalsh/thawktu-umasa/pull/5#issuecomment-6844517629)
supersedes the earlier open findings. Separate standards and spec sessions
reported `blocker=0 major=0 minor=0 note=0`, verdict `approve`.
[CI at implementation head 82e22d8](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43368565962)
passed in 23 seconds. The hosted PR Agent also
[completed successfully](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43368711031)
and reported no major/security issues or code suggestions through that head.
This PR Agent review is separate from the task 06 hosted eval suite.

The [task 05 handoff](../handoff-05.md) records the session-close state and
resume prerequisites. The documentation handoff has a separate
[local check log](05-handoff-check.txt); its head-specific CI and independent
review are recorded on PR #5. Human code-owner approval remains required;
no merge is authorized by this report.
