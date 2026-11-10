# Intent index

Every change follows an intent → spec → plan → reviewed PR trail. Active work:

| ID | Intent | Status |
| --- | --- | --- |
| 0001 | [Python starter baseline with agent-maintained tooling](0001-python-starter-baseline/intent.md) | accepted |

## Folder conventions

Copy [`_template/`](_template/) to the next unused `NNNN-slug/`, for example
`0002-offline-report-validation/`. Keep the four-digit ID stable. Each folder has
`intent.md` (what and why), `spec.md` (design), `plan.md` (execution),
`decisions.md` (choices and open questions), and `tasks/NN-slug.md` (scoped work).
Use [`tasks/00-task-template.md`](_template/tasks/00-task-template.md) for tasks.
Update this index when adding an intent or changing its status.

## Status values

- `draft`: proposed; awaiting owner acceptance.
- `accepted`: owner approved the intent; design can proceed.
- `active`: implementation is underway under an approved spec and plan.
- `shipped`: done criteria are met and the work is delivered.
- `superseded`: replaced by a linked later intent; retain the history.
- `abandoned`: intentionally stopped; record the reason.

## Stage handoffs

1. Write the intent in the originator's words, covering the problem and desired
   outcome. Tool choices and implementation details belong in the spec.
2. Owner acceptance of `intent.md` triggers design in `spec.md`; record approval
   and its source in `decisions.md`.
3. Approval of `spec.md` triggers plan mode. Prepare `plan.md` and numbered
   tasks, then obtain plan approval before implementation.
4. Execute one task per branch/PR, in order. Include acceptance evidence and
   review against [`REVIEW.md`](../REVIEW.md). A merged PR triggers the configured
   pipeline; once checks are available, CI runs the same checks as local work.
5. Record decisions and update progress before starting the next task. Mark an
   intent shipped only when its done criteria have evidence.

Intent 0001 remains `accepted` until its owner records a status transition.
Its task 01 is documentation bootstrap; tooling, CI, and agent evals arrive in
later tasks, as shown in its [plan](0001-python-starter-baseline/plan.md).
