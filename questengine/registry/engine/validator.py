"""
Schema validation tools for qe-graph-registry.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

from graphql import (
    DocumentNode,
    GraphQLSyntaxError,
    build_ast_schema,
    concat_ast,
    parse,
    validate_schema,
)

from questengine.registry.engine.merger import collect_schema_files


def _has_definitions(content: str) -> bool:
    """Check if content contains non-comment, non-whitespace tokens."""
    clean = re.sub(r"#.*", "", content).strip()
    return len(clean) > 0


def validate_individual_files(subgraph_dir: Path) -> List[Tuple[Path, str]]:
    """Validate syntax of each .graphql file individually."""
    errors: List[Tuple[Path, str]] = []
    schema_files = collect_schema_files(subgraph_dir)

    for file_path in schema_files:
        content = file_path.read_text(encoding="utf-8")
        if not _has_definitions(content):
            continue
        try:
            parse(content)
        except GraphQLSyntaxError as exc:
            errors.append((file_path, str(exc)))

    return errors


def validate_unified_schema(subgraph_dir: Path) -> List[str]:
    """Validate full schema composition, type consistency, and unresolved references."""
    syntax_errors = validate_individual_files(subgraph_dir)
    if syntax_errors:
        return [f"Syntax error in {path}: {err}" for path, err in syntax_errors]

    schema_files = collect_schema_files(subgraph_dir)
    ast_docs: List[DocumentNode] = []
    for file_path in schema_files:
        content = file_path.read_text(encoding="utf-8")
        if not _has_definitions(content):
            continue
        ast_docs.append(parse(content))

    if not ast_docs:
        return ["No GraphQL definitions found in any subgraph."]

    merged_ast = concat_ast(ast_docs)

    try:
        schema = build_ast_schema(merged_ast, assume_valid=False)
    except Exception as exc:
        return [f"Schema build error: {exc}"]

    schema_errors = validate_schema(schema)
    return [str(err) for err in schema_errors]
