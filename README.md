# views-appwrite

Shared Appwrite client library for the VIEWS platform. Extracts the duplicated Appwrite storage, metadata, and caching logic from `views-pipeline-core` and `views-faoapi` into a single, independently versioned package.

**Status:** Planned (this document is the roadmap)

---

## Table of Contents

1. [Motivation](#motivation)
2. [What This Package Contains](#what-this-package-contains)
3. [What This Package Does NOT Contain](#what-this-package-does-not-contain)
4. [Current Duplication Map](#current-duplication-map)
5. [Dependency Graph: Before and After](#dependency-graph-before-and-after)
6. [Package Design](#package-design)
7. [Migration Plan](#migration-plan)
   - 7.1 [Phase 1: Extract and Publish](#phase-1-extract-and-publish)
   - 7.2 [Phase 2: Migrate views-faoapi](#phase-2-migrate-views-faoapi)
   - 7.3 [Phase 3: Migrate views-pipeline-core](#phase-3-migrate-views-pipeline-core)
   - 7.4 [Phase 4: Migrate views-postprocessing](#phase-4-migrate-views-postprocessing)
8. [SDK Compatibility](#sdk-compatibility)
9. [Testing Strategy](#testing-strategy)
10. [Risks and Things to Be Mindful Of](#risks-and-things-to-be-mindful-of)
11. [Decision Log](#decision-log)

---

## Motivation

Three repos in the VIEWS platform interact with Appwrite cloud storage today:

| Repo | Role | Appwrite code |
|------|------|---------------|
| `views-pipeline-core` | Uploads predictions to the public forecast store | `modules/appwrite/file.py` (~3,000 lines), `modules/datastore/datastore.py` (~550 lines) |
| `views-faoapi` | Downloads predictions from the UNFAO bucket and serves them via HTTP | `managers/appwrite.py` (~2,000 lines), `managers/prediction.py` (~380 lines) |
| `views-postprocessing` | Reads from the public forecast bucket, transforms data, writes to the UNFAO bucket | Uses `views-pipeline-core`'s classes directly |

The problem is that `views-faoapi` was deliberately decoupled from `views-pipeline-core` (to avoid pulling in the entire God-repo as a dependency), so its Appwrite client was copy-pasted and evolved independently. The two implementations are now ~90% identical in structure but differ in:

- SDK compatibility layer (`views-faoapi` handles both Appwrite SDK 13 and 14+; `views-pipeline-core` targets SDK 13 only)
- Naming (`AppWriteFileManager` vs `AppWriteFileModule`, `PredictionStoreManager` vs `DatastoreModule`, `PredictionMetadata` vs `FileMetadata`)
- Bug fixes applied to one but not the other (the `_as_dict` guard for SDK 14 only exists in `views-faoapi`)

This situation will get worse: we plan to clone `views-faoapi` to build consumer APIs for other stakeholders (e.g., World Bank, UNHCR). Each clone would carry its own copy of the Appwrite client. A bug fix or SDK upgrade would need to be applied N times.

`views-appwrite` solves this by being the single source of truth for "how to talk to Appwrite." Every consumer API and the pipeline itself depend on this one package. Changes propagate by bumping a version number, not by copy-pasting across repos.

---

## What This Package Contains

Everything that is about **talking to Appwrite** and nothing else. Concretely:

### Core client (`views_appwrite.client`)

- **`AppwriteConfig`** -- Frozen dataclass holding connection settings: endpoint, project_id, credentials, auth_method, bucket/collection/database IDs, cache TTL, timeout. This is the single configuration object every consumer constructs.
- **`AppwriteClient`** -- Thin wrapper around the Appwrite SDK `Client`. Handles authentication (API key or session), SDK version detection, and timeout configuration. All SDK calls go through this.
- **`OperationResult`** -- Standardised return type for every operation: `success`, `data`, `error`, `code`. Already exists in both repos with identical structure.

### Storage (`views_appwrite.storage`)

- **`StorageManager`** -- File upload, download, deletion, listing. Wraps `appwrite.services.storage.Storage`. Handles:
  - Upload with automatic deduplication via file hashing
  - Download with streaming to disk
  - Bucket creation on first upload (auto-provision)
  - File listing with pagination

### Metadata (`views_appwrite.metadata`)

- **`MetadataManager`** -- CRUD operations on the metadata database/collection that tracks file attributes (fileId, bucketId, filename, loa, category, targets, etc.). Handles:
  - Database and collection auto-creation with retry logic
  - Attribute schema creation (string, integer, enum attributes) with conflict handling
  - Document search with filters and pagination
  - Metadata updates and deletions

### Cache (`views_appwrite.cache`)

- **`CacheManager`** -- Local disk cache with TTL-based validation. Handles:
  - Cache directory management per bucket
  - TTL expiry checks
  - Remote timestamp comparison (is the cached file still current?)
  - Cache invalidation and cleanup

### SDK compatibility (`views_appwrite.compat`)

- **`_as_dict()`** -- Normalises Appwrite SDK responses across versions (dict in SDK 13, Pydantic models in SDK 14+). This is the bug fix that currently only exists in `views-faoapi`.
- **`_get()`** -- Attribute-or-key access that works with dicts, Pydantic models, and SimpleNamespace. Handles `$`-prefixed keys (Appwrite aliases like `$id`, `$createdAt`).

### High-level facade (`views_appwrite.datastore`)

- **`DatastoreManager`** -- The "PredictionStoreManager"/"DatastoreModule" equivalent. Composes `StorageManager`, `MetadataManager`, and `CacheManager` into the interface consumers actually use:
  - `upload(file, filename, metadata)` -- upload file + store metadata
  - `download(file_id, save_path, use_cache)` -- download with caching
  - `get_latest(filters)` -- find newest file matching metadata filters
  - `search(filters)` -- search by metadata
  - `delete(file_id)` -- delete file + metadata
  - `list_all()` -- list everything in the bucket

### Auth (`views_appwrite.auth`)

- **`AuthManager`** (ABC), **`ApiKeyAuth`**, **`SessionAuth`** -- Pluggable authentication strategies. Same structure as both repos already have.

---

## What This Package Does NOT Contain

The boundary is critical. This package must remain a **generic Appwrite client** that knows nothing about VIEWS domain logic. If it starts accumulating domain concepts, it becomes a second God-repo.

Specifically, `views-appwrite` does **not** contain:

- **Data transformation or postprocessing logic** -- No DataFrame manipulation, no GAUL mapping, no HDI-MAP calculations. That stays in `views-faoapi`, `views-postprocessing`, etc.
- **API endpoint definitions** -- No FastAPI routes, no HTTP serving logic. That stays in consumer APIs.
- **Pipeline orchestration** -- No model training, no ensemble management, no run types. That stays in `views-pipeline-core`.
- **Domain-specific metadata schemas** -- The `DatastoreManager` accepts a plain `Dict[str, Any]` for metadata. It does not enforce that metadata must have `loa`, `targets`, `category`, etc. Metadata validation is the consumer's job. (The `PredictionMetadata` / `FileMetadata` classes that enforce these fields stay in the consumer repos.)
- **ModelPathManager** -- The current `AppwriteConfig` takes a `path_manager` field used for cache directory resolution. `views-appwrite` should accept an optional `cache_dir: Path` instead. If consumers want to derive that from their path manager, they pass `path_manager.cache / "appwrite"`. The path manager itself is a pipeline-core concept and does not belong here.
- **Environment variable loading** -- This package does not call `os.getenv()` or `load_dotenv()`. The consumer constructs `AppwriteConfig` with values it obtained however it likes. This keeps the package testable and avoids hidden coupling to `.env` file layouts.
- **Prediction-specific terminology** -- No "predictions", no "forecasts", no "PredictionStore". The vocabulary is generic: files, metadata, buckets, collections. Consumer repos wrap `DatastoreManager` with their own domain-specific names if they want to.

---

## Current Duplication Map

The table below shows what exists today and where the code should live after migration.

### Low-level Appwrite client (file operations, auth, caching, metadata)

| Concept | `views-pipeline-core` | `views-faoapi` | `views-appwrite` target |
|---------|----------------------|----------------|------------------------|
| SDK client wrapper | `modules/appwrite/file.py` (3,047 lines) | `managers/appwrite.py` (2,000 lines) | `views_appwrite.client` + `views_appwrite.storage` + `views_appwrite.metadata` + `views_appwrite.cache` + `views_appwrite.auth` |
| Config dataclass | `AppwriteConfig` in `file.py` | `AppwriteConfig` in `appwrite.py` | `views_appwrite.client.AppwriteConfig` |
| Result type | `OperationResult` in `file.py` | `OperationResult` in `appwrite.py` | `views_appwrite.client.OperationResult` |
| Auth managers | `AuthManager`, `ApiKeyAuth`, `SessionAuth` in `file.py` | Same names, same structure in `appwrite.py` | `views_appwrite.auth` |
| Cache manager | `CacheManager` in `file.py` | `CacheManager` in `appwrite.py` | `views_appwrite.cache.CacheManager` |
| Metadata handler | `AppwriteMetadataHandler` in `file.py` | `AppwriteMetadataHandler` in `appwrite.py` | `views_appwrite.metadata.MetadataManager` |
| SDK compat layer | Does not exist (SDK 13 only) | `_as_dict()`, `_get()` in `appwrite.py` | `views_appwrite.compat` |

### High-level datastore (upload/download/search predictions)

| Concept | `views-pipeline-core` | `views-faoapi` | After migration |
|---------|----------------------|----------------|-----------------|
| Datastore facade | `DatastoreModule` in `modules/datastore/datastore.py` (703 lines) | `PredictionStoreManager` in `managers/prediction.py` (383 lines) | `views_appwrite.datastore.DatastoreManager` (generic); consumer repos keep thin wrappers with domain vocabulary |
| File metadata model | `FileMetadata` in `file.py` | `FileMetadata` in `appwrite.py` | `views_appwrite.metadata.FileMetadata` (generic, no domain fields) |
| Prediction metadata | `FileMetadata` (overloaded with domain fields) | `PredictionMetadata` in `prediction.py` | Stays in consumer repos -- not part of `views-appwrite` |

### Divergences to reconcile

| Area | `views-pipeline-core` | `views-faoapi` | Resolution |
|------|----------------------|----------------|------------|
| SDK version support | SDK 13 only | SDK 13 + 14+ via `_as_dict`/`_get` | Adopt `views-faoapi`'s compat layer |
| Class naming | `AppWriteFileModule` | `AppWriteFileManager` | New name: `AppwriteClient` (no camelCase "Write") |
| Timeout config | Not configurable | `timeout_seconds` and `connect_timeout_seconds` in config | Include both in `AppwriteConfig` |
| Saver protocol | `PredictionSaver` Protocol + `AppwriteSaver`, `NpzSaver`, `LocalParquetSaver` | Does not exist | Stays in `views-pipeline-core` -- these are pipeline concepts, not Appwrite concepts |
| ModelPathManager coupling | `path_manager` field on `AppwriteConfig` | Same field, different import path | Replace with `cache_dir: Optional[Path]` |

---

## Dependency Graph: Before and After

### Before (current state)

```
views-models (orchestrator)
├── views-postprocessing
│   └── views-pipeline-core  ←── Appwrite client (copy A: 3,750 lines)
│       └── appwrite SDK
└── views-faoapi             ←── Appwrite client (copy B: 2,383 lines)
    └── appwrite SDK
```

`views-faoapi` and `views-pipeline-core` are independent (no import path between them), which is correct. But they each maintain their own Appwrite client, which drifts.

When we clone `views-faoapi` for new consumer APIs, each clone carries copy B:

```
views-faoapi         ←── copy B
views-worldbankapi   ←── copy B'
views-unhcrapi       ←── copy B''
```

### After (target state)

```
views-appwrite                    ←── single Appwrite client
├── appwrite SDK (only external dependency)
└── (nothing else from the platform)

views-pipeline-core
├── views-appwrite               ←── depends DOWN
└── (pipeline-specific code: savers, model paths, orchestration)

views-faoapi
├── views-appwrite               ←── depends DOWN
└── (FAO-specific code: GAUL mapping, HDI-MAP, API endpoints)

views-worldbankapi
├── views-appwrite               ←── depends DOWN
└── (WB-specific code)

views-postprocessing
├── views-pipeline-core          ←── unchanged
└── (implicitly gets views-appwrite via pipeline-core)
```

Key properties:
- **DAG**: `views-appwrite` depends on nothing in the platform. Dependencies only flow downward.
- **Stable dependency**: `views-appwrite` changes infrequently (Appwrite SDK upgrades, bug fixes). Consumer APIs change often (new endpoints, new data levels). Unstable depends on stable.
- **No transitive coupling**: `views-faoapi` and `views-pipeline-core` remain independent of each other. They share a library, not a dependency on each other.

---

## Package Design

### Directory structure

```
views-appwrite/
├── pyproject.toml              # hatchling build, minimal deps
├── README.md                   # this file
├── src/
│   └── views_appwrite/
│       ├── __init__.py         # re-exports: AppwriteConfig, DatastoreManager, OperationResult
│       ├── client.py           # AppwriteConfig, AppwriteClient (SDK wrapper)
│       ├── storage.py          # StorageManager (upload, download, delete, list)
│       ├── metadata.py         # MetadataManager, FileMetadata (database/collection CRUD)
│       ├── cache.py            # CacheManager (disk cache with TTL)
│       ├── auth.py             # AuthManager ABC, ApiKeyAuth, SessionAuth
│       ├── compat.py           # _as_dict(), _get() -- SDK 13/14+ normalisation
│       └── datastore.py        # DatastoreManager (high-level facade)
└── tests/
    ├── test_compat.py          # SDK normalisation unit tests
    ├── test_cache.py           # Cache TTL and validation tests
    ├── test_storage.py         # Storage operations (mocked SDK)
    ├── test_metadata.py        # Metadata CRUD (mocked SDK)
    ├── test_datastore.py       # Facade integration (mocked SDK)
    └── test_integration.py     # Live Appwrite tests (requires credentials, skipped in CI)
```

### Dependencies

```toml
[project]
dependencies = [
    "appwrite>=5.0.0",          # Appwrite Python SDK
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov",
    "ruff",
]
```

That's it. No pandas, no numpy, no FastAPI, no pipeline-core. The package is a pure Appwrite client. Consumers bring their own data libraries.

The one exception: `DatastoreManager.download()` returns raw bytes (or writes to a file path). If a consumer wants a DataFrame, they call `pd.read_parquet(io.BytesIO(result.data["file_bytes"]))` themselves -- exactly as `views-postprocessing` already does today.

### Public API surface

The package exposes a small, stable API. Everything else is internal.

```python
# What consumers import:
from views_appwrite import AppwriteConfig, DatastoreManager, OperationResult

# Construct config (consumer provides all values -- no hidden env vars)
config = AppwriteConfig(
    endpoint="https://fra.cloud.appwrite.io/v1",
    project_id="691b14fc0024f568fb42",
    credentials=api_key,
    bucket_id="unfao_bucket",
    collection_id="unfao",
    database_id="file_metadata",
    cache_dir=Path("/tmp/appwrite_cache"),
)

# Use the facade
store = DatastoreManager(config)
result = store.upload(file_path, filename="predictions.parquet", metadata={...})
latest = store.get_latest(filters={"category": "forecast"})
data   = store.download(file_id="abc123", save_path="/tmp/out.parquet")
```

### Design principle: no opinions about metadata

The current `PredictionMetadata` (in `views-faoapi`) enforces that metadata must have `loa`, `name`, `type`, `targets`, `category`. The current `FileMetadata` (in `views-pipeline-core`) has a different set of required fields.

`views-appwrite` does not enforce any metadata schema. It accepts `Dict[str, Any]` and passes it through to the Appwrite database. Schema validation is the consumer's responsibility.

This means:
- `views-faoapi` keeps its `PredictionMetadata` class and validates before calling `store.upload()`
- `views-pipeline-core` keeps its `FileMetadata` class and validates before calling `store.upload()`
- A future `views-worldbankapi` can define its own metadata schema
- `views-appwrite` never needs to change when a consumer adds a metadata field

---

## Migration Plan

### Phase 1: Extract and Publish

**Goal:** A working `views-appwrite` package on GitHub that can be pip-installed.

**Steps:**

1. **Scaffold the package** with `pyproject.toml` (hatchling), `src/views_appwrite/` layout, and this README.

2. **Start from `views-faoapi`'s `appwrite.py`** as the base, since it has the SDK 13/14 compat layer and the `_as_dict`/`_get` fixes that `views-pipeline-core` lacks. Copy it into `src/views_appwrite/` and decompose the monolith into the module structure defined in [Package Design](#package-design):
   - Extract `_as_dict()`, `_get()` into `compat.py`
   - Extract `AuthManager`, `ApiKeyAuth`, `SessionAuth` into `auth.py`
   - Extract `CacheManager` into `cache.py`
   - Extract `AppwriteMetadataHandler` into `metadata.py`
   - Extract file upload/download/delete into `storage.py`
   - Extract `AppwriteConfig`, `OperationResult`, client init into `client.py`
   - Build `DatastoreManager` in `datastore.py` from `PredictionStoreManager`'s structure

3. **Remove domain coupling:**
   - Replace `from views_faoapi.managers.model import ModelPathManager` with `cache_dir: Optional[Path]`
   - Remove `PredictionMetadata` (stays in consumer repos)
   - Rename classes to generic names (see duplication map)
   - Remove any `os.getenv()` calls

4. **Write tests** against the decomposed modules. Unit tests mock the Appwrite SDK. One integration test file connects to a real Appwrite instance (skipped unless `APPWRITE_TEST_ENDPOINT` is set).

5. **Publish to GitHub** as `prio-data/views-appwrite` (or `views-platform/views-appwrite` depending on org preference). Tag `v0.1.0`. Consumers can install via `pip install git+https://github.com/prio-data/views-appwrite.git@v0.1.0`.

**Deliverable:** `pip install views-appwrite` works. The package passes its own test suite. No other repos are modified yet.

### Phase 2: Migrate views-faoapi

**Goal:** `views-faoapi` depends on `views-appwrite` instead of its own `managers/appwrite.py`.

**Why this repo first:** We control it directly, the API is in shadow deployment (low operational risk), and it was the source of the extracted code, so compatibility is highest.

**Steps:**

1. **Add dependency** to `views-faoapi`'s `pyproject.toml`:
   ```toml
   dependencies = [
       "views-appwrite @ git+https://github.com/prio-data/views-appwrite.git@v0.1.0",
       # ... existing deps
   ]
   ```

2. **Update imports in `managers/prediction.py`:**
   ```python
   # Before:
   from views_faoapi.managers.appwrite import AppwriteConfig, AppWriteFileManager, OperationResult

   # After:
   from views_appwrite import AppwriteConfig, DatastoreManager, OperationResult
   ```

3. **Rewrite `PredictionStoreManager`** to be a thin wrapper around `DatastoreManager`:
   ```python
   class PredictionStoreManager:
       def __init__(self, config: AppwriteConfig):
           self._store = DatastoreManager(config)

       def upload_predictions(self, file, filename, **metadata_fields):
           metadata = PredictionMetadata(**metadata_fields).to_dict()
           return self._store.upload(file, filename, metadata)

       def get_latest_file_id(self, filters):
           return self._store.get_latest(filters)
       # ... etc
   ```
   `PredictionMetadata` stays in this file -- it's domain validation, not Appwrite logic.

4. **Delete `managers/appwrite.py`** (2,000 lines removed). This is the big payoff.

5. **Update `managers/api.py`** -- the API manager constructs `AppwriteConfig`. Change the import path. The config fields are the same, so the constructor call should be unchanged.

6. **Run the existing test suite** (`test_integration_appwrite.py`, `test_appwrite_manager.py`, `test_datastore_manager.py`). These tests exercise the full upload/download/search path and will catch any regression.

7. **Test on Hetzner** -- deploy the updated `views-faoapi` to the shadow server and verify the API serves data correctly from `unfao_bucket`.

**Deliverable:** `views-faoapi` has ~2,000 fewer lines of Appwrite code. Its test suite passes. The live API works.

**Mindful of:**
- The `_as_dict()` and `_get()` compat functions are used throughout `managers/api.py` (in `_get_latest_dataframe` and the format-guessing cascade). After deleting `appwrite.py`, these must be imported from `views_appwrite.compat` instead. Search for all `from views_faoapi.managers.appwrite import` to catch every import site.
- The `AppwriteConfig` field `path_manager` is used in `views-faoapi` to derive cache paths. After migration, the consumer must pass `cache_dir=path_manager.cache / "appwrite"` explicitly.

### Phase 3: Migrate views-pipeline-core

**Goal:** `views-pipeline-core` depends on `views-appwrite` instead of its own `modules/appwrite/file.py`.

**Why this repo second:** It has a different maintainer (the pipeline-core author), so this phase requires coordination. The migration is also more complex because pipeline-core has additional abstractions (`PredictionSaver` protocol, `AppwriteSaver`, `NpzSaver`, etc.) layered on top of the Appwrite client.

**Steps:**

1. **Add dependency** to `views-pipeline-core`'s build config (poetry or hatchling, depending on what they use):
   ```
   views-appwrite @ git+https://github.com/prio-data/views-appwrite.git@v0.1.0
   ```

2. **Update `modules/datastore/datastore.py`:**
   - Replace `from views_pipeline_core.modules.appwrite.file import AppwriteConfig, AppWriteFileModule, OperationResult`
   - With `from views_appwrite import AppwriteConfig, DatastoreManager, OperationResult`
   - `DatastoreModule` becomes a thin domain wrapper, or is replaced entirely by `DatastoreManager` if the interface is close enough.

3. **Update `managers/prediction/savers.py`:**
   - `AppwriteSaver` currently wraps `DatastoreModule.upload_data()`. After migration, it wraps `DatastoreManager.upload()`.
   - The `PredictionSaver` protocol, `NpzSaver`, `LocalParquetSaver`, `ViewsForecastsSaver` are pipeline concepts and stay in pipeline-core unchanged.

4. **Update `configs/prediction_store.py`:**
   - This file currently validates Appwrite env vars at import time and constructs `AppwriteConfig`. It should now import `AppwriteConfig` from `views_appwrite` instead of from `modules.appwrite.file`.

5. **Deprecate but don't delete `modules/appwrite/file.py` immediately:**
   - Other code in pipeline-core may import from it. Grep for all import sites first.
   - Add a deprecation shim: `from views_appwrite import *  # deprecated: import from views_appwrite directly`
   - Remove the shim in a follow-up release once all internal references are updated.

6. **Run pipeline-core's test suite** and any downstream integration tests.

**Deliverable:** `views-pipeline-core` delegates all Appwrite operations to `views-appwrite`. Its own Appwrite module is deprecated. The `PredictionSaver` protocol and saver implementations remain in pipeline-core.

**Mindful of:**
- **The pipeline-core author must be involved.** This is their repo. Present the migration as: "your code now has a cleaner dependency, and SDK upgrades happen in one place." Don't frame it as "your code was wrong."
- **`AppwriteConfig` field differences.** Pipeline-core's `AppwriteConfig` has `timeout_seconds` but not `connect_timeout_seconds`. The `views-appwrite` version should be a superset. Check that no pipeline-core code depends on fields that are removed or renamed.
- **`ModelPathManager` coupling.** Pipeline-core's `AppwriteConfig` takes `path_manager: ModelPathManager`. The migrated version takes `cache_dir: Optional[Path]`. Every call site constructing `AppwriteConfig` must be updated to pass `cache_dir=path_manager.cache_dir / "appwrite"` or similar.
- **Graceful degradation in `AppwriteSaver`.** This saver catches all exceptions and logs instead of raising (a deliberate design choice -- see D-10 in the risk register). This behavior is preserved: `AppwriteSaver` wraps `DatastoreManager`, and if `DatastoreManager.upload()` raises, `AppwriteSaver.save()` catches it. No change to the graceful-degradation contract.

### Phase 4: Migrate views-postprocessing

**Goal:** `views-postprocessing` works correctly after pipeline-core's migration to `views-appwrite`.

**Why this is the easiest phase:** `views-postprocessing` does not import Appwrite classes directly. It imports `AppwriteConfig` and `DatastoreModule` from `views-pipeline-core`. So if Phase 3 is done cleanly (with deprecation shims or updated exports), `views-postprocessing` may need zero changes.

**Steps:**

1. **Check import paths in `unfao/managers/unfao.py`:**
   ```python
   # Current:
   from views_pipeline_core.modules.appwrite.file import AppwriteConfig
   from views_pipeline_core.modules.datastore import DatastoreModule
   ```
   If pipeline-core's deprecation shim re-exports these names, this code works unchanged.

2. **If pipeline-core removes the shim** (in a later release), update to:
   ```python
   from views_appwrite import AppwriteConfig, DatastoreManager
   ```
   And update `DatastoreModule(...)` calls to `DatastoreManager(...)`.

3. **Add `views-appwrite` as a direct dependency** of `views-postprocessing` only if it imports from `views_appwrite` directly. If it continues to import through `views-pipeline-core`, no new dependency is needed (though an explicit dependency is cleaner).

4. **Test the full postprocessing pipeline:**
   - Read from `prod_forecasts` bucket (via pipeline-core's `DatastoreModule` / `DatastoreManager`)
   - Transform (append GAUL metadata)
   - Write to `unfao_bucket`
   - Verify `views-faoapi` can read the written data

**Deliverable:** The full data pipeline (postprocessing → Appwrite → API) works end-to-end with `views-appwrite` as the shared client.

**Mindful of:**
- `views-postprocessing` constructs two separate `AppwriteConfig` objects in `unfao.py`: one for reading from `prod_forecasts` and one for writing to `unfao_bucket`. Both must use the same `AppwriteConfig` class. After migration, this is guaranteed because there's only one source.
- The commented-out config blocks in `unfao.py` (lines 93-117) reference experimental bucket IDs (`APPWRITE_UNFAO_FORECASTS_BUCKET_ID`). These can be cleaned up during migration but are not blocking.

---

## SDK Compatibility

The Appwrite Python SDK had a breaking change between versions 13 and 14:

| Aspect | SDK 13 (and earlier) | SDK 14+ |
|--------|---------------------|---------|
| Response type | Plain `dict` | Pydantic `BaseModel` subclasses |
| Access pattern | `response["$id"]` | `response.id` (attribute) or `response.to_dict()["$id"]` |
| Nested data | Flat dict with all fields | `_data`-bearing models nest fields under `.data` |

`views-faoapi` already solved this with `_as_dict()` and `_get()` (lines 31-72 of `managers/appwrite.py`). `views-pipeline-core` did not -- it only works with SDK 13.

`views-appwrite` adopts the `views-faoapi` solution in `compat.py` and applies it consistently everywhere. This means:

1. **`views-appwrite` works with both SDK 13 and SDK 14+** out of the box.
2. When the platform eventually standardises on SDK 14+, the compat layer can be simplified but the public API doesn't change.
3. Consumers never interact with raw SDK response objects. They get `OperationResult` (which contains plain dicts in `.data`).

### Pinning strategy

`pyproject.toml` should use a broad pin: `appwrite>=5.0.0`. The compat layer handles SDK differences at runtime. Consumers who need a specific SDK version can pin it in their own `pyproject.toml` and `views-appwrite` will adapt.

If a future SDK version introduces further breaking changes to the response model, the fix goes into `compat.py` once and all consumers get it.

---

## Testing Strategy

### Unit tests (run in CI, no credentials needed)

Mock the Appwrite SDK at the `Client`/`Storage`/`Databases` boundary. Test that:

- `_as_dict()` normalises SDK 13 dicts, SDK 14 Pydantic models, and SimpleNamespace objects identically
- `_get()` handles `$`-prefixed keys, regular keys, and missing keys across all response types
- `CacheManager` respects TTL, detects stale timestamps, and cleans up expired entries
- `StorageManager` retries bucket creation on `storage_bucket_not_found`
- `MetadataManager` handles attribute creation retries, pagination, and filter construction
- `DatastoreManager.get_latest()` sorts by `$createdAt` descending and returns the first match
- `AppwriteConfig.__post_init__()` normalises `auth_method` strings to enums and derives `bucket_name`/`database_name` defaults

### Contract tests (run against both repos during migration)

During Phases 2 and 3, the existing test suites in `views-faoapi` and `views-pipeline-core` serve as contract tests. They verify that `views-appwrite` is a drop-in replacement:

- `views-faoapi`: `test_integration_appwrite.py`, `test_appwrite_manager.py`, `test_datastore_manager.py`, `test_sdk_compat.py`
- `views-pipeline-core`: `tests/test_modules/test_appwrite.py`

If these tests pass with `views-appwrite` as the backend, the migration is correct.

### Integration tests (run manually, require Appwrite credentials)

A single `test_integration.py` that connects to a real Appwrite instance and exercises the full lifecycle:

1. Create a test bucket
2. Upload a file with metadata
3. Search by metadata filters
4. Download the file (verify content matches)
5. Download again (verify cache hit)
6. Update metadata
7. Delete the file and metadata
8. Verify bucket is clean

Skipped in CI via `@pytest.mark.skipif(not os.getenv("APPWRITE_TEST_ENDPOINT"))`. Run manually before releases.

### End-to-end test (run manually after full migration)

The ultimate test is the data pipeline:
1. Postprocessor writes to `unfao_bucket` via `views-pipeline-core` → `views-appwrite`
2. FAO API reads from `unfao_bucket` via `views-faoapi` → `views-appwrite`
3. API serves correct data to an HTTP client

This test is run manually on the Hetzner server after Phase 4.

---

## Risks and Things to Be Mindful Of

### R1: Behaviour divergence during extraction

The two Appwrite clients are ~90% identical but not 100%. During extraction, we must decide which behaviour to keep when they differ. Known divergences:

| Behaviour | `views-pipeline-core` | `views-faoapi` | Decision |
|-----------|----------------------|----------------|----------|
| SDK compat | SDK 13 only | SDK 13 + 14+ | Keep faoapi's (broader) |
| Timeout config | Not configurable | Configurable | Keep faoapi's |
| `upload_data` vs `upload_predictions` | `upload_data` accepts DataFrame directly | `upload_predictions` raises `NotImplementedError` for DataFrame | Keep the `NotImplementedError` for now -- direct DataFrame upload is a footgun (serialisation format is implicit) |
| Duplicate file detection | SHA-256 hash check, configurable overwrite | Same | No divergence |
| Error on missing bucket | Raises | Auto-creates then retries | Keep auto-create (faoapi's behaviour) |

**Mitigation:** Before extracting, write a diff of the two files' public methods and settle every divergence explicitly. Document each decision in the Decision Log below.

### R2: Import path breakage across repos

Changing import paths (`from views_pipeline_core.modules.appwrite.file import ...` → `from views_appwrite import ...`) touches many files. If a repo has scattered imports, some may be missed.

**Mitigation:** Use `grep -rn "from views_pipeline_core.modules.appwrite" .` and `grep -rn "from views_faoapi.managers.appwrite" .` before and after migration to verify zero remaining references.

### R3: Pipeline-core maintainer resistance

The pipeline-core author has a different development style and may resist the dependency. They may prefer to keep their own copy.

**Mitigation:** Frame as a benefit to them: they get SDK 14 compatibility for free, they get bug fixes from the faoapi side, and they don't have to maintain 3,000 lines of Appwrite client code. If they refuse, `views-appwrite` still works for all consumer APIs -- pipeline-core can be migrated later.

### R4: Version pinning coordination

When `views-appwrite` releases a new version, all consumers must bump. If one consumer pins an old version, they miss fixes. If the new version has breaking changes, consumers break.

**Mitigation:** Semantic versioning. Breaking changes = major version bump. Consumers pin to `>=0.1,<1.0` during the 0.x phase. After 1.0, pin to `>=1.0,<2.0`.

### R5: The package grows beyond Appwrite

The most likely way this package fails long-term is scope creep: someone adds a "utility" function, then a DataFrame helper, then a VIEWS-specific schema, and it becomes pipeline-core-lite.

**Mitigation:** The "What This Package Does NOT Contain" section is a contract. Any PR that adds domain-specific logic should be rejected. The test is: "Would a non-VIEWS project using Appwrite find this useful?" If no, it doesn't belong here.

### R6: `AppwriteConfig.path_manager` removal breaks call sites

Every place that constructs `AppwriteConfig` today passes `path_manager=...`. After migration, this field is replaced with `cache_dir=...`. This is a mechanical change but it touches multiple files in multiple repos.

**Mitigation:** During Phase 1, `views-appwrite`'s `AppwriteConfig` can temporarily accept both `path_manager` (deprecated, extracts `cache_dir` from it) and `cache_dir` (preferred). Remove `path_manager` support in v0.2.0 after all consumers have migrated.

### R7: Silent staleness (inherited from C-50)

The current `AppwriteSaver` in pipeline-core catches all exceptions during upload and logs instead of raising. If `views-appwrite` changes the exception types or error codes that `DatastoreManager.upload()` raises, `AppwriteSaver`'s catch-all will still swallow them -- but the log messages may change, making debugging harder.

**Mitigation:** `DatastoreManager.upload()` should raise specific, documented exception types. `AppwriteSaver` should catch those specific types, not bare `Exception`. This is an improvement opportunity, not a blocker for Phase 1.

---

## Decision Log

Decisions made during planning and extraction. Updated as work progresses.

| # | Date | Decision | Rationale |
|---|------|----------|-----------|
| 1 | 2026-06-01 | Start from `views-faoapi`'s `appwrite.py`, not pipeline-core's `file.py` | faoapi's version has SDK 13+14 compat (`_as_dict`, `_get`), configurable timeouts, and recent bug fixes. Pipeline-core's is larger but the extra size is mostly docstrings. |
| 2 | 2026-06-01 | Use generic vocabulary (files, buckets) not domain vocabulary (predictions, forecasts) | Keeps the package reusable for non-prediction use cases and prevents domain logic from creeping in. |
| 3 | 2026-06-01 | Accept `Dict[str, Any]` for metadata, not typed dataclasses | Domain-specific metadata schemas (`PredictionMetadata`, `FileMetadata`) belong in consumer repos. The shared package should not enforce what metadata fields exist. |
| 4 | 2026-06-01 | Replace `path_manager` with `cache_dir: Optional[Path]` | Removes coupling to `ModelPathManager` (a pipeline-core concept). Consumers derive `cache_dir` from whatever path manager they use. |
| 5 | 2026-06-01 | Migrate `views-faoapi` first, then `views-pipeline-core` | faoapi is under our direct control, is in shadow deployment (low risk), and was the extraction source. Pipeline-core requires coordination with another maintainer. |
| 6 | 2026-06-01 | Keep `PredictionSaver` protocol and saver implementations in pipeline-core | These are pipeline orchestration concepts (format selection, graceful degradation policy). They happen to use Appwrite but are not about Appwrite. |
| 7 | 2026-06-01 | Broad SDK pin (`appwrite>=5.0.0`) instead of exact pin | The compat layer handles SDK differences at runtime. Consumers who need a specific version can override. |

---

## Datafactory Notes and Recommendation

*Added 2026-06-02 after reviewing the duplication landscape and current platform priorities.*

### Assessment

The roadmap above is well-designed. The scope boundary is correct, the migration order is sensible, and the risks are honestly catalogued. The ~5,000 lines of duplicated Appwrite client code across `views-pipeline-core` and `views-faoapi` are real, and the drift between them (SDK 14 compat in faoapi only, different class names, bug fixes applied to one but not the other) will get worse over time.

That said, **the recommendation is to hold off on building this package until a concrete trigger fires.** The duplication is stable today -- it works, it's understood, and it's not blocking any current work. The cost of extraction is real (coordination with the pipeline-core maintainer, import path migration across repos, testing across both consumers), and the benefit only materialises when the duplication actively causes pain.

### Triggers that justify starting Phase 1

Start this work when any of these happen:

1. **Second consumer API clone.** The moment you clone `views-faoapi` to build a World Bank or UNHCR API, you are copying the Appwrite client a third time. At N=3, extraction pays for itself immediately. This is the strongest trigger.

2. **SDK 14 upgrade in pipeline-core.** If `views-pipeline-core` needs to upgrade to Appwrite SDK 14+, the missing `_as_dict()`/`_get()` compat layer becomes a blocking problem. Rather than backporting the fix from faoapi (creating a fourth divergent copy of the compat code), extract it once into `views-appwrite`.

3. **Bug fix that must be applied to both copies.** If a cache TTL bug, a metadata race condition, or a silent upload failure is discovered in one copy and must be fixed in both, the fix-it-twice cost is the signal that shared code is overdue.

### Why not now

- **Only two consumers exist today**, and one (`views-postprocessing`) gets its Appwrite access transitively through `views-pipeline-core`. The actual duplication is between two repos, not N.
- **Neither copy is broken.** The SDK 14 compat gap in pipeline-core is latent (they're on SDK 13 and it works). No active bug requires a coordinated fix.
- **The datafactory migration is the current priority.** Engineering time is better spent completing the VIEWSER→datafactory transition (UNFAO historical data, remaining model migrations) than on infrastructure that isn't blocking anything.
- **The roadmap is durable.** This README serves as a ready-to-execute plan. When the trigger fires, Phase 1 can start immediately from this document without re-investigation.

### What to do instead right now

- **Keep this README as-is.** It's a good plan document. When the trigger fires, open it and start Phase 1.
- **Track the trigger conditions.** If someone proposes cloning faoapi for a new stakeholder, point them here first. If an SDK upgrade is discussed, check this document.
- **Don't let the copies drift further.** If you fix a bug in one Appwrite client, note whether the other copy has the same bug. If it does, fix both -- but don't use that as justification to extract the package immediately. Two coordinated fixes are cheaper than a premature extraction.
