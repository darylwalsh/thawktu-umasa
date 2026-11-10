# Claude Agent SDK Python

Use this reference for the `claude-agent-sdk` Python package. The SDK targets
Python 3.10+ and bundles the Claude Code CLI by default.

## Installation

Use the repository's package manager:

```sh
pip install claude-agent-sdk
```

The package bundles Claude Code CLI. Use a custom CLI path only when the
repository explicitly needs a system-wide or pinned CLI:

```python
options = ClaudeAgentOptions(cli_path="/path/to/claude")
```

## Simple Query

```python
import anyio
from claude_agent_sdk import ClaudeAgentOptions, query

async def main() -> None:
    options = ClaudeAgentOptions(
        cwd="/path/to/project",
        max_turns=1,
        allowed_tools=["Read", "Glob", "Grep"],
        disallowed_tools=["Bash"],
    )

    async for message in query(
        prompt="Summarize this codebase.",
        options=options,
    ):
        print(message)

anyio.run(main)
```

`query()` is async and returns an async iterator of SDK messages.

## Message Types

Common message types include:

- `AssistantMessage`
- `UserMessage`
- `SystemMessage`
- `ResultMessage`

Common content blocks include:

- `TextBlock`
- `ToolUseBlock`
- `ToolResultBlock`

Extract assistant text by checking message/block types, not by string casting.

## Options

Important `ClaudeAgentOptions` fields include:

- `system_prompt`
- `max_turns`
- `cwd`
- `allowed_tools`
- `disallowed_tools`
- `permission_mode`
- `mcp_servers`
- `hooks`
- `can_use_tool`
- `resume`
- `fork_session`
- `session_store`
- `session_store_flush`
- `sandbox`
- `cli_path`

Use local type definitions for the complete current list.

## Tool Permissions

By default, Claude can have access to the full Claude Code toolset. In Python
Agent SDK:

- `allowed_tools` auto-approves listed tools.
- unlisted tools fall through to `permission_mode` and `can_use_tool`.
- `allowed_tools` does not remove tools from the toolset.
- `disallowed_tools` blocks specific tools.

This distinction is critical for security review.

## Working Directory

Set `cwd` for workspace tasks:

```python
from pathlib import Path

options = ClaudeAgentOptions(cwd=Path("/path/to/project"))
```

Do not rely on process current directory in services that handle multiple
projects.

## ClaudeSDKClient

Use `ClaudeSDKClient` for bidirectional interactive workflows:

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(cwd="/path/to/project", max_turns=3)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Inspect the tests.")
    async for message in client.receive_response():
        print(message)
```

Use this for custom tools, hooks, repeated prompts, and session-level control.

## Custom Tools

Define in-process SDK MCP tools with `@tool`:

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, create_sdk_mcp_server, tool

@tool("greet", "Greet a user", {"name": str})
async def greet_user(args):
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}

server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[greet_user],
)

options = ClaudeAgentOptions(
    mcp_servers={"tools": server},
    allowed_tools=["mcp__tools__greet"],
)
```

Benefits of in-process SDK MCP tools:

- no subprocess management.
- lower IPC overhead.
- simpler deployment.
- easier debugging.
- direct Python type hints.

## Hooks

Hooks are Python callbacks invoked by the Claude Code application at specific
events.

Example policy:

```python
from claude_agent_sdk import ClaudeAgentOptions, HookMatcher

async def block_unsafe_bash(input_data, tool_use_id, context):
    if input_data.get("tool_name") != "Bash":
        return {}
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "Refusing destructive command",
            }
        }
    return {}

options = ClaudeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_unsafe_bash])]},
)
```

Keep hooks deterministic and fast.

## Error Handling

Common errors:

- `ClaudeSDKError`
- `CLINotFoundError`
- `CLIConnectionError`
- `ProcessError`
- `CLIJSONDecodeError`

Pattern:

```python
from claude_agent_sdk import CLINotFoundError, CLIJSONDecodeError, ProcessError

try:
    async for message in query(prompt="Hello", options=options):
        pass
except CLINotFoundError:
    raise RuntimeError("Claude Code CLI is unavailable")
except ProcessError as exc:
    raise RuntimeError(f"Agent process failed with exit code {exc.exit_code}")
except CLIJSONDecodeError as exc:
    raise RuntimeError("Agent stream could not be parsed") from exc
```

Do not expose raw transcripts in exceptions.

## Session Stores

Use session stores for transcript mirroring and resume.

Review:

- key scoping.
- append/load implementation.
- timeout.
- deletion.
- resume validation.
- tenant isolation.
- conformance tests where available.

## Sandboxing

Sandbox settings can restrict bash command behavior on supported platforms.

Review:

- `enabled`.
- `autoAllowBashIfSandboxed`.
- excluded commands.
- network policy.
- whether unsandboxed commands are allowed.
- fallback if sandbox is unavailable.

Hosted products should fail closed when sandboxing is required.
