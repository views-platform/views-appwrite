
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

## Challenges and questions

Raised during review and kept here on purpose. **These are not decisions.** They change nothing above
them. Each entry records when it was raised, what prompted it, and what would settle it. An entry may
end in an amendment to this ADR, or in a recorded "looked at it, it is fine" — both are useful
outcomes and the second should be written down rather than left implicit.

### 2026-11-25 — The planned test strategy would import the cost structure that missed the defect this ADR names

**Raised by:** a multi-expert review of `views-faoapi` and `views-crafdapi` conducted on 2026-11-25
(`reports/2026-11-25_faoapi_crafdapi_review.md`), read back against this document. Quotations below
are from the chapter extract at
`~/Desktop/views_blueprints/reading/5_FreemanPryce_Ch08_building_on_third_party_code.pdf`, converted
to text and read during that review.

**What this ADR gets right, and should get credit for.** The Context section names the failure mode
that matters: *"a stale cache served as fresh."* **That is exactly the defect found in a consumer on
2026-11-25** — `views-faoapi#660`, in which the two routes the UN FAO actually download from serve a
cached artefact gated on file existence, cache schema version and TTL, but never on which forecast run
the file belongs to. This ADR anticipated the class of bug correctly, in June, before any of it
existed.

**The problem is the strategy proposed to catch it.** The "Planned Test Layout" section specifies five
unit test files with the **SDK mocked**, and then names `views-faoapi`'s `test_appwrite_manager.py`,
`test_sdk_compat.py`, `test_integration_appwrite.py` and `test_datastore_manager.py` as *"drop-in
replacement verifiers"*, on the reasoning that if they pass against this package the migration is
correct.

**Measured in those consumer suites on 2026-11-25. Fact, checked that day.** `views-faoapi` carries
29,171 lines of test against 14,855 lines of source — two lines of test per line of source. It
contains **261** `patch`/`Mock`/`MagicMock` call sites, 33 of them naming Appwrite.
`tests/test_appwrite_manager.py` is **1,447 lines** and `tests/test_sdk_compat.py` is **599 lines** —
2,046 lines whose subject is a vendor SDK pinned at an exact version, `appwrite==19.2.0`.

**And none of it caught #660.** The defect was found by a falsification audit of the claim "nothing in
this repository blocks running the pipeline", not by the suite. A test that mocks the store cannot
observe that the store moved on, because the mock is whatever the test said it was.

**What the literature says about precisely this.** Freeman & Pryce devote a section to it, titled
*"Only Mock Types That You Own"* and subtitled *"Don't Mock Types You Can't Change"*. Their diagnosis
is that the cost shows up in the tests and is then mistaken for thoroughness: *"tests that mock
external libraries often need to be complex to get the code into the right state for the functionality
we need to exercise. The mess in such tests is telling us that the design isn't right but, instead of
fixing the problem by improving the code, we have to carry the extra complexity in both code and
test."* They add the correctness objection separately: *"we have to be sure that the behavior we stub
or mock matches what the external library will actually do."*

Their prescription is an adapter layer, and the size constraint is the operative clause: *"We write a
layer of adapter objects ... We keep this layer as thin as possible, to minimize the amount of
potentially brittle and hard-to-test code. We test these adapters with focused integration tests to
confirm our understanding of how the third-party API works. There will be relatively few integration
tests compared to the number of unit tests."*

**Fact, checked 2026-11-25:** the adapter layer in `views-faoapi` — `src/views_faoapi/managers/appwrite/` —
is **2,421 lines**, and **Read** from `docs/boundary_tests.md` test 8, that repository performs
**three** store operations. The layer is not thin, and the integration tests are not few.

**Why this matters more here than there.** This ADR's own Context states the reason: *"A defect here is
not contained: it propagates to every consumer."* The same is true of a test strategy. If this package
adopts SDK mocking as its unit-test default and inherits 2,046 lines of vendor-mock suite as its
correctness criterion, then every consumer that migrates onto it inherits a suite that is large,
slow to change, pinned to one SDK version, and structurally unable to detect the staleness failure
this ADR was written to prevent.

**What would settle it.** Decide three things, none of which requires new code:

1. **Whether the package's own interface, or the Appwrite SDK, is what unit tests mock.** If the
   package publishes a store interface it owns, a fake implementing that interface is a type we own,
   and Freeman & Pryce's objection does not apply to it. If unit tests mock `appwrite.services.storage`,
   it does.
2. **Whether the inherited consumer suites are a migration *check* or a migration *target*.** Running
   them once to prove a drop-in replacement is cheap and useful. Adopting them as this package's
   permanent suite is the thing to refuse.
3. **What test would have caught `views-faoapi#660`**, and whether this package's layout contains it.
   The review's answer is a fake store holding two runs and an assertion that the second read does not
   return the first run's bytes. **That test needs an owned interface to exist at all**, which makes
   this question the same question as ADR-012's.

**What this does not settle.** Nothing above changes the three-colour taxonomy, the enforcement rules,
or the requirement that behaviour-affecting code ships with tests. The taxonomy is orthogonal to what
gets mocked. Red/beige/green survive this entry unchanged.

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
