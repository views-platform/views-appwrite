
# ADR-005: Testing as Mandatory Critical Infrastructure

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

`views-appwrite` is intended to become the single client through which the entire VIEWS
platform reads and writes forecast data to Appwrite. A defect here is not contained: it
propagates to every consumer (`views-pipeline-core`, `views-faoapi`, future World
Bank/UNHCR clones) on the next version bump. The failure modes that matter most are not
crashes but *quiet* ones — a swallowed upload, a stale cache served as fresh, an SDK-14
response misread as empty.

In such a package, failure is not limited to exceptions. It includes:
- silent semantic drift (e.g. `compat` mis-normalising an SDK response),
- misuse by well-intentioned consumers (passing metadata that later can't be filtered),
- over-trust in cached or "latest" results,
- brittle behavior across SDK 13 and SDK 14+.

Given this, testing is not a convenience. It is **critical infrastructure**. The roadmap
already designates the existing consumer test suites as *contract tests* that must keep
passing through the migration — codifying that intent here.

---

## Decision

This repository treats **testing as mandatory critical infrastructure**.

All non-trivial functionality **must be covered by tests**. Testing must explicitly
address adversarial behavior, realistic consumer use, and robustness under expected
operation. Tests are divided into three complementary categories — **none may substitute
for another**:

- 🟥 **Red team tests** (adversarial)
- 🟫 **Beige team tests** (realistic, neutral misuse)
- 🟩 **Green team tests** (supportive, resilience-oriented)

---

## Test Taxonomy

### 🟥 Red Team Tests — Adversarial Testing

Deliberately attempt to break or misuse the client by assuming hostile or worst-case
conditions.

- **Goal:** expose failure modes and unsafe behaviors
- **Mindset:** *“How could this go wrong?”*
- **Project-grounded focus (planned):**
  - Malformed or unexpected SDK responses fed to `compat._as_dict`/`_get`
  - Missing/contradictory `AppwriteConfig` fields (must fail loud, ADR-003)
  - `storage_bucket_not_found` and attribute-creation conflicts/races in `MetadataManager`
  - Corrupt or truncated downloads; auth failures

### 🟫 Beige Team Tests — Realistic, Neutral Usage

Focus on boring, realistic, non-adversarial consumer behavior that is still dangerous if
mishandled.

- **Goal:** catch failures caused by normal consumer behavior
- **Mindset:** *“What will a real consumer repo actually do?”*
- **Project-grounded focus (planned):**
  - A consumer uploads opaque metadata, then filters on a field it never set (`get_latest`/`search` returning nothing)
  - A consumer treats a cache hit as authoritative when the remote file changed (TTL/timestamp comparison in `CacheManager`)
  - The same code running against SDK 13 in one environment and SDK 14+ in another
  - Downloading bytes and deserializing with the wrong format (the package returns bytes; the consumer owns deserialization)

### 🟩 Green Team Tests — Supportive, Resilience-Oriented Testing

Ensure the system works as intended under expected conditions and degrades safely.

- **Goal:** ensure reliability and trustworthiness
- **Mindset:** *“How do we make this solid?”*
- **Project-grounded focus (planned):**
  - `compat` normalises SDK 13 dicts, SDK 14 Pydantic models, and `SimpleNamespace` identically
  - `CacheManager` respects TTL, detects stale timestamps, cleans up expired entries
  - `DatastoreManager.get_latest()` sorts by `$createdAt` descending and returns the first match
  - `AppwriteConfig.__post_init__()` normalises `auth_method` and derives default names
  - The live-lifecycle integration test (`test_integration.py`): create bucket → upload → search → download → cache-hit → update → delete → verify clean (skipped unless `APPWRITE_TEST_ENDPOINT` is set)

---

## Planned Test Layout

From the roadmap's "Testing Strategy" (no code exists yet):

- `tests/test_compat.py`, `tests/test_cache.py`, `tests/test_storage.py`, `tests/test_metadata.py`, `tests/test_datastore.py` — unit, SDK mocked, run in CI without credentials.
- `tests/test_integration.py` — live Appwrite, skipped in CI.
- **Contract tests during migration:** the existing consumer suites — `views-faoapi`'s `test_integration_appwrite.py`, `test_appwrite_manager.py`, `test_datastore_manager.py`, `test_sdk_compat.py`; `views-pipeline-core`'s `tests/test_modules/test_appwrite.py` — serve as drop-in-replacement verifiers. If they pass with `views-appwrite` as the backend, the migration is correct.

---

## Relationship to Other ADRs

- **ADR-001 (Ontology):** tests must respect declared categories and stability (e.g. never assume a metadata schema the package disclaims).
- **ADR-002 (Topology):** tests must not bypass architectural boundaries.
- **ADR-003 (Authority & Semantics):** tests must assert loud failure on missing config / ambiguous responses.
- **ADR-004 (Deferred):** future evolution rules must account for test coverage obligations.

---

## Enforcement Rules

- Code that meaningfully affects behavior **must not be merged without tests**.
- Happy-path-only coverage is insufficient.
- A known-but-untested failure mode is technical debt and must be tracked in the risk register (`reports/technical_risk_register.md`).

The absence of appropriate tests is valid grounds for blocking a change.

---

## Consequences

### Positive
- Reduced risk of silent failure propagating to all consumers
- Earlier detection of SDK-version and metadata-misuse issues
- The contract-test strategy makes the migration verifiable

### Negative
- Higher upfront development cost
- Slower iteration if tests are neglected

These costs are accepted intentionally.

---

## Notes

Testing here is about preventing *silent* harm in a dependency that many repos trust. Because no code exists yet, this ADR currently constrains the Phase 1 extraction rather than describing an existing suite.
