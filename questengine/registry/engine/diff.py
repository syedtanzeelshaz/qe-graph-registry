"""
Breaking change detection for schema changes using graphql-core utilities.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from graphql import build_schema
from graphql.utilities import (
    BreakingChange,
    DangerousChange,
    find_breaking_changes,
    find_dangerous_changes,
)


def load_schema_from_git(git_ref: str, relative_file_path: str, repo_root: Path) -> str:
    """Read a file at a specific git ref (e.g. origin/main)."""
    cmd = ["git", "show", f"{git_ref}:{relative_file_path}"]
    result = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def detect_schema_diff(
    old_sdl: str,
    new_sdl: str,
) -> tuple[List[BreakingChange], List[DangerousChange]]:
    """Compare old vs new SDL and return breaking and dangerous changes."""
    old_schema = build_schema(old_sdl)
    new_schema = build_schema(new_sdl)

    breaking = find_breaking_changes(old_schema, new_schema)
    dangerous = find_dangerous_changes(old_schema, new_schema)

    return breaking, dangerous

