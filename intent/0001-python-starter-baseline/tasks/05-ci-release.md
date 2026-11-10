# 05 — CI, release PR flow, Dependabot

## Context
Everything runs locally through `mise run check` (02–04). Read `AGENTS.md`,
`../spec.md` → CI and release, and D5/D19. The repo is public. Nothing is
published to PyPI. This task answers **Q20** (release-PR mechanics).

Decided, don't revisit: nothing pushes to `main` directly, including
releases. A release is a PR opened by the starter-bot App, and the tag is
created after it merges (D19).

The owner provides the maintainers team name for `CODEOWNERS` and has
created the starter-bot App (see `../plan.md` → Human gates).

## Goal
GitHub Actions runs exactly the local checks, a manual workflow opens a
release PR that commitizen prepared, merging it tags the release, and
`docs/github-setup.md` tells the owner how to apply the `main` ruleset.

## Scope
In:
- **`.github/workflows/ci.yml`**, on push to `main` and every PR. Job id and
  name `ci`, so the ruleset can require it.
  - `actions/checkout` with `fetch-depth: 0`, then `jdx/mise-action`, then
    `mise run setup`, then `mise run check`.
  - A `cz check --rev-range <base>..<head>` step for PRs, so commit-message
    rules hold in CI as well as in the hook.
  - `permissions: contents: read`. Every action pinned by commit SHA with a
    version comment. mise and uv caches on.
  - No secrets used or needed.
  - Leave a comment marking where tasks 06 and 08 add the `aw` and
    `test-first` jobs.
- **`.github/workflows/release.yml`**, `workflow_dispatch` on `main` only:
  - Mint a starter-bot App token (`actions/create-github-app-token`, pinned
    by SHA).
  - Same setup, then `mise run check`, then
    `cz bump --files-only --yes` with changelog generation (Q20: find the
    exact flags), on branch `release/vX.Y.Z`, committed as
    `chore(release): vA → vB`.
  - Push the branch and open a PR with the App token so `ci` runs on it.
  - `permissions: contents: read` for `GITHUB_TOKEN`; writes go through the
    App token.
- **`.github/workflows/release-tag.yml`**, on push to `main` when the head
  commit subject starts with `chore(release):`: read the version from
  `pyproject.toml`, create tag `vX.Y.Z`, and create a GitHub Release from the
  new CHANGELOG section. `contents: write` here only.
- **`.github/dependabot.yml`**: ecosystems `github-actions` and `uv`,
  weekly, commit prefixes `ci(deps)` and `build(deps)`.
- **`.github/CODEOWNERS`**: `* @<org>/<team>`.
- **`docs/github-setup.md`**: the exact ruleset for `main` (PRs only,
  squash/linear history, required check `ci`, one code-owner approval, no
  bypass yet), the starter-bot App (permissions, installation scope, where
  its id and key are stored). Leave clear empty sections for what tasks
  06–08 add (Anthropic key, `AGENTS_ENABLED`, `aw`/`pr-review`/`test-first`
  checks, report-merger App and bypass actor).
- Update `AGENTS.md` (CI mirrors `mise run check`; how to cut a release).

Out:
- Agent workflows (06–08). Applying the ruleset (human). Cutting a real
  release.

## Steps
1. Write `ci.yml`, open the PR, and get it green.
2. Prove CI catches failures, using throwaway commits on the PR branch,
   reverted afterwards:
   - a lint error → red;
   - a non-conventional commit message → red (the `cz check` step);
   - a fake key → red.
3. Write `release.yml` and `release-tag.yml`. Settle Q20 on a throwaway
   branch: run the bump command locally with the chosen flags and show that
   `pyproject.toml`, `uv.lock` and `CHANGELOG.md` change exactly as a full
   `cz bump` would, minus the commit and tag. Show how `release-tag.yml`
   derives the tag, and that it ignores ordinary merges.
4. Write `dependabot.yml`, `CODEOWNERS` and `docs/github-setup.md`.

## Acceptance
- CI is green on the PR and runs only `mise run check` plus the `cz check`
  step. No duplicated command lines.
- The three red cases are shown with run links.
- The release dry-run output is shown, and Q20 is answered.
- Only `release-tag.yml` has a write permission on `GITHUB_TOKEN`;
  `release.yml` writes only through the App token.
- CI takes under 5 minutes with a warm cache.

## Stop and ask if
- An action needs more than `contents: write` in `release-tag.yml`.
- The planned ruleset would block the release PR or the tag push.
- `--files-only` can't produce the CHANGELOG section; propose an
  alternative instead of falling back to pushing to `main`.
- CI takes more than about 5 minutes.

## Report
Workflow summary, permissions, run links (green and the three reds),
release dry-run output, the Q20 answer, the ruleset text for the owner to
apply, and proposed `decisions.md` entries.
