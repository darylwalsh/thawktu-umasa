# Lefthook Hook Recipes

Ready-to-use job configurations organized by language and purpose.

## JavaScript / TypeScript

### ESLint (lint)
```yaml
- name: eslint
  run: npx eslint {staged_files}
  glob: "*.{js,jsx,ts,tsx}"
```

### ESLint with auto-fix
```yaml
- name: eslint-fix
  run: npx eslint --fix {staged_files}
  glob: "*.{js,jsx,ts,tsx}"
  stage_fixed: true
```

### Prettier (format)
```yaml
- name: prettier
  run: npx prettier --write {staged_files}
  glob: "*.{js,jsx,ts,tsx,css,scss,less,json,md,yaml,yml,html}"
  stage_fixed: true
```

### Biome (lint + format)
```yaml
- name: biome
  run: npx biome check --write {staged_files}
  glob: "*.{js,jsx,ts,tsx,json,jsonc}"
  stage_fixed: true
```

### TypeScript type check
```yaml
- name: tsc
  run: npx tsc --noEmit
  glob: "*.{ts,tsx}"
```

### Jest tests (pre-push)
```yaml
- name: jest
  run: npx jest --bail --passWithNoTests
```

### Vitest tests (pre-push)
```yaml
- name: vitest
  run: npx vitest run
```

### commitlint (commit-msg)
```yaml
- name: commitlint
  run: npx commitlint --edit {1}
```

### npm audit
```yaml
- name: audit
  run: npm audit --audit-level=high
  tags: [security]
```

## Python

### Ruff (lint + fix)
```yaml
- name: ruff-check
  run: ruff check --fix {staged_files}
  glob: "*.py"
  stage_fixed: true
```

### Ruff (format)
```yaml
- name: ruff-format
  run: ruff format {staged_files}
  glob: "*.py"
  stage_fixed: true
```

### Black (format)
```yaml
- name: black
  run: black {staged_files}
  glob: "*.py"
  stage_fixed: true
```

### Flake8 (lint)
```yaml
- name: flake8
  run: flake8 {staged_files}
  glob: "*.py"
```

### mypy (type check)
```yaml
- name: mypy
  run: mypy {staged_files}
  glob: "*.py"
```

### pytest (pre-push)
```yaml
- name: pytest
  run: pytest -x --tb=short
```

## Ruby

### RuboCop (lint)
```yaml
- name: rubocop
  run: bundle exec rubocop --force-exclusion --server {staged_files}
  glob: "*.rb"
```

### RuboCop (auto-correct)
```yaml
- name: rubocop-fix
  run: bundle exec rubocop -A --force-exclusion --server {staged_files}
  glob: "*.rb"
  stage_fixed: true
```

### Standard Ruby
```yaml
- name: standardrb
  run: bundle exec standardrb --fix {staged_files}
  glob: "*.rb"
  stage_fixed: true
```

### RSpec (pre-push)
```yaml
- name: rspec
  run: bundle exec rspec --fail-fast
```

### Minitest (pre-push)
```yaml
- name: minitest
  run: bundle exec rails test
```

### ERB Lint
```yaml
- name: erb-lint
  run: bundle exec erblint {staged_files}
  glob: "*.erb"
```

### Brakeman (security)
```yaml
- name: brakeman
  run: bundle exec brakeman --no-pager -q
  tags: [security]
```

## Go

### golangci-lint
```yaml
- name: golangci-lint
  run: golangci-lint run --new-from-rev=HEAD
  glob: "*.go"
```

### gofmt
```yaml
- name: gofmt
  run: gofmt -w {staged_files}
  glob: "*.go"
  stage_fixed: true
```

### goimports
```yaml
- name: goimports
  run: goimports -w {staged_files}
  glob: "*.go"
  stage_fixed: true
```

### Go test (pre-push)
```yaml
- name: go-test
  run: go test ./...
```

### Go vet
```yaml
- name: go-vet
  run: go vet ./...
  glob: "*.go"
```

## Rust

### Clippy (lint)
```yaml
- name: clippy
  run: cargo clippy -- -D warnings
  glob: "*.rs"
```

### rustfmt (format)
```yaml
- name: rustfmt
  run: rustfmt {staged_files}
  glob: "*.rs"
  stage_fixed: true
```

### Cargo test (pre-push)
```yaml
- name: cargo-test
  run: cargo test
```

## Elixir

### mix format
```yaml
- name: mix-format
  run: mix format {staged_files}
  glob: "*.{ex,exs}"
  stage_fixed: true
```

### Credo (lint)
```yaml
- name: credo
  run: mix credo {staged_files}
  glob: "*.{ex,exs}"
```

### mix test (pre-push)
```yaml
- name: mix-test
  run: mix test
```

## PHP

### PHP CS Fixer
```yaml
- name: php-cs-fixer
  run: php-cs-fixer fix {staged_files}
  glob: "*.php"
  stage_fixed: true
```

### PHPStan
```yaml
- name: phpstan
  run: phpstan analyse {staged_files}
  glob: "*.php"
```

### PHPUnit (pre-push)
```yaml
- name: phpunit
  run: vendor/bin/phpunit
```

## Shell

### ShellCheck
```yaml
- name: shellcheck
  run: shellcheck {staged_files}
  glob: "*.{sh,bash,zsh}"
```

### shfmt
```yaml
- name: shfmt
  run: shfmt -w {staged_files}
  glob: "*.{sh,bash}"
  stage_fixed: true
```

## Cross-language

### Conventional commits (commit-msg)

Without commitlint:
```yaml
commit-msg:
  jobs:
    - name: conventional-commit
      run: >-
        grep -qE "^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?(!)?: .+" {1}
        || (echo "ERROR: Commit message must follow Conventional Commits format" && exit 1)
```

### Check for large files
```yaml
- name: no-large-files
  run: >-
    for f in {staged_files}; do
      size=$(wc -c < "$f");
      if [ "$size" -gt 1048576 ]; then
        echo "ERROR: $f is larger than 1MB ($size bytes)";
        exit 1;
      fi;
    done
  tags: [safety]
```

### Prevent debug markers
```yaml
- name: no-debug
  run: >-
    grep -rn "binding.pry\|debugger\|console.log\|import pdb\|breakpoint()" {staged_files}
    && echo "ERROR: Debug statements found" && exit 1
    || true
  tags: [safety]
```

### markdownlint
```yaml
- name: markdownlint
  run: npx markdownlint {staged_files}
  glob: "*.md"
```

### actionlint (GitHub Actions)
```yaml
- name: actionlint
  run: actionlint {staged_files}
  glob: ".github/workflows/*.{yml,yaml}"
```

### Secrets detection
```yaml
- name: detect-secrets
  run: >-
    grep -rn "AKIA\|sk-\|ghp_\|glpat-\|xoxb-\|-----BEGIN" {staged_files}
    && echo "ERROR: Possible secrets detected" && exit 1
    || true
  tags: [security]
```
