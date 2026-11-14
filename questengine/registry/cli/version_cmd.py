"""
Version command for graph-cli.
"""
from __future__ import annotations

import click

from questengine.registry.cli.utils import get_default_repo_root
from questengine.registry.engine.publisher import sync_versions


@click.command("version")
@click.argument("new_version")
def version_command(new_version: str) -> None:
    """Synchronize a new version string across pyproject.toml, package.json, and registry/__init__.py."""
    repo_root = get_default_repo_root()
    click.echo(f"🏷️ Updating version to {new_version}...")
    sync_versions(new_version, repo_root)
    click.echo("✅ Successfully synchronized versions in pyproject.toml and package.json")

