---
name: lefthook-mastery
description: >-
  This skill should be used when the user asks about "lefthook", "git hooks
  manager", "lefthook.yml", "lefthook config", "pre-commit hooks", "pre-push
  hooks", "commit-msg hooks", "stage_fixed", "lefthook install", "lefthook
  run", "lefthook parallel", "lefthook piped", "lefthook skip", "lefthook
  tags", "lefthook glob", "lefthook scripts", "lefthook docker", "lefthook
  remotes", "lefthook-local.yml", or when Claude is writing or modifying a
  lefthook.yml configuration file. Also triggers when the user mentions
  "git hook guardrails", "enforce lint on commit", "run tests before push",
  "auto-format on commit", or discusses setting up automated code quality
  checks tied to git operations.
---

# Lefthook Configuration Reference

Lefthook is a fast, polyglot Git hooks manager written in Go. Single binary, no dependencies. Use it to enforce code quality guardrails (lint, format, test) on git operations.

For tool-specific hook recipes, see `references/hook-recipes.md`.
For advanced configuration patterns, see `references/advanced-patterns.md`.

## Installation

```bash
brew install lefthook        # macOS
npm install lefthook -D      # Node.js (also yarn, pnpm, bun)
gem install lefthook         # Ruby
pipx install lefthook        # Python
go install github.com/evilmartians/lefthook/v2@latest  # Go
```

After install: `lefthook install` in the repo root to activate hooks.

## Config File

Primary: `lefthook.yml` (also supports `.lefthook.yml`, `lefthook.toml`, `lefthook.json`, or under `.config/`).

Local overrides: `lefthook-local.yml` — merged on top, never committed. Add to `.gitignore`.

## Top-Level Options

```yaml
min_version: 1.0.0           # Minimum lefthook version required
source_dir: ".lefthook"      # Directory for script files (default: .lefthook)
source_dir_local: ".lefthook-local"  # Local scripts directory
rc: "~/.bashrc"              # Shell rc file to source before commands
no_tty: false                # Disable TTY allocation
colors: true                 # Enable colored output
skip_lfs: false              # Skip LFS hooks
assert_lefthook_installed: true  # Fail if lefthook not installed
no_auto_install: false       # Don't auto-install on git init

output:                      # Control what lefthook prints
  - meta                     # Show hook name and version
  - summary                  # Show pass/fail summary
  - empty_summary            # Show summary even when nothing ran
  - success                  # Show successful job output
  - failure                  # Show failed job output
  - execution                # Show execution details
  - execution_out            # Show command stdout
  - execution_info           # Show file list info
  - skips                    # Show skipped jobs
```

## Hook Types

Any valid git hook name works. Common ones:

| Hook | When it runs | Typical use |
|------|-------------|-------------|
| `pre-commit` | Before commit is created | Lint, format staged files |
| `commit-msg` | After commit message entered | Validate message format |
| `pre-push` | Before push to remote | Run tests, build |
| `post-checkout` | After branch switch | Install deps, rebuild |
| `post-merge` | After merge completes | Install deps |
| `prepare-commit-msg` | Before editor opens | Template commit messages |

Custom groups (not tied to git events) can be defined and run manually with `lefthook run <name>`.

## Hook-Level Options

```yaml
pre-commit:
  parallel: true             # Run all jobs simultaneously (default: false)
  piped: true                # Run jobs sequentially, stop on failure (mutually exclusive with parallel)
  follow: true               # Like piped but continue on failure (mutually exclusive with parallel/piped)
  skip: true                 # Skip this entire hook
  only:                      # Only run in specific conditions
    - ref: main              # Only on specific branch
  exclude_tags: [slow]       # Exclude jobs with these tags
  files: "git diff --name-only HEAD"  # Custom file list for all jobs
  fail_on_changes: true      # Fail if working tree changes after hook
  fail_on_changes_diff: "git diff"  # Custom diff command for above
  jobs: [...]                # List of jobs to run
```

## Job Options

```yaml
jobs:
  - name: eslint                        # Required: job name
    run: npx eslint {staged_files}      # Command to execute
    glob: "*.{js,ts,jsx,tsx}"           # Filter files by pattern
    exclude: "vendor/**"                # Exclude files matching pattern
    files: "git diff --name-only"       # Custom file source command
    file_types: [text]                  # Filter by file type
    tags: [frontend, lint]              # Tags for grouping/filtering
    root: "frontend/"                   # Run from subdirectory
    env:                                # Environment variables
      NODE_ENV: test
    stage_fixed: true                   # Re-stage files after command (for auto-fix)
    interactive: true                   # Allocate TTY for interactive commands
    use_stdin: true                     # Pass file list via stdin
    priority: 1                         # Execution order (lower = first, with piped)
    fail_text: "ESLint found errors"    # Custom failure message
    skip:                               # Skip conditions
      - merge                           # Skip during merges
      - rebase                          # Skip during rebases
      - ref: main                       # Skip on branch
    only:
      - ref: "feature/*"               # Only on matching branches
```

## File Placeholders

Use in `run` commands — lefthook substitutes them with actual file lists:

| Placeholder | Resolves to |
|-------------|-------------|
| `{staged_files}` | Files in git staging area (most common for pre-commit) |
| `{push_files}` | Files changed between HEAD and remote (for pre-push) |
| `{all_files}` | All tracked files in repo |
| `{files}` | Files from custom `files` command |
| `{1}` | First argument (e.g., commit message file path for commit-msg) |

## Script Support

Instead of inline `run` commands, use script files:

```yaml
pre-commit:
  jobs:
    - script: "check-large-files.sh"
      runner: bash
```

Scripts live in `source_dir` (default `.lefthook/`):
```
.lefthook/
  pre-commit/
    check-large-files.sh
```

## Key Patterns

### Auto-fix and re-stage
Use `stage_fixed: true` with formatters so fixed files get staged automatically:
```yaml
- name: prettier
  run: npx prettier --write {staged_files}
  glob: "*.{js,ts,css,json,md}"
  stage_fixed: true
```

### Parallel for speed
Run independent linters simultaneously:
```yaml
pre-commit:
  parallel: true
  jobs:
    - name: eslint
      run: npx eslint {staged_files}
      glob: "*.{js,ts}"
    - name: stylelint
      run: npx stylelint {staged_files}
      glob: "*.{css,scss}"
```

### Monorepo with root
Scope jobs to subdirectories:
```yaml
- name: lint-api
  root: "api/"
  run: bundle exec rubocop {staged_files}
  glob: "*.rb"
```

### Skip during rebase
Avoid running hooks during rebase operations:
```yaml
- name: tests
  run: npm test
  skip:
    - rebase
    - merge
```

### Disable temporarily
```bash
LEFTHOOK=0 git commit -m "skip hooks this once"
```

## CLI Commands

| Command | Purpose |
|---------|---------|
| `lefthook install` | Set up git hooks from config |
| `lefthook uninstall` | Remove lefthook git hooks |
| `lefthook run <hook>` | Run a hook manually |
| `lefthook validate` | Validate config syntax |
| `lefthook dump` | Show merged config (with remotes/extends) |
| `lefthook version` | Show version |
