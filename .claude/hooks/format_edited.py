"""Format edited Python; lint findings are advisory and never fail a session."""

import json
import os
import subprocess
import sys
from pathlib import Path

from hook_input import edited_paths


def main() -> int:
    """Apply safe lint fixes then formatting, reporting residual findings."""
    root = Path(
        os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2])
    ).resolve()
    messages: list[str] = []
    try:
        for path in edited_paths(sys.stdin.read(), root):
            resolved = path.resolve()
            if (
                resolved.suffix != ".py"
                or not resolved.is_file()
                or not resolved.is_relative_to(root)
            ):
                continue
            # Use the project's exact Ruff, not a global binary or a new environment.
            ruff = root / ".venv/bin/ruff"
            for args in (["check", "--fix"], ["format"]):
                result = subprocess.run(  # noqa: S603  # Fixed project binary; edited path is a separate argv element.
                    [str(ruff), *args, "--", str(resolved)],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=1,
                )
                if result.returncode:
                    messages.append(
                        f"Ruff {' '.join(args)}: {result.stdout}{result.stderr}"
                    )
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        messages.append(
            f"Python edit formatting unavailable: {error}; run `mise run fmt` and `mise run lint`."
        )
    if messages:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": "\n".join(messages),
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
