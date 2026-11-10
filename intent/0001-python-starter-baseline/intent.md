---
id: "0001"
title: Python starter baseline with agent-maintained tooling
status: accepted     # draft | accepted | active | shipped | superseded | abandoned
owner: Daryl
ticket: none
created: 2026-10-24
updated: 2026-10-24
accepted: 2026-10-24 # by owner, recorded in the bootstrap commit (decisions.md D0)
---

# Intent: Python starter baseline with agent-maintained tooling

## Problem

Every new Python project in the org starts by re-deciding the same things:
how Python and CLI tools get installed, how dependencies are locked, which
linter, formatter and type checker to use, how commits are formatted, how
secrets are kept out of git, and what CI runs. The answers live in old repos,
past chat threads and people's heads. Copying a 2024-era repo brings its dead
config with it (an earlier audit found a disabled staged-lint hook, a commit
linter in the wrong hook, and about seven unused commit-emoji packages).

Even after the choices are made, they go stale. The Python tooling space moves
quickly: the main tools ship releases most weeks, and promising alternatives
appear every few months. Nobody has time to check all of this every week, so
a starter that was current in June is quietly out of date by October.

There is also no standard path for bugs and feature requests against the
starter itself. An issue gets filed and waits for someone to have a free
afternoon.

This hits two groups:

- **Developers starting a new Python project**, who want to clone something
  that already works and is already current.
- **The maintainer (Daryl)**, who wants to keep the starter current and handle
  issues without making either one a recurring manual job.

## Outcome

A **public GitHub repository in the org** that is the reference starter for
Python projects. It is built and maintained using the AI-native SDLC: every
change has a committed intent → spec → plan → reviewed PR trail.

When this is done:

1. **The starter works on a clean clone.** One tool provisions Python and
   every CLI tool at pinned versions, one tool owns dependencies and the
   lockfile, and one command runs every check locally. CI runs the same
   command.
2. **Guardrails are on from the first commit.** Lint, format, type check,
   tests, secrets scanning and conventional commit messages are enforced
   locally and in CI. Secrets are never needed for ordinary checks.
3. **Agents can work in the repo safely.** A single agent-instructions file
   lists the commands, conventions and invariants. A review policy file sets
   how PRs are reviewed. The same guardrails apply to an agent session on a
   developer's machine as to one in CI.
4. **A weekly "tooling watch" runs on its own.** Overnight every Monday into
   Tuesday, a scheduled agent checks each tracked tool and library for new
   releases, breaking changes and security advisories, and reports on every
   entry in a human-maintained watchlist of emerging tools. The report is on
   `main` by Tuesday morning without a human having to merge it. Each
   recommended change becomes its own issue; the report never changes pins
   itself.
5. **Issues get worked by an agent, with a human gate.** Once a human has
   triaged a bug report or feature request and marked it ready, an agent picks
   it up. For a bug, the agent first commits a failing test that reproduces
   it, then fixes it. For a feature, the agent writes a new `intent.md` for
   human approval before writing any code. Either way the result is a PR,
   reviewed by a separate agent session and then approved by a human.
6. **The agents' own configuration is regression-tested.** Changing the
   review policy, the agent instructions or a workflow prompt shows whether
   the agents still catch what they used to.
7. **Decisions are on record.** Tooling choices that future projects inherit
   are written down, and when a tooling-watch recommendation is adopted or
   rejected, that decision is logged too.

## Affected users and systems

