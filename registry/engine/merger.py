"""
AST Schema Merger for domain subgraphs and common definitions.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

from graphql import (
    DocumentNode,
    build_ast_schema,
    concat_ast,
    execute_sync,
    parse,
    print_schema,
)
from graphql.utilities import get_introspection_query


def _has_definitions(content: str) -> bool:
    """Check if content contains non-comment, non-whitespace tokens."""
    clean = re.sub(r"#.*", "", content).strip()
    return len(clean) > 0


def collect_schema_files(subgraph_dir: Path) -> List[Path]:
    """Collect all .graphql files ensuring common/ is ordered first."""
    common_dir = subgraph_dir / "common"
    ordered_files: List[Path] = []

    # Priority order for common files
    if common_dir.exists():
        priority_names = ["root.graphql", "directives.graphql", "scalars.graphql", "enums.graphql", "input.graphql"]
        for name in priority_names:
            file_path = common_dir / name
            if file_path.exists():
                ordered_files.append(file_path)

        for other_file in sorted(common_dir.glob("*.graphql")):
            if other_file not in ordered_files:
                ordered_files.append(other_file)

    # Load all domain subgraphs in alphabetical order
    for domain_dir in sorted(subgraph_dir.iterdir()):
        if domain_dir.is_dir() and domain_dir.name != "common":
            for domain_file in sorted(domain_dir.glob("*.graphql")):
                ordered_files.append(domain_file)

    return ordered_files


def merge_subgraphs(
    subgraph_dir: Path,
    output_schema_path: Path,
    output_introspection_path: Path | None = None,
) -> str:
    """
    Merge common and domain subgraphs into a unified supergraph.graphql.
    Optionally generate supergraph-api.json introspection file.
    """
    schema_files = collect_schema_files(subgraph_dir)
    if not schema_files:
        raise ValueError(f"No .graphql files found in {subgraph_dir}")

    ast_documents: List[DocumentNode] = []
    for file_path in schema_files:
        content = file_path.read_text(encoding="utf-8")
        if _has_definitions(content):
            ast_documents.append(parse(content))

    if not ast_documents:
        raise ValueError("No valid GraphQL definitions found across any subgraph.")

    merged_ast = concat_ast(ast_documents)
    schema = build_ast_schema(merged_ast, assume_valid=False)

    rendered_sdl = print_schema(schema)

    output_schema_path.parent.mkdir(parents=True, exist_ok=True)
    output_schema_path.write_text(rendered_sdl, encoding="utf-8")

    if output_introspection_path:
        output_introspection_path.parent.mkdir(parents=True, exist_ok=True)
        intro_query = parse(get_introspection_query())
        intro_result = execute_sync(schema, intro_query)
        if intro_result.errors:
            raise RuntimeError(f"Introspection failed: {intro_result.errors}")
        output_introspection_path.write_text(
            json.dumps(intro_result.data, indent=2), encoding="utf-8"
        )

    return rendered_sdl
