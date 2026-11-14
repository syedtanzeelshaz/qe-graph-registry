"""
questengine.registry: Centralized GraphQL Schema Registry for Quest Engine.
"""
from importlib.resources import files
from pathlib import Path

__version__ = "1.0.1"

try:
    from questengine.registry.constants import GraphConstants
except ImportError:
    try:
        from .constants import GraphConstants  # type: ignore
    except ImportError:
        GraphConstants = None  # type: ignore


def get_supergraph_path() -> Path:
    """Return the absolute path to the bundled supergraph.graphql file."""
    try:
        pkg_files = files("questengine.registry")
        path = Path(str(pkg_files.joinpath("schema/supergraph.graphql")))
        if path.exists():
            return path
    except Exception:
        pass

    try:
        pkg_files = files("questengine.registry")
        path = Path(str(pkg_files.joinpath("supergraph/build/supergraph.graphql")))
        if path.exists():
            return path
    except Exception:
        pass

    # Fallback to repository root
    local_path = Path(__file__).resolve().parent.parent.parent / "supergraph" / "build" / "supergraph.graphql"
    return local_path


__all__ = [
    "GraphConstants",
    "get_supergraph_path",
    "__version__",
]
