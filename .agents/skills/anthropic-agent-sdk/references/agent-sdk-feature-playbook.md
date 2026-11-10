# Claude Agent SDK Feature Playbook

Use this playbook to build or review programmatic agents with Claude Code
capabilities.

## Simple Query

Use `query()` when the app needs a single prompt and streamed messages.

Implementation steps:

1. Create options with `cwd`, `max_turns`, and permission settings.
2. Start `query()`.
3. Iterate SDK messages.
4. Extract assistant text by block type.
5. Handle result and error messages.
6. Cancel the stream when the caller disconnects.
7. Convert errors into app-level errors.

Use this for one-shot codebase summaries, simple local automations, and
deterministic internal workflows.

## Interactive Client

Use `ClaudeSDKClient` when the app needs:

- repeated prompts in one session.
- custom tools.
- hooks.
- bidirectional communication.
- MCP server status.
- session management.

Implementation steps:

1. Build `ClaudeAgentOptions`.
2. Open the client with an async context/lifecycle.
3. Send prompts with `client.query(...)`.
4. Receive responses with `receive_response()` or local equivalent.
5. Close client on request/job shutdown.
6. Test lifecycle cleanup.

## Built-In Tool Policy

Define policy before enabling tools:

- read-only inspection: allow/auto-approve `Read`, `Glob`, `Grep`.
- code editing: include `Edit`/`Write` only after user intent is clear.
- shell commands: treat `Bash` as high-risk; sandbox or approval is required
  for hosted products.
- destructive operations: block or require approval.

Implementation pattern:

```text
allowed_tools = small set for auto-approval
disallowed_tools = known blocked tools
permission_mode = product-approved behavior only
hooks = deterministic safety checks
cwd = intended workspace root
max_turns = bounded
```

## Permission Callbacks

Use permission callbacks when the app needs dynamic decisions:

- user/tenant policy.
- file path policy.
- command allow/deny logic.
- tool argument inspection.
- approval escalation.

Do not rely on permission callbacks for calls already permitted by broad
approval modes unless the local SDK docs/types guarantee callback order.
Prefer pre-tool hooks for deterministic blocking.

## Hooks

Use hooks for deterministic lifecycle behavior.

Common hook examples:

- block `Bash` commands matching forbidden patterns.
- block writes outside the workspace.
- record sanitized audit events.
- enforce max file size.
- reject network commands in offline mode.

Hook output should include a clear denial reason.

## Custom Tools

Use custom tools when the agent needs controlled access to application data or
actions.

Tool design rules:

- make tools narrow and named by action.
- validate every input.
- check authorization inside the tool.
- return bounded output.
- return structured errors for expected failures.
- avoid shelling out unless the whole tool is specifically a command runner and
  policy allows it.

## MCP Servers

Use MCP servers for external tools/services.

Review:

- server type and command/URL.
- environment variables and secrets.
- timeout and startup failure.
- tool naming and permissions.
- whether project-local MCP config is trusted.
- whether external network is allowed.

Prefer explicit MCP server config in hosted products rather than inheriting
untrusted project configuration.

## Sessions and Resume

Use resume when the app wants continuity. Use fork when the app wants to branch
from prior context without modifying the original session.

Rules:

- validate resume IDs.
- scope sessions by tenant and project.
- protect transcript stores from cross-tenant reads.
- define retention/deletion.
- handle missing/corrupt session data.
- test resume, fork, and deletion behavior.

## Session Stores

Use session stores when transcripts must be mirrored to Redis, Postgres, S3, or
another store.

Implementation steps:

1. Define project/session key strategy.
2. Implement append/load and optional list/delete operations.
3. Use conformance tests where available.
4. Add timeouts for store operations.
5. Handle append failures as operational errors.
6. Avoid storing secrets or raw customer data unless policy permits.

## Sandboxing

Use sandbox settings for shell/file execution where supported.

Sandbox policy should specify:

- whether sandbox is enabled.
- whether commands can bypass sandbox.
- excluded commands.
- network domains.
- filesystem access.
- fallback behavior when sandbox is unavailable.

For hosted products, fail closed when sandbox is required but unavailable.

## Agent Loop Limits

Always define limits for untrusted or production workflows:

- max turns.
- timeout.
- output size.
- tool call count.
- command runtime.
- file size.
- network policy.

Agent loops without limits are release blockers in hosted products.

## Migration from Claude Code SDK Naming

Older code may use Claude Code SDK naming. Modernize to Claude Agent SDK terms:

- package names use Claude Agent SDK.
- option names may have changed.
- older session APIs may be deprecated in favor of `query()` plus resume/session
  store options.
- Python uses `ClaudeAgentOptions` rather than older option names.

Check local package changelog/types before making broad migrations.
