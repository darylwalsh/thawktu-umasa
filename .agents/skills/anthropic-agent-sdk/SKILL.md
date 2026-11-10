---
name: anthropic-agent-sdk
description: This skill should be used when the user asks to implement, debug, migrate, validate, or review programmatic Claude Code agent workflows using @anthropic-ai/claude-agent-sdk in TypeScript/JavaScript or claude-agent-sdk in Python. Trigger on query(), ClaudeAgentOptions, ClaudeSDKClient, built-in tools, custom tools, MCP servers, hooks, sessions, session stores, resume, cwd, permissions, sandboxing, or workspace automation.
license: MIT
metadata:
  author: PT Kelana Tech Solutions
---

# Claude Agent SDK

## Purpose

Use this skill for programmatic agents built with the Claude Agent SDK. The
Agent SDK is appropriate when the application needs Claude Code-style
capabilities: understanding a codebase, editing files, running commands,
calling tools, applying permission policy, and executing multi-step workflows.

Use `@anthropic-ai/claude-agent-sdk` for TypeScript/JavaScript and
`claude-agent-sdk` for Python. Treat Node.js 18+ and Python 3.10+ as baseline
runtime requirements unless the repository already pins stricter versions.

## Required Workflow

1. Confirm development or validation mode from
   `../anthropic-sdk/references/agent-usage-modes.md`.
2. Inspect the app boundary:
   - CLI, worker, backend route, desktop process, hosted service, CI task, or
     local development tool.
   - Workspace root, permission policy, secrets strategy, and subprocess
     lifecycle.
3. Read:
   - `../anthropic-agent-sdk/references/agent-sdk-api-surface.md`
   - `../anthropic-agent-sdk/references/agent-sdk-feature-playbook.md`
   - the relevant language-specific Agent SDK reference.
   - `../anthropic-sdk-production-review/references/security-privacy.md`
4. Choose the API:
   - `query()` for a simple async stream of SDK messages.
   - `ClaudeSDKClient` for bidirectional interaction, repeated prompts, custom
     in-process tools, hooks, MCP status, or session-level controls.
5. Configure options explicitly:
   - `cwd` / `cwd` points at the intended project root.
   - `maxTurns` / `max_turns` prevents runaway loops.
   - `allowedTools` / `allowed_tools` auto-approves only intended tools.
   - `disallowedTools` / `disallowed_tools` blocks known-dangerous tools.
   - `permissionMode` / `permission_mode` matches app policy.
   - `mcpServers` / `mcp_servers` is explicit.
   - session store/resume/fork options are intentional.
6. Add tests for option construction, tool schema behavior, permission
   decisions, hook outputs, and error conversion.

## Permission Rules

Separate these controls:

- Tool availability: which built-in tools the agent can see/use, if the local
  Agent SDK version exposes a strict `tools` option.
- Auto-approval: `allowed_tools`/`allowedTools` pre-approves listed tools.
- Blocking: `disallowed_tools`/`disallowedTools`, hooks, permission callbacks,
  sandbox settings, and app-level approval policy prevent unsafe use.
- Working directory: `cwd` constrains the intended project root, but does not
  replace sandboxing or app authorization.
- Sandbox: restrict shell/file execution where available and document fallback
  behavior.

Do not treat auto-approval as a security boundary. Review the exact local SDK
types and the app's deployed runtime before relying on any option as a hard
block.

## Common Patterns

### Python simple query

```python
import anyio
from claude_agent_sdk import ClaudeAgentOptions, query

async def main() -> None:
    options = ClaudeAgentOptions(
        cwd="/path/to/project",
        max_turns=3,
        allowed_tools=["Read"],
        disallowed_tools=["Bash"],
    )

    async for message in query(
        prompt="Inspect the project structure and summarize the app.",
        options=options,
    ):
        print(message)

anyio.run(main)
```

### Python custom in-process tool

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server, tool

@tool("lookup_ticket", "Look up a support ticket", {"ticket_id": str})
async def lookup_ticket(args):
    return {"content": [{"type": "text", "text": f"Ticket {args['ticket_id']}"}]}

server = create_sdk_mcp_server(
    name="support",
    version="1.0.0",
    tools=[lookup_ticket],
)

options = ClaudeAgentOptions(
    mcp_servers={"support": server},
    allowed_tools=["mcp__support__lookup_ticket"],
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Read ticket INC-123 and summarize it.")
    async for message in client.receive_response():
        print(message)
```

### TypeScript shape

Use the TypeScript package for Node.js 18+ applications that need equivalent
programmatic agent workflows. Import `query` and options types from
`@anthropic-ai/claude-agent-sdk`; follow the installed package's local types for
exact option casing and helper names. Prefer `query({ prompt, options })` style
when the local package examples use object arguments, and mirror existing code
in the repository when present.

## Validation Checklist

For existing Agent SDK code, check:

- Runtime meets SDK minimum.
- `cwd` is deliberate and cannot point at an unintended workspace.
- `max_turns`/`maxTurns` exists for untrusted or long-running prompts.
- Built-in tool availability and auto-approval are not confused.
- `disallowed_tools`/`disallowedTools` blocks shell/file/destructive tools when
  the app policy requires blocking.
- Hooks return deterministic decisions and clear denial reasons.
- Custom tools validate inputs and avoid leaking secrets.
- MCP servers are explicitly configured and do not inherit unsafe project
  settings accidentally.
- Session stores have retention policy, tenant scoping, resume validation, and
  deletion/fork behavior.
- Streams/subprocesses are cancelled on request/job shutdown.
- Errors are converted without exposing sensitive transcript content.

## Additional Resources

- `../anthropic-agent-sdk/references/agent-sdk-api-surface.md`
- `../anthropic-agent-sdk/references/agent-sdk-feature-playbook.md`
- `../anthropic-agent-sdk/references/agent-sdk-typescript.md`
- `../anthropic-agent-sdk/references/agent-sdk-python.md`
- `../anthropic-sdk-production-review/references/security-privacy.md`
- `../anthropic-sdk-production-review/references/testing-patterns.md`
- `../anthropic-sdk-production-review/references/failure-modes.md`
- `../anthropic-sdk-production-review/references/production-checklist.md`
