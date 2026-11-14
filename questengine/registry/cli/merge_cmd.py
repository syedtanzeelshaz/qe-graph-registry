"""
Merge command for graph-cli.
"""
from __future__ import annotations

import sys
from pathlib import Path

import click

from questengine.registry.cli.utils import get_default_repo_root
from questengine.registry.engine.merger import merge_subgraphs


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
    "--out-constants",
    type=click.Path(path_type=Path),
    default=None,
    help="Path for generated constants.py output.",
)
@click.option(
    "--out-types-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Path for generated types/ package output.",
)
def merge_command(
    subgraph_dir: Path | None,
    out_schema: Path | None,
    out_introspection: Path | None,
    out_constants: Path | None,
    out_types_dir: Path | None,
) -> None:
    """Merge domain subgraphs and common schemas into unified supergraph.graphql."""
    repo_root = get_default_repo_root()
    sub_dir = subgraph_dir or (repo_root / "subgraph")
    schema_dest = out_schema or (repo_root / "supergraph" / "build" / "supergraph.graphql")
    intro_dest = out_introspection or (repo_root / "supergraph" / "build" / "supergraph-api.json")
    constants_dest = out_constants or (repo_root / "supergraph" / "build" / "constants.py")
    types_dest = out_types_dir or (repo_root / "supergraph" / "build" / "types")

    click.echo(f"🔄 Merging subgraphs from: {sub_dir}")
    try:
        merge_subgraphs(
            subgraph_dir=sub_dir,
            output_schema_path=schema_dest,
            output_introspection_path=intro_dest,
            output_constants_path=constants_dest,
            output_types_dir=types_dest,
        )
        click.echo(f"✅ Generated unified schema: {schema_dest}")
        click.echo(f"✅ Generated introspection JSON: {intro_dest}")
        click.echo(f"✅ Generated GraphConstants: {constants_dest}")
        click.echo(f"✅ Generated Python types: {types_dest}")
    except Exception as exc:
        click.secho(f"❌ Failed to merge subgraphs: {exc}", fg="red", err=True)
        sys.exit(1)
