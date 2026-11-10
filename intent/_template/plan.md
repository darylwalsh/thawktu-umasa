# Plan: <Intent title>

Implements [intent.md](intent.md) following [spec.md](spec.md).
Status: draft; record plan approval before implementation.

## Rules

- Run tasks in order, one fresh agent session, branch, and PR per task.
- Merge each task before starting the next unless the owner authorizes stacking.
- Follow [repository guidelines](../../AGENTS.md) and [review policy](../../REVIEW.md).
- Keep changes within task scope; record design departures and approval in
  `decisions.md` and update this plan in the same PR.
- Run `mise run check` or the available subset and include acceptance evidence.
- Obtain independent agent review and required human approval before merging.

## Prerequisites and human gates

- [ ] Accepted intent and approved spec, with approval sources recorded.
- [ ] <Required owner input, external setup, or credential provisioning.>

## Tasks

| Task | Outcome | Branch | Status |
| --- | --- | --- | --- |
| [01](tasks/00-task-template.md) | <First independently verifiable slice> | <type/slug> | todo |

Copy and rename the task template to `tasks/01-slug.md`, then update its link.
Task statuses: `todo` · `in progress` · `in review` · `done` · `blocked`.

## Current run

<Record approvals, authorized exceptions, current task, and evidence links.>

## Final acceptance

- [ ] Every intent done criterion has evidence.
- [ ] All task PRs are merged and documentation matches delivered behavior.
