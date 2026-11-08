# `qe-graph-registry`

> Centralized GraphQL schema registry and contract authority for Quest Engine.

---

## 1. Overview

`qe-graph-registry` is the single source of truth for all GraphQL Schema Definition Language (SDL) types, inputs, directives, queries, and mutations across Quest Engine.

It follows the **Federated Modular Monolith** architecture:
- Schema definitions are partitioned into **domain-driven subgraphs** (`common/`, `app-user/`, `organization/`, `audit/`, etc.).
- Cross-domain type relationships are explicitly declared using standard extension files (`extends.graphql`).
- A Python-native CLI tool (`graph-cli`) parses, validates, and merges domain subgraphs into a single consolidated `supergraph.graphql`.
- Dual distribution:
  - **Python Wheel**: Consumed by backend services (`quest-engine-core` / Ariadne).
  - **NPM Package** (`@quest-engine/graph-registry`): Consumed by frontend apps for typed code generation (GraphQL Code Generator / Apollo Client).

---

## 2. Directory Structure

```
qe-graph-registry/
├── pyproject.toml                     # Python package definition (uv build)
├── package.json                       # NPM package definition (frontend distribution)
├── README.md
│
├── subgraph/                          # Domain-driven subgraphs
│   ├── common/                        # Shared root operations, directives, scalars, enums, inputs
│   │   ├── root.graphql
│   │   ├── directives.graphql
│   │   ├── scalars.graphql
│   │   ├── enums.graphql
│   │   └── input.graphql
│   │
│   ├── app-user/                      # User & identity domain
│   │   ├── app-user.graphql
│   │   └── extends.graphql
│   │
│   └── organization/                  # Multi-tenant workspace domain
│       ├── organization.graphql
│       └── extends.graphql
│
├── supergraph/                        # Generated output artifacts
│   ├── supergraph-config.yml          # Apollo Rover composition manifest
│   └── build/
│       ├── supergraph.graphql         # Unified composed SDL
│       └── supergraph-api.json        # Introspection schema JSON
│
└── registry/                          # Python package and Schema Engine
    ├── __init__.py                    # Public API (get_supergraph_path, __version__)
    ├── cli/                           # CLI commands package
    │   ├── __init__.py
    │   ├── main.py                    # Entry point for `graph-cli`
    │   ├── merge_cmd.py               # `merge` command
    │   ├── validate_cmd.py            # `validate` command
    │   ├── diff_cmd.py                # `diff` command
    │   ├── publish_local_cmd.py       # `publish-local` command
    │   ├── version_cmd.py             # `version` command
    │   └── utils.py                   # Common CLI helpers & path resolvers
    └── engine/                        # Schema Engine core logic
        ├── __init__.py
        ├── merger.py                  # AST merger using graphql-core
        ├── validator.py               # Syntax and schema consistency validator
        ├── diff.py                    # Breaking change detection
        └── publisher.py               # Artifact builder & wheel publisher
```

---

## 3. Local Development & Setup

### Prerequisites
- Python >= 3.11
- [`uv`](https://docs.astral.sh/uv/) (Astral Python package manager)

### Installation
In the repository root:

```bash
uv sync
```

---

## 4. CLI Commands

All commands are runnable via `uv run graph-cli`:

### Validate Schema Syntax & Structure
Validates each `.graphql` file individually and verifies the full cross-domain type graph:
```bash
uv run graph-cli validate
```

### Merge Subgraphs into Supergraph
Concatenates and formats all subgraphs into `supergraph/build/supergraph.graphql` and generates `supergraph/build/supergraph-api.json`:
```bash
uv run graph-cli merge
```

### Breaking Change Detection
Detects breaking or dangerous changes against the target branch (e.g. `origin/main`):
```bash
uv run graph-cli diff --base origin/main
```

### Publish Wheel Locally (Python `mavenLocal()` pattern)
Builds the wheel and deposits it into `~/.qe/wheels/` so downstream backend services (like `quest-engine-core`) can resolve it via `find-links` without hardcoding local file paths:
```bash
# Publish with current version
uv run graph-cli publish-local

# Publish with custom / snapshot version via command-line argument
uv run graph-cli publish-local --version 0.1.1.dev0
```

### Synchronize Version
Syncs version across `pyproject.toml`, `package.json`, and `__init__.py`:
```bash
uv run graph-cli version 0.2.0
```

---

## 5. Architecture & Integration Guide
For the full architectural breakdown, CI/CD pipeline, CodeArtifact setup, and backend/frontend consumer configuration, see [docs/graph-stuffs.md](docs/graph-stuffs.md).
