# Task 05 handoff

Session-close record: 2026-11-13. This supersedes the current-state guidance
in [handoff-04.md](handoff-04.md); earlier handoffs remain historical evidence.

## State for owner review

- [PR #5](https://github.com/darylwalsh/thawktu-umasa/pull/5) is open and ready
  for human review: `task-05-ci-release` → `dev`. The agent has not merged it.
- Tasks 02–04 are merged into `dev`; task 05 remains **in review** in
  [plan.md](plan.md). Task 06 has not started.
- Implementation head `82e22d8d29ce922cb92de0fa1eececd2de66d785` passed
  [CI](https://github.com/darylwalsh/thawktu-umasa/actions/runs/43368565962)
  in 23 seconds. This handoff is a subsequent documentation change; use the
  PR's latest checks and review comment for its final head.
- Independent standards/spec reviews found no remaining implementation
  findings. See the [final implementation review](https://github.com/darylwalsh/thawktu-umasa/pull/5#issuecomment-6844517629).
- Acceptance proofs, release dry-run results and owner decisions are in
  [the evidence report](evidence/05-ci-release.md) and
  [decisions.md](decisions.md), D31–D36. The latest local documentation-handoff
  check output is in [05-handoff-check.txt](evidence/05-handoff-check.txt).

## Review boundaries and resolved approvals

Human code-owner approval remains required. CODEOWNERS retains `@darylwalsh`
as explicitly reaffirmed by the owner.

D35 grants PR #5 a temporary exception to the hosted head-SHA `agent-evals`
requirement until after task 06 completes. Offline evidence and independent
review still apply. No hosted eval pass is claimed; the existing hosted PR
Agent review is not the task 06 eval suite. Keep the exception scoped to PR #5.

D34's one-time public fake-key proof and commit-hook skip have been consumed.
The never-valid generic fixture in `5346069` failed hosted secret scanning,
then was immediately reverted in `22246f4`. Normal hooks apply to every
subsequent commit. D36 approves only this historical fingerprint:

```text
53460693ce332f2814cfd29c92267b0cb2fa7584:ci-secret-proof.txt:generic-api-key:2
```

The fixture is absent from the working tree. The exact exclusion passes the
history scan while still rejecting the fixture if reintroduced. Preserve
that scope; no history rewrite or broader path/rule/value exclusion is approved.
The failing post-revert scan log is historical evidence, not the current result.
Disposable negative-proof PRs #6/#7 are closed and their branches deleted.

The owner created starter-bot and confirmed installation on this repository
only. GitHub metadata verified `STARTER_BOT_APP_ID=5738669` and the presence
of `STARTER_BOT_APP_KEY`; no key value was read. The public ID is also in
`mise.toml`. The installation is owner-confirmed, not independently API-verified.
These approvals are captured in tracked decisions; resuming does not require
the ignored local approval prompt or any files under `/tmp`.

## Resume PR #5

1. Read [AGENTS.md](../../AGENTS.md), [REVIEW.md](../../REVIEW.md),
   [intent.md](intent.md), [spec.md](spec.md), [plan.md](plan.md),
   [decisions.md](decisions.md) and [task 05](tasks/05-ci-release.md).
2. Check the working tree, current PR head, CI and human review state before
   relying on this snapshot. Continue review fixes on `task-05-ci-release`
   while PR #5 is open; keep the base `dev`.
3. For changes, run `mise run setup` as needed, then `mise run check`.
   Check documentation links and whitespace, obtain independent review, and
   record evidence on the new PR head. Use normal commit/push hooks.
4. Leave merging to the owner. An agent verdict does not replace human approval.

## After owner review and merge

Read [task 06](tasks/06-gh-aw-pr-review-evals.md) before starting that work
on a fresh branch from the agreed base. Verify PR #5's actual merge and fetch
the updated base first. Task 06's context requires CI live on `main` and the
owner's `main` ruleset requiring `ci`; merging this PR into `dev` alone does
not establish those prerequisites.

No ruleset has been applied and no real release has been cut in task 05.
[GitHub setup](../../docs/github-setup.md) gives the owner settings, release
procedure and recovery steps. Release preparation is dispatched on `main`
after the workflows reach it; release tagging follows a reviewed squash merge.

Before task 06, confirm its owner prerequisites: `ANTHROPIC_API_KEY`,
`STARTER_BOT_APP_ID`, `STARTER_BOT_APP_KEY` and `AGENTS_ENABLED`. The App ID/key
presence above is already verified; the Anthropic credential and enabled flag
were not verified by this handoff. Task 06 implements gh-aw, `aw`, `pr-review`
and hosted agent evals. Its additional required checks are enabled only after
that work lands, following the owner setup guide.
