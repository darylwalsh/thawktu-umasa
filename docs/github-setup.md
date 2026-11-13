# GitHub setup

Task 05 supplies CI and the release PR flow. Apply these settings after the
workflows reach `main`; merging the implementation into `dev` alone does not
make the manual release workflow available on `main`.

## Main ruleset (owner applies)

In **Settings → General → Pull Requests**, enable squash merging, disable
merge commits and rebase merging, and select **Pull request title** as the
default squash commit message. Release PR titles must remain
`chore(release): vA → vB` so the merge triggers tagging.

In **Settings → Rules → Rulesets → New branch ruleset**, use:

| Setting | Value |
| --- | --- |
| Name / enforcement | `main` / Active |
| Target branches | Include by pattern: `main` |
| Bypass list | Empty, including administrators and starter-bot |
| Restrict deletions | On |
| Block force pushes | On |
| Require linear history | On |
| Require a pull request before merging | On |
| Required approvals | 1 |
| Require review from Code Owners | On |
| Dismiss stale approvals when new commits are pushed | On |
| Require conversation resolution | On |
| Require status checks to pass | On; `ci`, source GitHub Actions |
| Require branches to be up to date before merging | On |
| Restrict updates / creations | Off (the PR rule controls updates) |

Leave other rules off for this baseline. Do not add `aw`, `pr-review` or
`test-first` until their delivery tasks provide those checks. The `ci` name
comes from both the workflow job ID and job name. Run a PR once if GitHub
has not yet offered the check in its picker.

The owner selected `* @darylwalsh` for this personal repository. On transfer
to an organization, replace it with a visible team that has explicit write
access, such as `* @organization/maintainers`. Keep CODEOWNERS on the base
branch. GitHub does not allow authors to approve their own PRs: a human-authored
PR needs another eligible code owner. The starter-bot release PR can be
approved by Daryl.

This is a **branch** ruleset targeting `main`, not a tag ruleset. It allows
the App to push `release/vX.Y.Z` and propose a PR without bypassing review.
It allows the tagging workflow to create `vX.Y.Z` after that PR merges.
Before applying any organization-wide or tag rules, verify that they still
permit these two operations; do not add a bypass to work around them.

## Starter-bot App (owner configures)

Create a GitHub App named for this installation (GitHub requires a unique
App name). Webhooks are not needed for this release workflow. Grant repository
permissions **Contents: read/write**, **Pull requests: read/write**, and
**Issues: read/write** (reserved for tasks 06–08); Metadata is automatically
readable. No administration, Actions, workflow-file or organization permission
is needed. Install it on **only this repository**.

Under **Settings → Secrets and variables → Actions**, store:

| Type | Name | Value |
| --- | --- | --- |
| Repository variable | `STARTER_BOT_APP_ID` | App ID from the App settings |
| Repository secret | `STARTER_BOT_APP_KEY` | Generated private key, including PEM delimiters |

For this repository, App ID `5738669` is also in `mise.toml` for local
commands. The release workflow reads the **Actions variable** above, not
the mise environment value; configure that variable separately in template
copies. The App ID is public metadata, while its private key stays in Actions.

Never commit or paste the private key into a PR. The token action accepts the
App ID with its `app-id` input; upstream prefers Client ID for new setups,
but the baseline deliberately retains the specified App ID contract.
The release workflow narrows each installation token to this repository and
Contents/Pull requests write only, and revokes it at job completion.
The App is **not** a ruleset bypass actor.

## Cut a release

1. Merge intended changes into `main`. Optionally run `mise run bump` locally
   to preview the next version; it always uses `--dry-run --yes`.
2. In Actions, run **Prepare release PR**, selecting **main**. Other refs
   are skipped. It checks the exact dispatch commit, runs setup and the full
   quality gate, then runs `cz bump --files-only --yes --changelog`.
3. Review `release/vX.Y.Z`: only `pyproject.toml`, `uv.lock`, and `CHANGELOG.md`
   are staged. The App pushes that branch and opens the PR into `main`, so
   the ordinary PR checks run. Obtain code-owner approval and green `ci`.
4. Squash merge, retaining the release title. **Tag merged release** reads
   the version and newest changelog section from that exact merged SHA,
   creates `vX.Y.Z` there, and publishes those notes as a GitHub Release.
   Ordinary commit subjects skip the job. Nothing is published to PyPI.

Release preparation serializes runs. No eligible commits means Commitizen
fails without publishing. An existing release branch is never force-pushed:
finish or close the existing release PR before preparing another. If branch
push succeeded but PR creation failed, open a PR from that existing branch
through the App or owner account; do not delete reviewed work to retry.
If `main` moves, update the release PR through normal review, regenerate
the files with Commitizen if its notes/version need refreshing, and rerun CI.

The tagging job can be retried after a publication failure: it accepts an
existing tag only if it points to the same merged SHA, and leaves an existing
GitHub Release intact. Investigate a mismatched tag; never move a released tag.

## Tokens and tools

`ci.yml` uses read-only `GITHUB_TOKEN` and no repository secrets.
`release.yml` also grants only Contents read to `GITHUB_TOKEN`; all branch
and PR writes use the short-lived App token. `release-tag.yml` alone among
these three workflows grants Contents write to `GITHUB_TOKEN`. GitHub Releases
and tags require no additional write permission. The pre-existing PR Agent
workflow separately has Issues/Pull requests write; task 05 does not change it.

Actions are pinned to full commit SHAs with version comments. mise 2026.11.6
installs the project pins; mise and uv download caches are enabled. Release
jobs additionally install gh 2.104.0 with mise; contributors running `check`
do not need gh. Weekly Dependabot updates cover GitHub Actions and uv, with
`ci(deps)` and `build(deps)` commit prefixes. Mise tool pins remain reviewed
manual changes until tooling watch provides recommendations.

## Task 06: Anthropic key and agent switch

<!-- Task 06 documents ANTHROPIC_API_KEY and AGENTS_ENABLED here. -->

## Task 06: aw and pr-review required checks

<!-- Task 06 supplies these checks and their ruleset additions. -->

## Task 07: report-merger App and bypass actor

<!-- Task 07 documents the separate App and pull-request-only bypass here. -->

## Task 08: test-first required check

<!-- Task 08 supplies this check and its ruleset addition. -->

## References

- [Commitizen bump flags](https://commitizen-tools.github.io/commitizen/commands/bump/)
- [mise action inputs and caching](https://github.com/jdx/mise-action)
- [GitHub App token action](https://github.com/actions/create-github-app-token)
- [Available ruleset rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [Code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Dependabot configuration](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)
