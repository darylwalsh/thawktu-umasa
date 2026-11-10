# Python starter

A Python starter for reproducible tooling, shared local and CI quality checks,
and agent-maintained development workflows. The accepted design uses mise for
tools and tasks, uv for Python dependencies, and reviewed intent-driven changes.
The baseline provides a small typed pydantic package, repository guidance,
and planning templates. Quality checks, hooks, and agent workflows arrive in
later tasks.

Status: under construction, see [`intent/0001-python-starter-baseline/`](intent/0001-python-starter-baseline/).

## Local setup

Install [mise](https://mise.jdx.dev/getting-started.html), review the repository
configuration, and trust it with `mise trust`. Then run:

```sh
mise install
mise run setup
mise run run
```

The demo prints `python-starter 0.1.0`. Mise provisions Python and uv; uv installs
locked dependencies in `.venv`. Python downloads by uv are disabled. See the
[task 02 evidence](intent/0001-python-starter-baseline/evidence/02-toolchain.md)
for verified pins and interpreter ownership. `mise run check` arrives in task 03.
