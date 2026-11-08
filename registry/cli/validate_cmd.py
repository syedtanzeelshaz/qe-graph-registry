"""
Validate command for graph-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from registry.cli.utils import get_default_repo_root
from registry.engine.validator import validate_unified_schema


@click.command("validate")
@click.option(
    "--subgraph-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Path to subgraph directory (defaults to <repo_root>/subgraph).",
)
def validate_command(subgraph_dir: Path | None) -> None:
    """Validate syntax and consistency across all subgraphs."""
    repo_root = get_default_repo_root()
    sub_dir = subgraph_dir or (repo_root / "subgraph")

    click.echo(f"🔍 Validating subgraphs in: {sub_dir}")
    errors = validate_unified_schema(sub_dir)
    if errors:
        click.secho(f"❌ Schema validation failed with {len(errors)} error(s):", fg="red", err=True)
        for err in errors:
            click.echo(f"  • {err}", err=True)
        sys.exit(1)

    click.secho("✅ All subgraphs are syntactically and structurally valid!", fg="green")

