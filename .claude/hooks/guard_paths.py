"""Block direct file-tool edits to generated and human-owned paths.

TERMINATION: one denial per tool invocation; no retries or stateful loop.
Bash writes are outside this guard's scope (decision D26 / Q21).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from hook_input import edited_paths

RULES = {
    "uv.lock": "generated lockfile; regenerate with `uv lock`",
    "CHANGELOG.md": "generated changelog; regenerate with `mise run bump -- --dry-run` (release workflow in task 05)",
    "tooling/watchlist.toml": "human-only watchlist; propose the change in an issue",
    "fnox.toml": "human-owned secrets configuration; ask the owner to use `fnox set`",
}


def denial(path: Path, root: Path) -> str | None:
    """Explain a protected path or tracked test denial, including symlink aliases."""
    # Resolve the original path before discarding '..' across a directory symlink.
    for candidate in dict.fromkeys((Path(os.path.abspath(path)), path.resolve())):
        if not candidate.is_relative_to(root):
            continue
        relative = candidate.relative_to(root)
        name = relative.as_posix()
        reason = RULES.get(name)
        if relative.parent == Path(".github/workflows") and name.endswith(".lock.yml"):
            reason = "generated workflow; regenerate with `gh aw compile`"
        if relative.parent == Path("reports/tooling-watch") and name.endswith(
            ".facts.json"
        ):
            reason = "generated facts; regenerate with the task 07 collector"
        if reason:
            return f"Blocked {name}: {reason}."
        if os.environ.get("STARTER_FIX_MODE") == "1" and relative.parts[:1] == (
            "tests",
        ):
            git = shutil.which("git")
            if git is None:
                raise OSError("git unavailable; cannot verify tracked tests")
            result = subprocess.run(  # noqa: S603  # Resolved git; path is a separate argv element.
                [git, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", name],
                cwd=root,
                capture_output=True,
                check=False,
                timeout=1,
            )
            if result.returncode:
                raise OSError("cannot verify tests against HEAD")
            if result.stdout:
                return f"Blocked {name}: fix mode protects tests tracked at HEAD; preserve the reproducing assertion and fix the implementation. New test files are allowed."
    return None


def main() -> int:
    """Consume a PreToolUse event; malformed inputs fail closed with exit 2."""
    root = Path(
        os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parents[2])
    ).resolve()
    try:
        for path in edited_paths(sys.stdin.read(), root):
            reason = denial(path, root)
            if reason:
                print(reason, file=sys.stderr)
                return 2
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(
            f"Blocked: cannot validate file-tool paths ({error}); correct the hook input or restore git before retrying.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
