"""
Diff command for graph-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from questengine.registry.cli.utils import get_default_repo_root
from questengine.registry.engine.diff import detect_schema_diff, load_schema_from_git


@click.command("diff")
@click.option(
    "--base",
    default="origin/main",
    show_default=True,
    help="Git reference to compare against (e.g. origin/main, HEAD~1).",
)
@click.option(
    "--schema-file",
    default="supergraph/build/supergraph.graphql",
    show_default=True,
    help="Relative path to the supergraph SDL inside the repo.",
)
def diff_command(base: str, schema_file: str) -> None:
    """Detect breaking and dangerous changes against a Git ref."""
    repo_root = get_default_repo_root()
    current_schema_path = repo_root / schema_file

    if not current_schema_path.exists():
        click.secho(f"❌ Current schema not found at {current_schema_path}. Run 'merge' first.", fg="red", err=True)
        sys.exit(1)

    try:
        old_sdl = load_schema_from_git(base, schema_file, repo_root)
    except Exception as exc:
        click.secho(f"⚠️ Could not load base schema from '{base}:{schema_file}': {exc}", fg="yellow")
        click.echo("Assuming initial release or new branch. Skipping diff.")
        sys.exit(0)

    new_sdl = current_schema_path.read_text(encoding="utf-8")
    try:
        breaking, dangerous = detect_schema_diff(old_sdl, new_sdl)
    except Exception as exc:
        click.secho(f"❌ Schema diff failed: {exc}", fg="red", err=True)
        sys.exit(1)

    if dangerous:
        click.secho(f"⚠️ Found {len(dangerous)} dangerous change(s):", fg="yellow")
        for item in dangerous:
            click.echo(f"  • {item.description}")

    if breaking:
        click.secho(f"❌ Found {len(breaking)} BREAKING change(s):", fg="red", err=True)
        for item in breaking:
            click.echo(f"  • {item.description}", err=True)
        sys.exit(1)

    click.secho("✅ No breaking changes detected!", fg="green")

