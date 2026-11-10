# Claude Agent SDK API Surface

This reference summarizes the programmatic Claude Agent SDK surface used by the
plugin.

## Packages

| Language              | Package                          | Baseline runtime |
| --------------------- | -------------------------------- | ---------------- |
| TypeScript/JavaScript | `@anthropic-ai/claude-agent-sdk` | Node.js 18+      |
| Python                | `claude-agent-sdk`               | Python 3.10+     |

The Agent SDK enables applications to build agents with Claude Code
capabilities: codebase understanding, file edits, command execution, tool use,
and multi-step workflows.

## Primary APIs

Use `query()` for simple workflows:

- send a prompt.
- receive an async stream/iterator of SDK messages.
- configure options.
- finish when the query result completes.

Use `ClaudeSDKClient` for interactive workflows:

- bidirectional conversation.
- repeated prompts in one session.
- custom in-process tools.
- hooks.
- MCP status/control.
- session-level lifecycle.

## Python Exports

Common Python exports include:

- `query`
- `ClaudeAgentOptions`
- `ClaudeSDKClient`
- message types such as `AssistantMessage`, `UserMessage`, `SystemMessage`,
  `ResultMessage`.
- block types such as `TextBlock`, `ToolUseBlock`, `ToolResultBlock`.
- `tool`
- `create_sdk_mcp_server`
- `HookMatcher`
- error classes such as `ClaudeSDKError`, `CLINotFoundError`,
  `CLIConnectionError`, `ProcessError`, and `CLIJSONDecodeError`.
- session store helpers such as `InMemorySessionStore` where available.

## TypeScript Exports

The TypeScript package exposes equivalent query/session concepts. Exact helper
names and option casing should be checked against installed local types because
the Agent SDK evolves. Common concepts include:

- `query`.
- options for prompt, max turns, cwd, tools, permissions, MCP servers, hooks,
  sessions, sandbox, and session stores.
- SDK message unions.
- session store interfaces and in-memory/reference implementations.
- helper functions for custom tools/MCP servers where supported.

## Query Flow

General query flow:

```text
configure options
start query
for each SDK message:
    process assistant text, tool use, tool result, system/status, or result
finish on result message or stream completion
handle errors and cleanup
```

Use `max_turns`/`maxTurns` for untrusted prompts and hosted products.

## ClaudeAgentOptions Concepts

Important option concepts:

- `system_prompt` / `systemPrompt`: agent system instructions.
- `append_system_prompt` / `appendSystemPrompt`: additive system instructions.
- `max_turns` / `maxTurns`: maximum agent turns.
- `cwd`: working directory for the session.
- `allowed_tools` / `allowedTools`: tools auto-approved for use.
- `disallowed_tools` / `disallowedTools`: tools blocked from use.
- `permission_mode` / `permissionMode`: broad permission behavior.
- `can_use_tool` / `canUseTool`: application callback for tool permission.
- `mcp_servers` / `mcpServers`: MCP server configuration.
- `hooks`: deterministic hook callbacks.
- `resume`: resume a session.
- `continue_conversation`: continue recent conversation where supported.
- `fork_session`: fork instead of continuing previous session where supported.
- `session_store` / `sessionStore`: mirror/load transcripts.
- `sandbox`: shell/file sandbox settings where supported.
- `settings`/setting sources/plugins: optional Claude Code settings/plugin
  integration where supported.

Always confirm exact names in local types before editing.

## Built-In Tools

Agent SDK workflows can expose Claude Code tools such as:

- Read.
- Write.
- Edit.
- Bash.
- Glob.
- Grep.
- other tools available in the runtime.

Important distinction:

- `allowed_tools`/`allowedTools` auto-approves listed tools.
- `disallowed_tools`/`disallowedTools` blocks tools.
- a strict built-in `tools` option, where supported by the installed SDK,
  controls which built-in tools are visible.

Do not use auto-approval as the only security boundary.

## Custom Tools

Custom tools can be exposed through in-process SDK MCP servers or external MCP
servers.

Python in-process tools:

- define a function with `@tool`.
- create a server with `create_sdk_mcp_server`.
- pass it through `mcp_servers`.
- auto-approve with the generated MCP tool name only when policy allows.

TypeScript custom tools should follow installed SDK helper APIs and local
examples.

## Hooks

Hooks are deterministic application callbacks invoked by the Claude Code
application, not by the model as a model-chosen tool. Hooks can inspect or block
events such as tool use.

Use hooks for:

- blocking dangerous shell commands.
- enforcing file path policy.
- adding deterministic feedback.
- auditing tool calls.
- validating inputs before a tool runs.

Keep hooks deterministic and side-effect-light.

## Sessions and Session Stores

Agent SDK sessions can be resumed, continued, forked, and mirrored to external
storage where supported.

Session stores require:

- tenant/project scoping.
- append behavior.
- load behavior.
- optional listing/subkey behavior for advanced resume.
- retention and deletion policy.
- validation for resume IDs.

Use built-in conformance tests or local testing helpers when the SDK provides
them.

## Error Classes

Python error categories include:

- `ClaudeSDKError`: base SDK error.
- `CLINotFoundError`: CLI missing or unavailable.
- `CLIConnectionError`: communication issue.
- `ProcessError`: subprocess exited with failure.
- `CLIJSONDecodeError`: response parsing failure.

TypeScript code should catch package-specific errors or generic process/stream
errors according to installed local types.

## Agent SDK vs Client SDK Beta Sessions

Do not confuse:

- Claude Agent SDK sessions for programmatic Claude Code agents.
- Client SDK beta sessions exposed under `client.beta`.

They solve different problems and use different packages.
