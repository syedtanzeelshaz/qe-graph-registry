"""
Path and repository root utilities.
"""
from pathlib import Path


def get_default_repo_root() -> Path:
    """Return the repository root directory by locating pyproject.toml."""
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path(__file__).resolve().parents[3]
