"""
Publish-local command for graph-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from questengine.registry.cli.utils import get_default_repo_root
from questengine.registry.engine.publisher import get_current_version, publish_to_local_store


@click.command("publish-local")
@click.option(
    "--version",
    "-v",
    default=None,
    help="Version to stamp on the build (e.g. 0.1.1.dev0, 0.1.0-alpha.1). If omitted, uses current version.",
)
@click.option(
    "--dest",
    "-d",
    type=click.Path(path_type=Path),
    default=None,
    help="Target wheel directory (defaults to ~/.qe/wheels).",
)
def publish_local_command(version: str | None, dest: Path | None) -> None:
    """Build and publish wheel to local store (~/.qe/wheels) for local consumption."""
    repo_root = get_default_repo_root()
    click.echo(f"📦 Preparing local wheel build (version: {version or 'current'})...")
    try:
        wheel_path = publish_to_local_store(version=version, dest_dir=dest, repo_root=repo_root)
        current_v = version or get_current_version(repo_root)
        click.secho(f"✅ Published wheel: {wheel_path}", fg="green")
        click.echo("\nTo consume this in downstream Python projects (e.g. quest-engine-core):")
        click.echo("  1. In pyproject.toml, ensure:")
        click.echo("       [tool.uv]")
        click.echo('       find-links = ["~/.qe/wheels"]')
        click.echo(f'       dependencies = ["qe-graph-registry=={current_v}"]')
        click.echo("  2. Run:")
        click.echo("       uv sync --reinstall-package qe-graph-registry")
    except Exception as exc:
        click.secho(f"❌ Failed to publish local wheel: {exc}", fg="red", err=True)
        sys.exit(1)

