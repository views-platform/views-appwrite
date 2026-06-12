
# ADR-001: Ontology of the Repository

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

`views-appwrite` exists to be a *generic* Appwrite client — the single source of truth
for "how to talk to Appwrite" across the VIEWS platform. Its entire value proposition
depends on a sharp boundary: it must contain everything about talking to Appwrite and
**nothing** about VIEWS domain logic. The roadmap (`README.md`) is explicit that the
most likely way this package fails long-term is scope creep — "someone adds a utility
function, then a DataFrame helper, then a VIEWS-specific schema, and it becomes
pipeline-core-lite" (README R5).

Without an explicit ontology, systems accumulate implicit concepts, overloaded
abstractions, and objects that mix responsibilities. For this package specifically, the
danger is concrete: the two source implementations already overloaded `FileMetadata`
with domain fields. An explicit ontology defines **what kinds of things are allowed to
exist** here, and — equally importantly — which kinds are explicitly disallowed.

No code exists yet. The categories below describe the **intended** architecture from the
roadmap's "Package Design" and "What This Package Contains / Does NOT Contain"
sections. When implementation begins, classes must map onto these categories or be
rejected.

---

## Decision

This repository defines a **closed set of conceptual categories** that are allowed to
exist. Each category has a clear semantic role, an expected stability level, and explicit
boundaries.

Anything that does not clearly belong to one of these categories — in particular,
anything that encodes VIEWS domain meaning — is considered **out of scope** and must
be redesigned or rejected.

---

## Core Ontological Categories

Each category lists its purpose, authority level, expected stability, representative
entities (planned), and what it must not contain.

### 1. Configuration
- **Purpose:** A single immutable object holding all Appwrite connection settings that a consumer constructs and passes in.
- **Representative entities:** `AppwriteConfig` (frozen dataclass) — planned in `src/views_appwrite/client.py`.
- **Authority:** Authoritative (the declared source of all connection semantics).
- **Stability:** Stable.
- **Must not contain:** Environment-variable loading (`os.getenv`/`load_dotenv`), `ModelPathManager` coupling, or any domain field. Cache location is a plain `cache_dir: Optional[Path]`.

### 2. Result Envelope
- **Purpose:** A uniform return type for every operation so consumers never touch raw SDK responses.
- **Representative entities:** `OperationResult{success, data, error, code}` — `client.py`.
- **Authority:** Authoritative for operation outcomes.
- **Stability:** Stable.
- **Must not contain:** Raw SDK objects; `.data` holds plain dicts only.

### 3. SDK Client Adapter
- **Purpose:** Thin wrapper over the Appwrite SDK `Client`; handles authentication, SDK-version detection, and timeout configuration. All SDK calls go through it.
- **Representative entities:** `AppwriteClient` — `client.py`.
- **Authority:** Infrastructure.
- **Stability:** Stable.
- **Must not contain:** Business decisions about what to upload/download.

### 4. Compatibility Shims
- **Purpose:** Normalise Appwrite SDK responses across versions (dict in SDK 13, Pydantic models in SDK 14+).
- **Representative entities:** `_as_dict()`, `_get()` — planned in `src/views_appwrite/compat.py`.
- **Authority:** Infrastructure.
- **Stability:** **Evolving** — tracks SDK changes; the one place SDK differences are absorbed.
- **Must not contain:** Anything that is not pure response normalisation.

### 5. Resource Managers
- **Purpose:** Each owns exactly one Appwrite resource concern.
- **Representative entities:** `StorageManager` (files; `storage.py`), `MetadataManager` (metadata database/collection CRUD; `metadata.py`), `CacheManager` (local disk cache with TTL; `cache.py`).
- **Authority:** Authoritative within their concern.
- **Stability:** Stable.
- **Must not contain:** Cross-concern orchestration (that belongs to the Facade) or domain metadata schemas.

### 6. Auth Strategies
- **Purpose:** Pluggable authentication mechanisms.
- **Representative entities:** `AuthManager` (ABC), `ApiKeyAuth`, `SessionAuth` — `auth.py`.
- **Authority:** Authoritative for authentication.
- **Stability:** Stable.

### 7. Facade / Orchestrator
- **Purpose:** Composes the resource managers into the high-level interface consumers actually use (`upload`, `download`, `get_latest`, `search`, `delete`, `list_all`).
- **Representative entities:** `DatastoreManager` — `datastore.py`.
- **Authority:** Authoritative — this is the public surface.
- **Stability:** Stable.
- **Must not contain:** Domain vocabulary ("predictions", "forecasts") or domain validation.

### 8. Metadata Value
- **Purpose:** A generic, schema-free carrier for file attributes.
- **Representative entities:** `FileMetadata` (generic, no domain fields; `metadata.py`) and the opaque `Dict[str, Any]` metadata payload passed through to Appwrite.
- **Authority:** Derived / pass-through (the consumer owns schema meaning, per ADR-003).
- **Stability:** **Evolving** — intentionally unconstrained so consumers can attach any fields.
- **Must not contain:** Required domain fields (`loa`, `targets`, `category`, etc.). Those stay in consumer repos.

---

## Stability Rules

- Categories 1–3 and 5–7 are expected to be **stable** across the lifetime of the project. They change only on deliberate, ADR-worthy decisions.
- **Compatibility Shims (4)** are explicitly allowed to evolve as the Appwrite SDK changes — that is their job. Their public effect (consumers get plain dicts) must stay constant.
- **Metadata Value (8)** is explicitly allowed to flex per consumer, because the package declares no opinion about metadata schema.

This encodes the roadmap's governing principle: *unstable depends on stable*. The two evolving categories are isolated so churn does not propagate into the stable public surface.

---

## Explicit Non-Entities

The following are **not allowed** as first-class concepts in this repository (from README "What This Package Does NOT Contain"):

- **Domain models** — `PredictionMetadata`, or any domain-loaded `FileMetadata` carrying `loa`/`targets`/`category`. These belong in consumer repos.
- **Data transformation / postprocessing** — DataFrame manipulation, GAUL mapping, HDI-MAP calculations.
- **API endpoint definitions** — FastAPI routes, HTTP serving logic.
- **Pipeline orchestration** — model training, ensemble management, run types, the `PredictionSaver` protocol and its savers, `ModelPathManager`.
- **Environment-variable loading** — `os.getenv()` / `load_dotenv()`. The consumer supplies all config values.
- **Domain vocabulary** — "predictions", "forecasts", "PredictionStore". Vocabulary here is generic: files, metadata, buckets, collections.
- Implicit or inferred semantics; objects that mix multiple ontological roles; "convenience" abstractions that hide meaning.

If a concept matters and is generic to Appwrite, it must be explicit and placed in a category above. If it carries domain meaning, it does not belong here at all.

---

## Consequences

### Positive
- Shared vocabulary across contributors and consumer repos
- A concrete review test for every PR: *"Would a non-VIEWS project using Appwrite find this useful?"* If no, it is a non-entity.
- Reduced conceptual drift; the boundary that prevents a second God-repo is written down

### Negative
- Requires upfront discipline; some convenient shortcuts (e.g. a built-in DataFrame loader) are disallowed
- Consumers must own their own metadata schemas and validation

These trade-offs are accepted.

---

## Notes

This ADR defines *what exists*, not *how components depend on each other*.
Dependency rules are defined in ADR-002; semantic authority (including the opaque-metadata rule) in ADR-003; boundary contracts in ADR-009.
