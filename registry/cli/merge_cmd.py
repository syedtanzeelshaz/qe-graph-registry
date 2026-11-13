"""
Merge command for graph-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from registry.cli.utils import get_default_repo_root
from registry.engine.merger import merge_subgraphs


@click.command("merge")
@click.option(
    "--subgraph-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Path to subgraph directory (defaults to <repo_root>/subgraph).",
)
@click.option(
    "--out-schema",
    type=click.Path(path_type=Path),
    default=None,
    help="Path for generated supergraph.graphql output.",
)
@click.option(
    "--out-introspection",
    type=click.Path(path_type=Path),
    default=None,
    help="Path for generated supergraph-api.json output.",
)
@click.option(
    "--out-enums",
    type=click.Path(path_type=Path),
    default=None,
    help="Path for generated supergraph/build/enums.py output.",
)
def merge_command(
    subgraph_dir: Path | None,
    out_schema: Path | None,
    out_introspection: Path | None,
    out_enums: Path | None,
) -> None:
    """Merge domain subgraphs and common schemas into unified supergraph.graphql."""
    repo_root = get_default_repo_root()
    sub_dir = subgraph_dir or (repo_root / "subgraph")
    schema_dest = out_schema or (repo_root / "supergraph" / "build" / "supergraph.graphql")
    intro_dest = out_introspection or (repo_root / "supergraph" / "build" / "supergraph-api.json")
    enums_dest = out_enums or (repo_root / "supergraph" / "build" / "enums.py")

    click.echo(f"🔄 Merging subgraphs from: {sub_dir}")
    try:
        merge_subgraphs(sub_dir, schema_dest, intro_dest, enums_dest)
        click.echo(f"✅ Generated unified schema: {schema_dest}")
        click.echo(f"✅ Generated introspection JSON: {intro_dest}")
        click.echo(f"✅ Generated Python enums: {enums_dest}")
    except Exception as exc:
        click.secho(f"❌ Failed to merge subgraphs: {exc}", fg="red", err=True)
        sys.exit(1)

