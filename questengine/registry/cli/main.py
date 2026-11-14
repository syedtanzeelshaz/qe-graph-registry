"""
Main entry point for graph-cli.
"""
from __future__ import annotations

import click

from questengine.registry import __version__
from questengine.registry.cli.diff_cmd import diff_command
from questengine.registry.cli.merge_cmd import merge_command
from questengine.registry.cli.publish_local_cmd import publish_local_command
from questengine.registry.cli.validate_cmd import validate_command
from questengine.registry.cli.version_cmd import version_command


@click.group()
@click.version_option(__version__, prog_name="graph-cli")
def cli() -> None:
    """QE Graph Registry CLI — schema management & composition toolkit."""
    pass


cli.add_command(merge_command)
cli.add_command(validate_command)
cli.add_command(diff_command)
cli.add_command(publish_local_command)
cli.add_command(version_command)


if __name__ == "__main__":
    cli()

