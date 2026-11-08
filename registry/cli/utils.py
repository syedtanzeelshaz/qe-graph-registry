"""
Common CLI utilities and path resolvers.
"""
from pathlib import Path


def get_default_repo_root() -> Path:
    """Return the repository root directory."""
    return Path(__file__).resolve().parent.parent.parent

