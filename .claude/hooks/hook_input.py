"""Decode file-tool hook events without third-party dependencies."""

import json
import os
from pathlib import Path
from typing import cast


def object_dict(value: object) -> dict[str, object]:
    """Narrow an untrusted JSON object for strict type checking."""
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return cast(dict[str, object], value)


def edited_paths(raw: str, root: Path) -> list[Path]:
    """Return absolute lexical paths, honoring the tool's working directory."""
    event = object_dict(json.loads(raw))
    tool_input = object_dict(event.get("tool_input"))
    cwd = event.get("cwd", str(root))
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError("cwd must be an absolute path")
    inputs = [tool_input]
    edits = tool_input.get("edits")
    if isinstance(edits, list):
        inputs.extend(object_dict(edit) for edit in cast(list[object], edits))
    paths: list[Path] = []
    for entry in inputs:
        path = entry.get("file_path", entry.get("notebook_path"))
        if isinstance(path, str) and path:
            absolute = Path(os.path.abspath(Path(cwd) / path))
            if absolute not in paths:
                paths.append(absolute)
    if not paths:
        raise ValueError("file tool input has no file_path or notebook_path")
    return paths
