"""
Artifact publisher and version synchronization helper.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from questengine.registry.engine.utils import get_default_repo_root
from questengine.registry.engine.merger import merge_subgraphs


def get_current_version(repo_root: Path) -> str:
    """Read the current version from questengine/registry/__init__.py or pyproject.toml."""
    init_path = repo_root / "questengine" / "registry" / "__init__.py"
    if init_path.exists():
        match = re.search(r'__version__\s*=\s*"([^"]+)"', init_path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)

    pyproject_path = repo_root / "pyproject.toml"
    if pyproject_path.exists():
        match = re.search(r'version\s*=\s*"([^"]+)"', pyproject_path.read_text(encoding="utf-8"))
        if match:
            return match.group(1)

    return "0.1.0"


def sync_versions(new_version: str, repo_root: Path) -> None:
    """Sync version across pyproject.toml, package.json, and __init__.py files."""
    pyproject_path = repo_root / "pyproject.toml"
    package_json_path = repo_root / "package.json"
    init_path = repo_root / "questengine" / "registry" / "__init__.py"

    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        updated = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content, count=1)
        pyproject_path.write_text(updated, encoding="utf-8")

    if package_json_path.exists():
        try:
            data = json.loads(package_json_path.read_text(encoding="utf-8"))
            data["version"] = new_version
            package_json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except Exception:
            pass

    if init_path.exists():
        content = init_path.read_text(encoding="utf-8")
        updated = re.sub(r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content, count=1)
        init_path.write_text(updated, encoding="utf-8")


def publish_to_local_store(
    version: str | None = None,
    dest_dir: Path | None = None,
    repo_root: Path | None = None,
) -> Path:
    """
    Build wheel and copy it to the local wheel repository (~/.qe/wheels by default).
    Similar to Gradle's publishToMavenLocal pattern.
    """
    if repo_root is None:
        repo_root = get_default_repo_root()

    target_version = version or get_current_version(repo_root)

    # 1. Sync version across files if an explicit version was passed
    if version:
        sync_versions(target_version, repo_root)

    # 2. Merge subgraphs to ensure supergraph.graphql, supergraph-api.json, constants.py, and types/ are fresh
    sub_dir = repo_root / "subgraph"
    schema_dest = repo_root / "supergraph" / "build" / "supergraph.graphql"
    intro_dest = repo_root / "supergraph" / "build" / "supergraph-api.json"
    constants_dest = repo_root / "supergraph" / "build" / "constants.py"
    types_dest = repo_root / "supergraph" / "build" / "types"
    schema_dest.parent.mkdir(parents=True, exist_ok=True)
    merge_subgraphs(
        subgraph_dir=sub_dir,
        output_schema_path=schema_dest,
        output_introspection_path=intro_dest,
        output_constants_path=constants_dest,
        output_types_dir=types_dest,
    )

    # 3. Destination folder
    if dest_dir is None:
        dest_dir = Path.home() / ".qe" / "wheels"
    dest_dir = dest_dir.expanduser().resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 4. Clean dist directory in repo_root before build to avoid copying old wheels
    dist_dir = repo_root / "dist"
    if dist_dir.exists():
        for old_whl in dist_dir.glob("*.whl"):
            try:
                old_whl.unlink()
            except OSError:
                pass

    # 5. Build wheel via uv build --wheel
    build_cmd = ["uv", "build", "--wheel"]
    res = subprocess.run(build_cmd, cwd=repo_root, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Build failed with code {res.returncode}:\n{res.stderr}\n{res.stdout}")

    # 6. Locate generated wheel in dist/
    wheels = list(dist_dir.glob(f"qe_graph_registry-{target_version}*.whl"))
    if not wheels:
        wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        raise FileNotFoundError(f"No wheel found in {dist_dir} after build.")

    latest_wheel = sorted(wheels, key=lambda p: p.stat().st_mtime, reverse=True)[0]

    # 7. Copy to destination directory
    dest_wheel = dest_dir / latest_wheel.name
    shutil.copy2(latest_wheel, dest_wheel)

    return dest_wheel
