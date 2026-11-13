"""
qe-graph-registry: Centralized GraphQL Schema Registry for Quest Engine.
"""
from importlib.resources import files
from pathlib import Path

__version__ = "1.0.1"


def get_supergraph_path() -> Path:
    """Return the absolute path to the bundled supergraph.graphql file."""
    try:
        pkg_files = files("registry")
        path = Path(str(pkg_files.joinpath("supergraph/build/supergraph.graphql")))
        if path.exists():
            return path
    except Exception:
        pass

    # Fallback to repository root
    local_path = Path(__file__).resolve().parent.parent / "supergraph" / "build" / "supergraph.graphql"
    return local_path


def get_enums_path() -> Path:
    """Return the absolute path to the generated enums.py file."""
    try:
        pkg_files = files("registry")
        path = Path(str(pkg_files.joinpath("enums.py")))
        if path.exists():
            return path
    except Exception:
        pass

    local_path = Path(__file__).resolve().parent.parent / "supergraph" / "build" / "enums.py"
    return local_path

