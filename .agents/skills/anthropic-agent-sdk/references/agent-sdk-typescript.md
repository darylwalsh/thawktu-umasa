# Claude Agent SDK TypeScript

Use this reference for `@anthropic-ai/claude-agent-sdk` in Node.js 18+
applications.

## Installation

Use the repository's package manager:

```sh
npm install @anthropic-ai/claude-agent-sdk
```

Use `pnpm add`, `yarn add`, or existing package manager equivalents when
appropriate.

## Import and Local Type Rule

The TypeScript Agent SDK evolves. Always inspect installed local types or
examples before relying on exact helper names or option casing.

Expected concepts:

- `query`.
- options object.
- SDK message stream.
- built-in tools/permissions.
- MCP server config.
- hooks.
- session stores.
- resume/session options.

## Query Pattern

Typical shape:

```ts
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Inspect this repository and summarize the test strategy.",
  options: {
    cwd: process.cwd(),
    maxTurns: 3,
    allowedTools: ["Read", "Glob", "Grep"],
    disallowedTools: ["Bash"],
  },
})) {
  console.log(message);
}
```

If local examples use a different function signature, follow the installed
package's types.

## Options Checklist

For every TypeScript Agent SDK workflow, configure or deliberately omit:

- `cwd`.
- `maxTurns`.
- `allowedTools`.
- `disallowedTools`.
- `permissionMode`.
- strict built-in `tools` option where available.
- `mcpServers`.
- hooks.
- `sessionStore`.
- `resume`.
- sandbox settings where available.

Do not leave broad defaults in hosted products.

## Built-In Tools

Tool policy should be explicit:

```ts
const options = {
  cwd: "/workspace/project",
  maxTurns: 3,
  allowedTools: ["Read", "Glob", "Grep"],
  disallowedTools: ["Bash", "Write", "Edit"],
};
```

Where the installed SDK supports a strict `tools` option, use it to define the
visible built-in tool set. Keep `allowedTools` for auto-approval and
`disallowedTools` for blocking.

## Session Stores

TypeScript examples include session store implementations for stores such as
Redis, Postgres, and S3.

Review session store implementations for:

- key design.
- append atomicity.
- load ordering.
- resume behavior.
- subagent/sidechain support.
- conformance tests.
- deletion.
- tenant scoping.
- timeouts.

Use `sessionStore` with `query({ options: { sessionStore } })` when the local
package supports it.

## Resume

Use resume options for continuing a prior session. Pair resume with session
store only when the store can materialize the transcript required by the
subprocess/session.

Validation:

- resume ID is validated.
- user has access to the session.
- session belongs to the same project/tenant.
- missing session produces a safe error.
- fork behavior is deliberate when branching.

## Custom Tools and MCP

Use installed SDK helpers for custom tools where available. If helpers are not
available, configure MCP servers explicitly and validate tool names.

For external MCP servers:

- avoid inheriting untrusted project config in hosted products.
- pass secrets through environment config only.
- set startup timeout where available.
- handle server failure as a recoverable app error.

## Hooks

Use hooks for deterministic enforcement. Review event names and callback shapes
against installed local types.

Common hook policy:

- block `Bash` patterns.
- block writes outside workspace.
- audit sanitized metadata.
- reject tool calls with missing required authorization.

## Error Handling

Handle:

- subprocess startup failure.
- stream parse errors.
- non-zero process exits.
- permission denials.
- MCP server startup failures.
- session store append/load failures.
- user cancellation.

Do not expose raw transcript content in error messages.

## Testing

TypeScript tests should mock:

- `query`.
- SDK messages.
- tool permission decisions.
- session store behavior.
- MCP startup failures.
- cancellation.

For live smoke tests, gate by environment variables and never run them by
default in CI without credentials and isolation.
