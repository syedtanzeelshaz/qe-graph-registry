"""
Schema Engine module: AST merging, validation, diffing, and version synchronization.
"""
from registry.engine.diff import detect_schema_diff, load_schema_from_git
from registry.engine.merger import merge_subgraphs
from registry.engine.publisher import sync_versions
from registry.engine.validator import validate_individual_files, validate_unified_schema

__all__ = [
    "detect_schema_diff",
    "load_schema_from_git",
    "merge_subgraphs",
    "sync_versions",
    "validate_individual_files",
    "validate_unified_schema",
]

