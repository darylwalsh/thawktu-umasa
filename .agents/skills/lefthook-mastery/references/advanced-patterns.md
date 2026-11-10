# Lefthook Advanced Patterns

## Monorepo Configuration

Use `root` to scope jobs to subdirectories. Each job only sees files within its root:

```yaml
pre-commit:
  parallel: true
  jobs:
    - name: lint-frontend
      root: "frontend/"
      run: npx eslint {staged_files}
      glob: "*.{js,ts,tsx}"

    - name: lint-backend
      root: "backend/"
      run: bundle exec rubocop {staged_files}
      glob: "*.rb"

    - name: lint-api
      root: "api/"
      run: golangci-lint run --new-from-rev=HEAD
      glob: "*.go"
```

## Job Groups

Nest jobs within a group for scoped parallel/piped execution:

```yaml
pre-commit:
  jobs:
    - group:
        name: frontend
        parallel: true
        jobs:
          - name: eslint
            run: npx eslint {staged_files}
            glob: "*.{js,ts}"
          - name: stylelint
            run: npx stylelint {staged_files}
            glob: "*.{css,scss}"
    - group:
        name: backend
        piped: true
        jobs:
          - name: rubocop
            run: bundle exec rubocop {staged_files}
            glob: "*.rb"
          - name: rspec
            run: bundle exec rspec --fail-fast
```

## Remote Configs

Pull lefthook config from a shared repo (org-wide standards):

```yaml
remotes:
  - git_url: https://github.com/org/lefthook-configs
    ref: main
    configs:
      - lefthook-common.yml
```

With refetch control:
```yaml
remotes:
  - git_url: https://github.com/org/lefthook-configs
    ref: main
    refetch: true
    refetch_frequency: "24h"
    configs:
      - base.yml
      - security.yml
```

### Plugin integration

If the user has configured a shared config via `/lefthook:setup`, it's stored in `.claude/lefthook.local.md`:

```yaml
---
remote_repo: "https://github.com/org/lefthook-config"
remote_ref: "main"
remote_configs: ["base.yml", "security.yml"]
refetch_frequency: "24h"
---
```

When generating `lefthook.yml`, include the `remotes:` block from these settings. The shared config provides org-wide baseline hooks; local jobs layer on top.

## Extends

Extend from local config files:

```yaml
extends:
  - .lefthook/base.yml
  - .lefthook/team-overrides.yml
```

## Conditional Execution

### Skip conditions

Skip a job during specific git operations:
```yaml
- name: tests
  run: npm test
  skip:
    - merge        # Skip during merge
    - rebase       # Skip during rebase
    - ref: main    # Skip on main branch
```

Skip the entire hook:
```yaml
pre-commit:
  skip:
    - merge
    - rebase
```

### Only conditions

Run a job only in specific conditions:
```yaml
- name: deploy-check
  run: ./scripts/validate-deploy.sh
  only:
    - ref: "release/*"    # Only on release branches
```

## Environment Variables

Set per-job environment:
```yaml
- name: test
  run: pytest
  env:
    DATABASE_URL: "sqlite:///test.db"
    DJANGO_SETTINGS_MODULE: "project.settings.test"
```

Global env via `rc`:
```yaml
rc: "~/.bashrc"    # Source this file before all commands
```

## Piped Execution

Run jobs sequentially — each waits for the previous to succeed:

```yaml
pre-push:
  piped: true
  jobs:
    - name: lint
      run: npm run lint
      priority: 1           # Runs first
    - name: type-check
      run: npx tsc --noEmit
      priority: 2           # Runs second
    - name: test
      run: npm test
      priority: 3           # Runs last
```

Use `follow: true` instead of `piped: true` to continue even if earlier jobs fail.

## Docker Integration

Run hooks inside containers:

```yaml
pre-commit:
  jobs:
    - name: rubocop-docker
      run: docker compose run --rm app bundle exec rubocop {staged_files}
      glob: "*.rb"
```

## Templates

Use YAML anchors to define reusable job fragments:

```yaml
.lint-defaults: &lint-defaults
  stage_fixed: true
  skip:
    - merge
    - rebase

pre-commit:
  parallel: true
  jobs:
    - name: eslint
      run: npx eslint --fix {staged_files}
      glob: "*.{js,ts}"
      <<: *lint-defaults
    - name: prettier
      run: npx prettier --write {staged_files}
      glob: "*.{js,ts,css,json,md}"
      <<: *lint-defaults
```

The anchor `&lint-defaults` defines the template, and `<<: *lint-defaults` merges it into each job.

## Output Configuration

Control verbosity:

```yaml
# Minimal — only show failures
output:
  - failure

# Verbose — show everything
output:
  - meta
  - summary
  - success
  - failure
  - execution
  - execution_out
  - execution_info
  - skips

# Balanced (recommended)
output:
  - meta
  - summary
  - failure
```

## Local Overrides

`lefthook-local.yml` merges on top of the main config. Use it for:

### Skip slow jobs locally
```yaml
pre-push:
  exclude_tags: [slow]
```

### Add personal jobs
```yaml
pre-commit:
  jobs:
    - name: my-custom-check
      run: ./my-script.sh
```

### Disable a hook entirely
```yaml
pre-push:
  skip: true
```

## Custom Manual Groups

Define groups that aren't tied to git events — run with `lefthook run <name>`:

```yaml
# Fix all files (not just staged)
fix:
  jobs:
    - name: eslint-fix
      run: npx eslint --fix {all_files}
      glob: "*.{js,ts}"
    - name: prettier-fix
      run: npx prettier --write {all_files}
      glob: "*.{js,ts,css,json,md}"

# Full audit
audit:
  jobs:
    - name: npm-audit
      run: npm audit
    - name: license-check
      run: npx license-checker --failOn "GPL"
```

Run: `lefthook run fix` or `lefthook run audit`

## Performance Tips

1. **Use `parallel: true`** for independent jobs (linters, formatters)
2. **Use `{staged_files}`** instead of `{all_files}` in pre-commit — only check what changed
3. **Use `glob`** to avoid passing irrelevant files to tools
4. **Use `--server` flag** for RuboCop (keeps daemon running)
5. **Move slow checks to pre-push** instead of pre-commit
6. **Use `skip: [rebase, merge]`** to avoid running during non-authoring operations
7. **Use `tags` + `exclude_tags`** in local config to skip slow jobs during rapid iteration

## Migration from Other Tools

### From husky
Replace `.husky/pre-commit` scripts with lefthook.yml jobs. Remove husky from package.json. Run `lefthook install`.

### From pre-commit (Python)
Map `.pre-commit-config.yaml` repos/hooks to lefthook.yml jobs. Each hook becomes a job with `run` and `glob`.

### From overcommit
Map `.overcommit.yml` hook definitions to lefthook.yml. Similar structure but different syntax.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Hook not running | Run `lefthook install` to reinstall |
| Wrong files passed | Check `glob` pattern, use `lefthook run <hook> --verbose` |
| Config not loading | Run `lefthook dump` to see merged config |
| Slow hooks | Move to pre-push, use parallel, narrow glob |
| Hooks run during rebase | Add `skip: [rebase]` to the job |
| Need to skip once | `LEFTHOOK=0 git commit ...` |
| Hook fails in CI | Set `LEFTHOOK=0` in CI env, or use `assert_lefthook_installed: false` |
