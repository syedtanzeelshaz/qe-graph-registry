# `qe-graph-registry`

> Centralized GraphQL schema registry and contract authority for Quest Engine.

---

## 1. Overview

`qe-graph-registry` is the single source of truth for all GraphQL Schema Definition Language (SDL) types, inputs, directives, queries, and mutations across Quest Engine.

It follows the **Federated Modular Monolith** architecture:
- Schema definitions are partitioned into **domain-driven subgraphs** (`common/`, `user/`, `member/`, `organization/`, `operations/`).
- Cross-domain type relationships are explicitly declared using standard extension files (`extends.graphql`).
- Authorization is declarative via `@authorize(customer: [...], operations: [...])` driven by atomic permission strings (`<action>.<experience>.<domain>.[<subdomain>]`).
- All queries and mutations are generalized based on explicit inputs and IDs (zero dependency on implicit session / self-auth contexts in the GraphQL layer).
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
│   │   ├── directives.graphql         # @authorize, @key
│   │   ├── scalars.graphql            # DateTime, Date, JSON, UUID
│   │   ├── enums.graphql              # SortOrder
│   │   └── input.graphql              # PageRequest, Sort
│   │
│   ├── user/                          # Security & authentication principal domain
│   │   └── user.graphql               # User entity (auth status, credentials state)
│   │
│   ├── member/                        # Customer persona, profiles, and invitations domain
│   │   └── member.graphql             # Member entity, JoinRequest entity, invitations
│   │
│   ├── organization/                  # Multi-tenant workspace & roles governance domain
│   │   ├── organization.graphql       # Organization entity, Role entity, permissions
│   │   └── extends.graphql            # extend type Member { organization: Organization }
│   │
│   └── operations/                    # Internal platform operations domain
│       └── operations.graphql         # Operator entity, operations telemetry dashboard
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

### 5.1. Overview & Flow

The schema registry acts as the **central contract authority**. Schemas are authored in domain subgraphs, validated, merged into a unified supergraph, and published as versioned packages. Downstream consumers resolve packages by name and version—never by hardcoded filesystem paths.

```
                         qe-graph-registry
              (subgraph/common + domain subgraphs)
                               │
                   uv run graph-cli merge
                               ▼
              supergraph/build/supergraph.graphql
                │                             │
   [Local Dev]  │                [Local Dev]  │
  publish-local │               tarball / yalc│
                ▼                             ▼
       Local Wheel Store              Local NPM / Yalc
        (~/.qe/wheels)                     Store
                │                             │
       uv sync  │ find-links         npm / yarn
                ▼                             ▼
        Backend Service                Frontend App
      (quest-engine-core)          (TypeScript / React)
    • Ariadne loads SDL            • Typed code generation
    • Binds resolvers/loaders      • Apollo / TanStack Query

═════════════════════════════════════════════════════════════
                   REMOTE / CI / PRODUCTION
═════════════════════════════════════════════════════════════
                │                             │
     uv publish │                  npm publish│
                ▼                             ▼
      AWS CodeArtifact /            AWS CodeArtifact /
       Private PyPI                  Private NPM
                │                             │
    uv sync (UV_EXTRA_INDEX_URL)    npm install (.npmrc)
                ▼                             ▼
       Production Backend            Production Frontend
```

---

### 5.2. Backend Integration (`quest-engine-core`)

#### Local Development (The Python `mavenLocal()` Pattern)
1. **Publish wheel locally**:
   ```bash
   uv run graph-cli publish-local --version 0.1.0
   ```
2. **Configure downstream `pyproject.toml`**:
   ```toml
   [tool.uv]
   find-links = ["~/.qe/wheels"]

   [project]
   dependencies = [
       "qe-graph-registry==0.1.0",
   ]
   ```
3. **Sync dependency**:
   ```bash
   uv sync --reinstall-package qe-graph-registry
   ```
4. **Load schema in Ariadne**:
   ```python
   from ariadne import load_schema_from_path
   from registry import get_supergraph_path

   schema_path = get_supergraph_path()
   type_defs = load_schema_from_path(str(schema_path))
   ```

#### Production / CI Deployment
- CI publishes the wheel to AWS CodeArtifact / Private PyPI: `uv publish --publish-url <CODEARTIFACT_INDEX_URL>`.
- Backend resolves `qe-graph-registry==<version>` via standard `UV_EXTRA_INDEX_URL`.

---

### 5.3. Frontend Integration

#### Local Development
- Generate a local tarball with `npm pack` or publish locally via `yalc`:
   ```bash
   # Inside qe-graph-registry
   npm pack
   # Inside frontend app
   npm install /path/to/quest-engine-graph-registry-0.1.0.tgz
   ```

#### Production / CI Deployment
- Published to AWS CodeArtifact as `@quest-engine/graph-registry`.
- Frontend runs `graphql-codegen` against `@quest-engine/graph-registry/supergraph/build/supergraph.graphql` to generate typed React hooks.

---

### 5.4. Breaking Change Governance

Before merging any schema modifications, run diff against the baseline target:
```bash
uv run graph-cli diff --base origin/main
```
If breaking changes (e.g. removed fields, changed scalar types) are detected, the command exits with code `1`, blocking CI pipelines from accidentally breaking clients.