- Developers who clone the starter (directly or via GitHub's "Use this
  template").
- The maintainer and any org members who triage issues.
- The org's GitHub space: repository settings, branch protection, Actions,
  GitHub Apps, and the agent integration set up for the repo.
- The Anthropic API account that pays for agent runs.
- The sibling TypeScript starter (`intent/0001-ts-starter-migration` in that
  repo), which shares conventions and should stay consistent where the
  languages allow.

## Constraints

- **Toolchain anchors (owner decision):** mise is the top-level tool
  provisioner, task runner and environment/secrets entry point. uv manages
  Python dependencies, virtualenvs and the lockfile. Nothing in the starter
  should need a tool that mise does not install.
- **Consistency with the TypeScript starter:** use the same tool family for
  commits, secret scanning, secrets at rest, git hooks and CI unless a
  Python-specific reason says otherwise, and record that reason.
- **Same checks everywhere:** CI runs the same command as a developer's
  machine. No CI-only checks of the code that can't be reproduced locally.
- **Agents never push to `main`.** Everything an agent writes arrives as a PR
  through branch protection. A human code owner approves every merge, except
  report-only PRs, which may merge through a deterministic (non-model) gate.
- **Least privilege for scheduled and issue-triggered agents:** read-only by
  default, writes only through declared outputs (open PR, open issue,
  comment), a network allowlist, no production or org-admin credentials, and
  a per-run cost or time cap.
- **Verifiable reports:** every version number, release date or advisory in a
  tooling-watch report links to its source, and that can be checked
  mechanically. If nothing changed, the run records a "no-op" so quiet weeks
  are visible.
- **Cadence:** weekly, overnight Monday into Tuesday (America/Detroit), with
  a manual run available for previews and catch-up.
- **Generated projects stay green:** a project created from the template
  must pass CI without any agent secrets or Apps; the agent workflows are
  opt-in.
- **Public-safe:** no internal hostnames, secrets, customer data or private
  org details in the repo, since the repo is public.

## Done criteria

On a clean clone with only mise installed:

```bash
mise install        # provisions python, uv and all CLI tools at pinned versions
mise run setup      # dependencies installed + git hooks installed
mise run check      # format check + lint + type check + tests + secrets scan
```

- [ ] The three commands above succeed on Linux and macOS with no secrets
      present, and `mise run check` exits non-zero on any failure.
- [ ] CI runs `mise run check` on every PR and push to `main`, and it is a
      required status check under branch protection.
- [ ] A commit with a non-conventional message is rejected locally and by
      CI.
- [ ] A commit containing a fake key-shaped string is rejected locally and
      by CI.
- [ ] The lockfile is committed, and CI fails if it is out of date.
- [ ] `AGENTS.md`, `REVIEW.md`, `intent/README.md` and `intent/_template/`
      exist and match the conventions of the TypeScript starter.
- [ ] A local Claude Code session is blocked from editing generated or
      human-only files (lockfiles, compiled workflows, the watchlist).
- [ ] A manual run of the tooling watch produces a dated report in a PR. The
      report covers every tracked tool and every watchlist entry, a
      deterministic check confirms every claim has a source and matches it,
      and one issue is opened or updated per recommended change.
- [ ] The tooling watch runs on schedule two Tuesdays in a row without a
      human starting it, and both report PRs merge without a human (or are
      held with a reason).
- [ ] A test report PR that touches a file outside the report folder is
      refused by the merge gate.
- [ ] A test bug issue marked ready is picked up by the agent. The resulting
      PR has the failing test in an earlier commit than the fix (checked
      mechanically), links the issue, and passes CI.
- [ ] A test feature-request issue marked ready makes the agent open a PR
      that contains only a new `intent/NNNN-*/intent.md`, with no code.
- [ ] Each agent-opened PR carries a `REVIEW.md` review from a session that
      did not write the change, ending in a verdict.
- [ ] A change to the review policy or an agent prompt runs a fixed eval
      suite and reports its pass rate on the PR.
- [ ] The watchlist is a version-controlled file that only humans edit,
      populated by the maintainer before the first scheduled run. The agent
      can propose changes only through issues.
- [ ] A repo created from the template passes CI with no agent secrets set.
- [ ] README explains how to use the repo as a template, the commands, and
      how the agent workflows behave and are switched on.
- [ ] Every question in `decisions.md` is answered or explicitly deferred to
      a later intent.

## Non-goals

- Adding a web framework, ML stack or app scaffold (FastAPI, Quart, Jupyter,
  etc.). The starter is the toolchain and guardrails. Framework variants can
  be later intents.
- A polyglot monorepo layout. That is a separate starter.
- Automatic dependency or tool upgrades merged without review. The tooling
  watch reports and opens issues. It does not bump pins.
- Replacing mise or uv as part of this work. The watch may recommend
  evaluating an alternative, but any switch needs its own intent and ADR.
- Publishing to PyPI or any package index.
- Agents acting on untriaged issues, issues from outside the org, or issues
  that touch repo governance (agent instructions, review policy, workflows,
  secrets config).
- Supporting Windows shells in hooks and tasks beyond what mise gives for
  free.
- A dashboard or website for the reports. Markdown in the repo is enough.

## Open questions

All nine original questions were answered on 2026-10-24, and a design review
the same day added D14–D21. See [`decisions.md`](decisions.md). Remaining
implementation-level questions are tracked there as Q10 onward.

## Related

- Design: [`spec.md`](spec.md)
- Plan: [`plan.md`](plan.md)
- Decisions: [`decisions.md`](decisions.md)
- Repo-wide rules: [`../../AGENTS.md`](../../AGENTS.md)
- Review policy: [`../../REVIEW.md`](../../REVIEW.md)
- Process: [The AI-Native SDLC Playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook)
  (Anthropic): Stage 1 intent.md, Stage 3 CLAUDE.md and hooks, Stage 4
  failing-test-first and evals, Stage 5 REVIEW.md, Stage 6 scheduled loops
- Sibling: TypeScript starter `intent/0001-ts-starter-migration`
