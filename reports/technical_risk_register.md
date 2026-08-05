# Technical Risk Register

| Register Info     | Details                              |
|-------------------|--------------------------------------|
| Project           | views-appwrite                       |
| Owner             | Polichinl                            |
| Last Updated      | 2026-08-02                           |
| Total Concerns    | 45                                   |
| Open Concerns     | 40                                   |
| Resolved Concerns | 5                                    |
| Disagreements     | 5 (4 open, 1 resolved — D-02)        |
| Also hosts        | `PLATFORM-001` — the platform seam contract (`docs/ADRs/platform/`) |

---

## Tier Definitions

| Tier | Severity | Description |
|------|----------|-------------|
| 1 | Critical | Silent data corruption or model output correctness risk. Requires immediate attention. |
| 2 | High | Structural fragility that will cause failures under realistic change scenarios. |
| 3 | Medium | Maintainability or coupling issues that increase cost of change. |
| 4 | Low | Code quality concerns that do not affect correctness or reliability. |

---

## Causal Clusters

Added by `review-rr` strategic review (2026-06-12). Clusters group open concerns by shared root cause; fixing the root cause resolves — or fully specifies the fix for — every member entry. Membership reflects open entries only.

| Cluster | Root cause | Members | Highest tier | Fix strategy |
|---------|-----------|---------|--------------|--------------|
| A. Corpus freshness | External facts snapshotted in prose, never re-verified | C-09, C-17 (evidence also in C-03, C-05) | 2 | Reconcile roadmap with reality once upstream work settles; extend `validate_docs.sh` past `ADR-00[0-9]` |
| B. Unratified public contracts | Interfaces named but contracts never written (ADR-012/014 and CICs missing) | C-04, C-12, C-15, C-19, C-20, C-24, C-25 (+D-01, D-03) | 2 | One contract-writing session: ADR-012 (config schema), ADR-014 (exception taxonomy, envelope rules), `DatastoreManager` CIC |
| C. Inherited behavior vs fail-loud constitution | Source-repo behaviors conflict with ADR-003/008 | C-06, C-13, C-14 | 2 | **Doctrine settled 2026-07-28** (þing-01: ADR-008:38 amended, D-02 resolved, `PLATFORM-001` §6 ratified). Remaining work is *code-side and external* — the two client lineages ship raise-by-default; C-14's retry policy still needs ADR-014 |
| F. Platform seam contract — open items (new 2026-07-28) | The seam contract this repo now hosts names two hard problems it did not solve | C-27 (O1: secret-value rotation has no propagation mechanism), C-28 (O2: the FAO external-caller credential is unmodelled) | 2 | Not this repo's to fix: C-27 is an operator design task (issue #9), C-28 is views-faoapi + operator (faoapi #279). This repo tracks them because it hosts `PLATFORM-001` |
| D. Extraction inputs unsecured | Phase 1 inputs (source SHAs, divergence audit, source governance) uncaptured | C-03, C-05, C-07, C-16 | 2 | Divergence-audit artifact as the first act of Phase 1, when upstream settles |
| E. Scaffold mechanics unowned | No document owns sub-architectural setup decisions | C-02, C-18 (C-10 resolved 2026-07-28) | 3 | One scaffold session: `pyproject.toml`, CI workflow, ADR-numbering alignment. **Deferred by ratified decision** (`dómr_endurmat` E6, issue #8, trigger: operator ∧ test project) — the scaffold was priced against hosting the reference validator; the validator deferred, so the scaffold defers with it |

Standalone: C-01 (dissolves when the scaffold exists), C-21 (README instance closed 2026-07-28; pipeline-core's dataclass-defaults instance and the fixture guard remain), C-04's re-derived remainder, C-26 (external, operational).

**Note on Cluster E and D-04 (2026-07-28):** the þing briefly approved this repo's scaffold, then
**deferred it again** on adversarial review — the scaffold's justification was hosting the reference
validator, and when the validator deferred behind *operator ∧ test project*, its justification went
with it. So **C-02 and C-18's open half stay open, and D-04 stays unresolved**: they were priced
against hosting code, and no code is hosted. This repo reverts to its constitutional default —
parked, with one more recorded trigger.

---

## Open Concerns

### C-01: Roadmap repository may be mistaken for a shippable package

| Field | Value |
|-------|-------|
| ID | C-01 |
| Tier | 3 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When a consumer repo adds `views-appwrite @ git+...@v0.1.0` to its `pyproject.toml` dependencies, verify that the tag and package actually exist before relying on the import. |
| Location | `views-appwrite/` (entire repo: untracked `README.md`, `docs/`, `reports/`; 0 commits as of 2026-06-12) |

The repository contains only a 640-line `README.md` and has no commits, no `src/`, no `tests/`, and no `pyproject.toml`. Everything described under "Package Design" (`README.md:216-237`) is a plan, not code. The risk is that the roadmap's concrete install instructions (`pip install git+...@v0.1.0`, `README.md:326`) are read as already-published, and a consumer pins a dependency that cannot resolve. The failure is loud (install/import error) rather than silent, which is why this is Tier 3 rather than Tier 2. Currently mitigated only by the `Status: Planned` line (`README.md:5`) and the "hold until a trigger fires" recommendation (`README.md:616`).

---

### C-02: Package boundary invariants are prose contracts with no mechanical enforcement

| Field | Value |
|-------|-------|
| ID | C-02 |
| Tier | 3 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When the first code commit lands (Phase 1 scaffold), verify CI/lint enforces the "Appwrite-SDK-only dependency", "no domain logic", and "no `os.getenv`/`load_dotenv`" rules — not just the README prose. |
| Location | planned `pyproject.toml` and CI; rules stated at `README.md:106-119,255,322` |

The package's defining constraints — exactly one runtime dependency (`appwrite>=5.0.0`), zero VIEWS domain logic, and no environment-variable loading inside the package — are asserted only as prose in "What This Package Does NOT Contain" (`README.md:106-119`). The README's own R5 (`README.md:572`) identifies scope creep as "the most likely way this package fails long-term." Without an import-linter rule, a dependency allowlist in CI, or a grep gate for `os.getenv`, nothing prevents a future PR from adding pandas, a domain schema, or hidden `.env` coupling. This raises cost of change for every future maintainer. Currently mitigated by the prose contract and the Decision Log (D2–D4, `README.md:599-601`).

**Falsification evidence (2026-06-12, probe P3):** CI is *presupposed* five times in the corpus ("run in CI", "skipped in CI" — `README.md:236,491,525`, ADR-005:93-94) but specified zero times — no CI system, workflow content, lint configuration, or Python version matrix exists in any document, so this concern's own trigger cannot be satisfied from the docs as written. The gate must be authored, not transcribed. Enforced by failing stub `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_03_ci_gate_is_specified`.

---

### C-03: SDK 13→14 compatibility layer exists in only one of the two source copies

| Field | Value |
|-------|-------|
| ID | C-03 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When `views-pipeline-core` upgrades its Appwrite SDK to 14+, verify that `_as_dict()`/`_get()` normalisation is present on every SDK response access path before deploying. |
| Location | external: `views-pipeline-core/modules/appwrite/file.py` (SDK 13 only); compat asset at `views-faoapi/managers/appwrite.py:31-72`; documented at `README.md:463-485,624` |

The Appwrite SDK changed responses from plain `dict` (SDK 13) to Pydantic models (SDK 14+) (`README.md:467-471`). `views-faoapi` handles both via `_as_dict()`/`_get()`, but `views-pipeline-core` is SDK-13-only and lacks this layer (`README.md:473`). If pipeline-core upgrades to SDK 14+ before the extraction happens, dict-style access (`response["$id"]`) against Pydantic models breaks across pipeline-core's Appwrite paths. This is the README's own trigger #2 for starting the extraction (`README.md:624`) and the stated reason faoapi was chosen as the extraction base (roadmap Decision Log #1, `README.md:598`). Latent today because pipeline-core remains on SDK 13. Currently unmitigated except by not upgrading.

---

### C-04: `AppwriteConfig` field divergence will break call sites during extraction

| Field | Value |
|-------|-------|
| ID | C-04 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When defining `views_appwrite.client.AppwriteConfig`, diff the field sets of both source repos' configs and confirm the new dataclass is a superset; then update every `AppwriteConfig(...)` construction site to pass `cache_dir=` instead of `path_manager=`. |
| Location | external: `views-pipeline-core` (`AppwriteConfig` with `timeout_seconds`, `path_manager`), `views-faoapi` (`AppwriteConfig` with `timeout_seconds` + `connect_timeout_seconds`, `path_manager`); documented at `README.md:148-155,421-422,578-582` |

The two source repos define `AppwriteConfig` with different fields: pipeline-core has `timeout_seconds` but not `connect_timeout_seconds`; both pass a `path_manager: ModelPathManager` that the extracted package intends to replace with `cache_dir: Optional[Path]` (roadmap Decision Log #4, `README.md:601`). The new config must be a superset (`README.md:421`), and every construction site across at least three repos must change `path_manager=...` to `cache_dir=path_manager.cache / "appwrite"` (`README.md:383,422`). A missed call site fails at construction time (`TypeError`) — but the silent path is what grounds Tier 2: if the superset config quietly redefines a field's default or semantics between the two source variants (e.g. differing timeout defaults), consumers get changed runtime behavior with no error at all. This is structural fragility with a concrete migration trigger. The README proposes a transitional config accepting both fields (R6 mitigation, `README.md:582`) — not yet implemented.

**Falsification evidence (2026-06-12, probe P6):** the divergence already exists *inside this repository's own docs* — four partial, disagreeing field enumerations: `README.md:57` (has `auth_method`, cache TTL, timeout; omits `cache_dir`), the canonical example `README.md:268-276` (7 fields; omits `auth_method`, TTL, all timeouts), ADR-009:41 (adds `cache_dir`, plural "timeouts"), and `README.md:501` (derived `bucket_name`/`database_name` fields appearing in no list). No authoritative enumeration exists from which even a class stub could be written; candidate ADR-012 is the natural home. Enforced by failing stub `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_06_appwriteconfig_has_single_authoritative_field_list`.

---

### C-05: Duplicated Appwrite clients drift, and cloning faoapi adds further copies

| Field | Value |
|-------|-------|
| ID | C-05 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When a bug is fixed in one Appwrite client copy, check whether the other copy has the same bug; and when `views-faoapi` is cloned for a new consumer API (e.g. World Bank, UNHCR), confirm whether the clone copies the Appwrite client a third time. |
| Location | external: `views-pipeline-core/modules/appwrite/file.py` (~3,047 lines), `views-faoapi/managers/appwrite.py` (~2,000 lines); documented at `README.md:39-45,128-155,540-552,622-639` |

Two implementations of the Appwrite client (~5,000 lines total) are ~90% identical but have already diverged: the `_as_dict` SDK-14 guard exists only in faoapi, class names differ, and timeout config exists in only one (`README.md:39-45,148-155`). Continued independent evolution risks silent behavioural divergence in production (e.g. one copy auto-creates a missing bucket while the other raises, `README.md:550`) and widens the eventual extraction diff. Cloning `views-faoapi` for a new stakeholder API copies the client a third time — the README's strongest "start now" trigger (#1, `README.md:622`). Currently mitigated only by the manual discipline in the Datafactory note: "if you fix a bug in one copy, fix both" (`README.md:639`). Subsumes the clone-creates-3rd-copy finding (RA-8) as an additional trigger/location. **Drift confirmed live (falsification round 2, 2026-06-12):** `prediction.py` measured at 423 lines vs the roadmap's 383 (`README.md:142`) — ~10% growth in the eleven days since the roadmap was written.

---

### C-06: `AppwriteSaver` swallows all upload exceptions, hiding failures across the extraction

| Field | Value |
|-------|-------|
| ID | C-06 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When implementing `DatastoreManager.upload()` in `views-appwrite`, define and document specific exception types, and update pipeline-core's `AppwriteSaver` to catch those specific types rather than bare `Exception`. |
| Location | external: `views-pipeline-core/managers/prediction/savers.py` (`AppwriteSaver`); documented at `README.md:423,584-588` |

`AppwriteSaver` in pipeline-core deliberately catches all exceptions during upload and logs instead of raising (graceful degradation, tied to the README's reference to pipeline-core's own decision log #10 and that repo's external register entry C-50, `README.md:423`). The risk: if the extracted `DatastoreManager.upload()` changes the exception types or error codes it raises, the catch-all still swallows them but log messages shift, so silently-failed uploads (predictions not stored) become harder to diagnose (R7, `README.md:584-588`). This borders Tier 1 because a swallowed upload failure leaves downstream consumers reading stale data with no raised error; it is held at Tier 2 because a log signal does exist and the behaviour is an intentional, documented contract. The README itself flags catching specific types as the improvement (`README.md:588`).

---

### C-07: Phase 3 depends on coordination with the pipeline-core maintainer

| Field | Value |
|-------|-------|
| ID | C-07 |
| Tier | 4 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When Phase 3 (migrate `views-pipeline-core`) is scheduled, confirm the pipeline-core maintainer has agreed to take the inbound `views-appwrite` dependency before starting the import-path migration. |
| Location | organizational; `views-pipeline-core` repo; documented at `README.md:385-389,560-564,602` |

Migrating `views-pipeline-core` to depend on `views-appwrite` requires buy-in from a different maintainer who may prefer to keep their own copy (R3, `README.md:560-564`). This is a coordination/process risk rather than a code-quality defect, so it is registered at Tier 4. It does not block the rest of the plan: the README notes consumer APIs can adopt `views-appwrite` regardless, and pipeline-core can migrate later (`README.md:564`). Currently mitigated by the documented framing strategy (present as a benefit: free SDK-14 compat, fewer lines to maintain).

---

### C-09: `validate_docs.sh` cannot see ADR-010+ references and skips Deferred-status files

| Field | Value |
|-------|-------|
| ID | C-09 |
| Tier | 4 |
| Source | repo-assimilation (2026-06-12) |
| Trigger | When the first project-specific ADR (011+) is written, or when ADR-004 is activated out of Deferred status, extend the script's reference pattern beyond `ADR-00[0-9]` and include Deferred files in the placeholder scan before trusting a green run. |
| Location | `docs/validate_docs.sh:60` (pattern `ADR-00\K[0-9]`), `docs/validate_docs.sh:36` (Status filter excludes `Deferred`), `docs/validate_docs.sh:24-35` (placeholder checks) |

The script was inherited from the base_docs template when only constitutional ADRs (000–009) existed. ADR-010 now exists and is referenced from `reports/technical_risk_register.md:144` and `docs/ADRs/README.md:32`, but the cross-reference check at `validate_docs.sh:60` only matches `ADR-00[0-9]`, so a phantom reference to ADR-010 — or to any of the candidate ADRs 011–015 anticipated in `docs/ADRs/README.md` — passes validation silently. The placeholder scan likewise only examines files whose Status is Accepted/Active, excluding the Deferred ADR-004. The failure mode is a false "PASSED" from the repository's only mechanical documentation gate. Currently mitigated only by manual review of cross-references.

See also C-02 (shared root cause: invariants asserted in prose with incomplete mechanical enforcement).

---

### C-10: ADR numbering scheme is stated inconsistently across three documents

| Field | Value |
|-------|-------|
| ID | C-10 |
| Tier | 4 |
| Source | repo-assimilation (2026-06-12) |
| Trigger | When the next ADR is authored, confirm which scheme governs (010+ project-specific vs 010 governance / 011+ project-specific) and align ADR-000, `docs/ADRs/README.md`, and ADR-010 before assigning the number. |
| Location | `docs/ADRs/000_use_of_adrs.md:44` ("constitutional 000–009; project-specific 010+"), `docs/ADRs/README.md:9-13` (three tiers: 010 = governance, 011+ = project-specific), `docs/ADRs/010_technical_risk_register.md:73` ("project-specific ADRs (010+)") |

ADR-000 and ADR-010 both describe 010+ as the project-specific range, while `docs/ADRs/README.md` introduces a three-tier scheme in which 010 is a distinct Governance tier and project-specific numbering starts at 011. The number 010 is already occupied by the risk-register ADR, so an author following ADR-000 literally would collide with it or misclassify the new ADR. Pure documentation drift with no correctness impact, but it sits in the artifact set whose stated purpose is preventing silent inconsistency.

**Resolved (2026-07-28, þing-01 / issue #3):** the three-tier scheme adopted (constitutional 000–009; governance 010; project-specific 011+); `ADR-000:44` and `ADR-010:73` amended to match `docs/ADRs/README.md`. A fourth, prefixed cross-repo tier (`docs/ADRs/platform/`, `PLATFORM-NNN`) established for platform-seam contracts, so the seam ADR's identifier is unambiguous when cited from other repos — discharging þing-01 sáttmál S16(ii).

---

### C-12: `upload()`/`delete()` are non-atomic two-write operations with no partial-failure semantics

| Field | Value |
|-------|-------|
| ID | C-12 |
| Tier | 2 |
| Source | expert-review (2026-06-12) |
| Trigger | When implementing `DatastoreManager.upload()` and `delete()`, define the write order (file-first vs metadata-first), partial-failure behavior, and orphan handling in the `DatastoreManager` CIC before writing the methods. |
| Location | planned `src/views_appwrite/datastore.py`; interface at `README.md:92-98`; danger named but unspecified in ADR-008 (Context: "a metadata write that partially succeeds") |

`upload()` performs two separate Appwrite writes — file to storage, then a metadata document — and `delete()` the inverse. A failure between them leaves either an orphaned file invisible to `search()`/`get_latest()` (consumers silently read older "latest" data) or, with the reverse order, metadata pointing at a nonexistent file. ADR-008 explicitly names partial metadata writes as a key danger, but no document specifies ordering, compensation, or reconciliation. Tier 2 (bordering 1) because the orphaned-file case produces stale downstream reads with no error signal; held at 2 because a `list_all()`-based reconciliation can detect it and the failure requires a mid-operation fault. No mitigation currently exists.

**Update (2026-07-28, þing-01 / issue #6) — status changes from *anticipated* to *OBSERVED*.**
This entry was registered on 2026-06-12 as a design hazard about code that did not exist. þing-01
produced the incident. On run-0 (2026-07-27), views-postprocessing's delivery wrote a file to
`unfao_bucket` whose metadata document was **rejected for exceeding the 255-character `description`
limit**; the store **logged the failure and reported success upward** (orð_09 §3). That is exactly
this entry's first failure mode — an orphaned file invisible to `search()`/`get_latest()`, with no
error signal — realised in production, on the first real delivery, without anyone having to
contrive it.

Three consequences. **(1) The predicted mechanism is confirmed**, including the part that made it
Tier 2: the failure was *silent upward*, so the caller believed the write succeeded.
**(2) A consumer-side partial mitigation now exists** — views-postprocessing's PR #132 raises on
partial success at its upload port — which narrows but does not close the entry, since the
mitigation lives in one consumer rather than in the shared write path. **(3) The fix is now named
and ratified:** *a half-succeeded write must raise* (ADR-008 §1 as amended 2026-07-28;
`PLATFORM-001` §6). The entry stays **open at Tier 2** because the ordering/compensation semantics
this repo owes — write order, orphan reconciliation, what `OperationResult` reports on partial
failure — are still unwritten and belong in the `DatastoreManager` CIC (C-20) before any method
body exists.

See also C-06 (the consumer-side catch-all that would mask the partial failure), C-20 (the return
contract that must encode partial-failure semantics), and D-02 (resolved — the doctrinal half).

---

### C-13: Bucket auto-creation converts a typo'd `bucket_id` into silent data divergence

| Field | Value |
|-------|-------|
| ID | C-13 |
| Tier | 2 |
| Source | expert-review (2026-06-12) |
| Trigger | When defining `AppwriteConfig` and `StorageManager`'s missing-bucket behavior, make auto-provisioning an explicit opt-in (default: raise a documented exception) and add a red-team test for the misconfigured-`bucket_id` path. |
| Location | `README.md:66,550` (auto-create on missing bucket); ~~ADR-008:38 (blesses auto-create)~~ — **amended 2026-07-28, no longer blesses it**; live exposure now external: views-faoapi `create_*` helpers, views-pipeline-core `datastore.py:350` + the `upload_file_with_metadata` provisioning chain |

The planned behavior auto-creates a bucket on first upload when it does not exist. A consumer with a typo'd `bucket_id` therefore silently provisions a new empty bucket and uploads into it successfully, while readers of the intended bucket see stale data indefinitely — no error is raised anywhere in the system. This contradicts the fail-loud constitution (ADR-003) for the misconfiguration case, even though ADR-008 currently blesses auto-create as "explicit, documented behavior." Tier 2 because it is structural fragility with a concrete, realistic trigger (one wrong character in config) producing a silent wrong-data outcome. Currently unmitigated; the documented behavior actively enables it.

**Update (2026-07-28, þing-01 / issue #5):** the *doctrinal* half is closed — D-02 resolved,
ADR-008:38 amended to raise-by-default, and the rule ratified platform-wide at `PLATFORM-001` §6
("a wrong or missing coordinate raises, naming the offending coordinate"). Two things sharpened the
entry rather than closing it. **(1) It is no longer hypothetical:** þing-01 sáttmál S8 (amended)
established from code on disk that *both* live client lineages provision-on-miss on their write
paths, so the typo→phantom-bucket path is real today, not merely planned. **(2) The exposure moved
out of this repo:** nothing here can fix it, because nothing here runs. C-13 therefore stays **open
at Tier 2** as the tracking entry for the two external lineages' fixes, and closes when both have
shipped raise-by-default *and* declared it per the drill ordering (amend → ship → drill the raise
path → test project → drill the provisioning path). See also D-02 (resolved) and PLATFORM-001 §6.

---

### C-14: No retry policy defined; shared client amplifies retries into platform-wide storms

| Field | Value |
|-------|-------|
| ID | C-14 |
| Tier | 3 |
| Source | expert-review (2026-06-12) |
| Trigger | When implementing any retry loop (the `MetadataManager` database/collection auto-creation retries, or transient SDK error handling), ratify a retry policy first: bounded attempts, exponential backoff with jitter, and an explicit retryable-error-code list. |
| Location | `README.md:73` ("auto-creation with retry logic" — no policy), planned `metadata.py`/`storage.py` |

The roadmap mentions retry logic but no document specifies attempt counts, backoff, jitter, or which error codes are retryable. Because every platform consumer (`views-pipeline-core`, `views-faoapi`, future clones) will run this same client, an Appwrite brownout plus naive synchronized retries becomes a coordinated retry storm against the shared endpoint, prolonging the outage and risking platform-wide rate limiting. Tier 3: affects all consumers (multiple developers) but degrades loudly rather than corrupting data. Mitigated only by the fact that no retry code exists yet to get wrong.

---

### C-15: `OperationResult.code` passthrough would re-couple consumers to SDK error semantics

| Field | Value |
|-------|-------|
| ID | C-15 |
| Tier | 3 |
| Source | expert-review (2026-06-12) |
| Trigger | When defining `OperationResult` in `client.py`, decide whether `code` carries package-owned vocabulary or raw Appwrite SDK codes; if package-owned, relegate the raw SDK code to a debug/diagnostic field. |
| Location | `README.md:59` (`OperationResult{success, data, error, code}`), ADR-009 §1 (envelope contract) |

Both source repos pass Appwrite SDK error codes through their result envelopes today. If the extracted `OperationResult.code` does the same, consumers will branch on Appwrite-specific codes, re-coupling every consumer to SDK semantics through the very envelope meant to insulate them — and an SDK upgrade that changes codes silently misroutes consumer error handling with no package-side signal. Tier 3: a coupling/cost-of-change issue across all consumers; becomes correctness-relevant only after an SDK code change. Unmitigated; the roadmap does not address `code`'s vocabulary.

See also C-03 (the same SDK-version coupling surfacing through a different channel).

---

### C-16: Extraction sources are unpinned and the R1 divergence audit has not been produced

| Field | Value |
|-------|-------|
| ID | C-16 |
| Tier | 2 |
| Source | expert-review (2026-06-12) |
| Trigger | Before decomposing any source file in Phase 1, record the exact commit SHAs of `views-faoapi/managers/appwrite.py` and `views-pipeline-core/modules/appwrite/file.py` being extracted, and commit the R1 public-method diff as an artifact (e.g. `docs/extraction/divergence_audit.md`). |
| Location | `README.md:309` (extraction base), `README.md:552` (R1 mitigation: "Before extracting, write a diff of the two files' public methods"), `docs/contributor_protocols/silicon_based_agents.md:80-105` (anti-truncation rule lacking a reference snapshot to diff against) |

The roadmap's own R1 mitigation — a public-method diff of the two source files settling every divergence explicitly — has not been executed; the divergence table (`README.md:544-552`) covers only five known divergences and the "~90% identical" claim is unverified from this repository. No source commit SHAs are recorded anywhere, so the extraction target is a moving file in a live repo: an upstream fix landing mid-extraction would silently diverge from the copy being decomposed, and the silicon-agent anti-truncation review has no immutable origin to diff modules against. Tier 2: structural fragility of the extraction itself, with contract tests catching behavioral loss only where consumer suites happen to have coverage. Currently mitigated only by the contract-test strategy (ADR-005).

**Falsification round-2 evidence (2026-06-12, probe P1):** the unconsumed extraction inputs include *governance*, not just code. The source repos carry intent contracts for the very classes being extracted — faoapi `docs/CICs/AppWriteFileManager.md` and `PredictionStoreManager.md`; pipeline-core `documentation/CICs/AppWriteFileModule.md` and `DatastoreModule.md` — plus ≥19 faoapi ADRs and a faoapi risk register with ≥23 entries, none referenced by the roadmap. The Phase-1 plan to author views-appwrite's CICs from scratch (ADR-006 Notes) ignores four existing contracts that should seed them. The divergence audit should therefore cover both code *and* the source repos' ADR/CIC/register corpus.

See also C-05 (ongoing drift between the copies; this entry covers the extraction-process exposure).

---

**Re-derivation (2026-07-28, þing-01 / issue #6) — the premise was stale; the mechanism survives and
sharpens.** views-pipeline-core gave direct testimony on its own config object (orð_08 §1, settled as
sáttmál S24), checked against code on disk. It replaces two of this entry's factual claims.

**(a) The timeout premise is retired — and what replaces it is worse.** This entry asserted that
pipeline-core "has `timeout_seconds` but not `connect_timeout_seconds`." False: a full-text search of
both client modules returns **zero hits for `timeout`**. `AppwriteConfig` (`file.py:218-296`) has **no
timeout field of any kind**, so every Appwrite call rides the SDK's transport defaults. The
divergence is not *mismatched* fields — it is **one side having no deadline at all**. This does not
weaken C-04, it sharpens its Tier-2 grounding: the silent path was never the constructor `TypeError`
but *"the superset config quietly redefines a field's semantics."* Under the true premise, a superset
that adds timeouts **introduces a deadline where none existed** — calls that today hang forever begin
to fail — arriving as a behaviour change wearing a field addition's costume, in a version bump.
The *operational* half of that fact (pipeline-core has no deadline on any Appwrite call **today**,
independent of any merge) is not a field-divergence risk and would be buried here; it is split out
as **C-26**.

**(b) `path_manager` is confirmed live, and R6 is misclassified.** Live at `file.py:286` as
`path_manager: ModelPathManager = None` — annotated non-Optional yet defaulted `None`, *the
annotation lies* — doing three jobs, with a commented-out type check at `file.py:1621` fossilising
the author's own doubt. The roadmap's **R6** (`README.md:578-582`) calls the `path_manager`→
`cache_dir` migration *"a mechanical change."* That is now demonstrably wrong. Cache-dir resolution
(`file.py:1654`) is mechanical. **Metadata name-injection is not:** `datastore.py:392-393` auto-adds
`filters["name"] = model_path.model_name` to metadata queries, and the only escape is attribute
surgery on a live object (`datastore.model_path = None`) — the manoeuvre that snagged the `un_fao`
contract read during run-0. Removing `path_manager` therefore **removes behaviour consumers depend on
or work around**, silently, at the query layer. **R6 is re-recorded as having a mechanical half and a
semantic half**, and the semantic half is a migration blocker requiring its own contract clause.

**(c) What the þing dissolved.** With `PLATFORM-001` §4's registry supplying coordinates and §7's
in-process preflights validating them at entry, the field-merge risk **shrinks to behavioural fields
only** — connection and target fields stop being a merge question because neither config *originates*
them any more. C-04 is therefore **half-answered**: the field-set question is closed, the coordinate
half is superseded by the registry, and what remains open is the semantic merge of behavioural fields
plus (b)'s name-injection blocker. **Tier stays 2.** Cross-refs: **C-26** (the no-deadline fact),
`PLATFORM-001` §3-§4.

---

### C-17: Documented SDK pin contradicts both the compat narrative and PyPI reality (SDK is at major 20)

| Field | Value |
|-------|-------|
| ID | C-17 |
| Tier | 2 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When writing the scaffold `pyproject.toml` dependency pin, verify the floor against the compat layer's actual coverage (SDK 13+) and test against the current PyPI major (20.x as of 2026-06-12) before tagging `v0.1.0`; update `README.md:244` and the SDK Compatibility section (`README.md:463-485`) to match reality. |
| Location | `README.md:244` (`appwrite>=5.0.0`), `README.md:463-485` (compat narrative covering SDK 13/14+ only); evidence: PyPI `appwrite` releases span majors 0–20, latest 20.1.0 |

The roadmap's single runtime dependency line is materially wrong in two directions. The pin `appwrite>=5.0.0` admits majors 5–12, which predate the entire SDK-13/14 compat narrative and whose APIs the design never considers; and it resolves today to major 20 — six majors past the narrative's frontier (15–20 all unexamined). A scaffolder copying the documented pin verbatim, as the docs intend, installs an SDK version the compat layer (`_as_dict`/`_get`, designed against the 13→14 dict-to-Pydantic break) has never been evaluated against. The roadmap (dated 2026-06-01) described a dependency landscape that did not exist even when written. Tier 2: structural fragility with a concrete trigger — the first `pip install` of the scaffolded package resolves to an unconsidered major, and any breakage in compat normalisation surfaces as misread responses, not necessarily as loud errors. Enforced by failing stub `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_02_sdk_pin_consistent_with_compat_narrative`.

**Falsification round-2 evidence (2026-06-12, probe P1):** the contradiction is worse than staleness — `views-faoapi` ratified **ADR-019 (Accepted 2026-05-29, three days before this roadmap was written)** pinning `appwrite==19.2.0` *exactly*, after discovering its declared pin (`==13.3.0`) had silently diverged from its runtime (19.2.0). ADR-019 also documents that SDK 19.2.0 **deprecates `databases.list_documents()`** — used at 5 call sites in the code slated for extraction into `MetadataManager` — with tripwire tests already present in faoapi's `test_sdk_compat.py`. The roadmap's broad-pin strategy (`>=5.0.0`) therefore contradicts the extraction source's own accepted governance, and a known, tested-for deprecation hazard in the to-be-extracted code is absent from the migration plan entirely. Candidate ADR-011 (SDK strategy) must reconcile with faoapi ADR-019, not just with PyPI. Additional enforcing stub: `tests/test_falsification_enough_info_orthogonal.py::test_falsify_r2_01_roadmap_consumed_source_repo_sdk_decision`.

**Update (2026-06-12):** a staleness banner now marks the README SDK Compatibility section (acknowledging SDK major 20, faoapi ADR-019, and the `list_documents` deprecation) and Decision Log #7 is flagged stale. Full reconciliation deferred until in-flight work on adjacent repos settles; this entry stays open until the pin and narrative are actually rewritten.

See also C-03 (same SDK-version asymmetry in the source repos) and C-15 (SDK semantics leaking through the result envelope). Part of the corpus-freshness pattern with C-09.

---

### C-18: No license, Python version floor, or `.gitignore` decision exists anywhere in the corpus

| Field | Value |
|-------|-------|
| ID | C-18 |
| Tier | 3 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When creating the Phase 1 scaffold commit, decide the license, `requires-python` floor, and `.gitignore` content explicitly (or record an explicit deferral in the README Decision Log) before tagging `v0.1.0` for consumer installation. |
| Location | entire corpus (grep for license/`requires-python`/gitignore returns zero specification hits); demonstrated by dry-run build producing `views_appwrite-0.1.0-py2.py3-none-any.whl` |

Zero mentions of a software license, a supported Python version range, or `.gitignore` content exist in the documentation, and none is explicitly scoped out. (**Update 2026-06-12:** the `.gitignore` half self-demonstrated — commit `1e54734` accidentally swept `tests/__pycache__/*.pyc` into history; a minimal `.gitignore` was added immediately after. License and `requires-python` remain open for the scaffold session.) The falsification dry-run (probe P1) built a wheel from documented values only: it succeeded, but the artifact was tagged `py2.py3-none-any` — with no Python floor specifiable, the package silently claims Python 2 compatibility, a wrong-by-default installability claim that surfaces as confusing downstream failures rather than a clean resolver error. For an org-distributed, pip-installable package (`README.md:326-328`), the missing license decision is reviewer-blocking. Tier 3: affects every consumer repo and contributor but fails loudly-ish at review/install time rather than corrupting data. Enforced by failing stubs `test_falsify_01_scaffold_buildable_without_invented_values` and `test_falsify_05_license_and_python_floor_decided`.

---

### C-19: Public API surface contradiction — `_as_dict`/`_get` are simultaneously internal and a documented consumer import

| Field | Value |
|-------|-------|
| ID | C-19 |
| Tier | 3 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When writing `__init__.py` and naming the compat functions during the Phase 1 decomposition, resolve whether `_as_dict`/`_get` are public API (rename without the underscore prefix and export them) or internal (give consumers a public wrapper); update `README.md:382` and the Phase 2 migration instructions accordingly. |
| Location | `README.md:222,261-265` (3-name public surface, "Everything else is internal"), `README.md:382` (Phase 2: consumers "must" import `_as_dict`/`_get` from `views_appwrite.compat`); ADR-001 Category 4 (compat's public effect is dicts, implying no direct consumer access) |

The package design declares exactly three public names (`AppwriteConfig`, `DatastoreManager`, `OperationResult`) with everything else internal — yet the Phase 2 migration plan instructs `views-faoapi` to import the underscore-prefixed `_as_dict()`/`_get()` directly from `views_appwrite.compat`, making private-by-convention names load-bearing consumer API. The scaffolder cannot write `__init__.py`, choose compat naming, or apply semver guarantees (deferred ADR-004 activates at `v0.1.0`) without resolving this contradiction, and ADR-003 forbids resolving it by guessing. Tier 3: an API-design ambiguity propagating into at least one consumer repo's migration; no silent correctness impact. Enforced by failing stub `test_falsify_04_public_surface_internally_consistent`.

See also C-15 (the envelope side of the same public-surface question) and D-01 (module granularity, which a compat-surface decision feeds into).

---

### C-20: Facade method return contracts are unspecified — three of six methods cannot be written without guessing

| Field | Value |
|-------|-------|
| ID | C-20 |
| Tier | 3 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When writing the `DatastoreManager` CIC (first Phase-1 contract per ADR-006), specify each of the six methods' parameters, `OperationResult.data` shape, and error behavior — before any method body is written. |
| Location | `README.md:92-98` (six-method interface), `README.md:255-257` (`download` dual-mode, `"file_bytes"` key mentioned once), `README.md:365-366` (Phase-2 example: `get_latest_file_id` returns `get_latest()` output unmodified) |

The return contracts of `get_latest()`, `search()`, and `list_all()` are specified nowhere — file ID, metadata document, or some `OperationResult.data` shape is undeterminable from the corpus; `upload()`'s result payload is likewise unstated, and `download()` is dual-mode (bytes vs write-to-path) with its data key named once in passing. The roadmap's own Phase-2 migration example does not know the answer: a consumer wrapper named `get_latest_file_id` passes through `get_latest()`'s return value unchanged. Until these contracts exist, neither the facade nor the consumer wrappers nor their tests can be written without guessing, which ADR-003 forbids. Tier 3: blocks correct implementation across package and consumer repos; no silent-corruption path until code exists. Enforced by failing stub `tests/test_falsification_enough_info_orthogonal.py::test_falsify_r2_02_facade_return_contracts_specified`.

See also C-12 (the partial-failure semantics these contracts must include) and C-15 (the `code` vocabulary inside the same envelope).

---

### C-21: Integration-test isolation is unspecified — the only documented endpoint points destructive tests at production

| Field | Value |
|-------|-------|
| ID | C-21 |
| Tier | 2 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When writing `tests/test_integration.py` (or its documentation) in Phase 1, state explicitly that `APPWRITE_TEST_ENDPOINT` must reference a dedicated test project — never the production project — and validate that constraint in the test fixture (e.g. refuse to run against the documented production project ID). |
| Location | `README.md:512-525` (lifecycle: create bucket → … → delete, gated only on `APPWRITE_TEST_ENDPOINT` being set), `README.md:269-270` (the only concrete endpoint+project_id in the corpus: `fra.cloud.appwrite.io`, project `691b14fc0024f568fb42`), ADR-005:85 |

The documented live integration lifecycle creates and deletes buckets and files, and is gated solely on an environment variable being set — no document states what that variable must point at, and the only concrete endpoint/project pair appearing anywhere in the corpus is the production-looking one used in the config example. A developer following the docs ("run manually before releases") who sets the variable to the only value the docs ever show points bucket-creation and deletion operations at the production Appwrite project. Tier 2: destructive operations against production data under a realistic, docs-suggested action; the skip-by-default gate protects only the inaction path. Enforced by stub `tests/test_falsification_enough_info_orthogonal.py::test_falsify_r2_03_integration_test_isolation_specified`.

**Update (2026-06-12):** the isolation rule is now stated in the README Testing Strategy (stub green); the fixture-level guard (refuse to run against the production project ID) remains pending Phase 1, so this entry stays open at reduced exposure.

**Amendment (2026-07-28, þing-01 / issue #6) — generalised to a hazard class, and one instance
closed.** This entry described a single artifact (a copyable README example). þing-01 showed it is
an instance of a recurring pattern, now named:

> **Hazard class: *production coordinates reachable without a deliberate choice*.**

Two recorded instances, with different vectors and different severities:

| # | Instance | Vector | Status |
|---|---|---|---|
| i | this repo's `README.md` config example carried the live endpoint + project id | requires a human to **copy** it | **CLOSED 2026-07-28** — replaced with placeholders pointing at `coordinate_registry.toml` |
| ii | `views-pipeline-core`'s `AppwriteConfig` dataclass **defaults** (`bucket_id = "production_forecasts"`, `file.py:276` ff.) | applies when a caller **omits** the field | open; owner committed to stripping them (orð_08 §1, its ledger row C3) |

Instance (ii) is strictly the more dangerous of the two, and the distinction is worth keeping
because it orders the fix: **a copyable example needs a human to choose wrongly; a silent default
needs a human to choose nothing at all.** There is no moment at which anyone decides.

**The structural fix for the whole class is `PLATFORM-001` §4:** one owned, versioned registry is
where coordinates come from, so neither an example nor a default is ever where anyone learns a
bucket id. Every seat's copy-chain scar traced to the same absence.

**This entry stays open**, now tracking two things rather than the (closed) example: (1) instance
(ii) until pipeline-core strips its defaults; (2) **the fixture-level guard** — a test fixture that
refuses to run against the production project id — deferred with the scaffold (issue #8, trigger:
operator ∧ test project). Note that `PLATFORM-001` §7 now **forbids integration tests against the
production project outright** until a test project exists, which lowers the exposure to
documentation-only but does not substitute for the guard: a prohibition in prose is not a fixture
that refuses. Cross-refs: `PLATFORM-001` §4/§7, C-01, issue #8.

---

### C-24: `get_latest()` resolves "latest" by server clock — concurrent uploads make the result silently ambiguous

| Field | Value |
|-------|-------|
| ID | C-24 |
| Tier | 3 |
| Source | expert-review (2026-06-12) |
| Trigger | When implementing `DatastoreManager.get_latest()`, document the ordering semantics (server-assigned `$createdAt`, its resolution, tie behavior) in the `DatastoreManager` CIC, steer consumers toward consumer-owned recency metadata where ordering matters, and add a beige-team test for two uploads landing within the same timestamp resolution. |
| Location | `README.md:500` (`get_latest()` sorts by `$createdAt` descending, returns first match), `README.md:96` (facade interface); ADR-005 beige-team list (does not currently include this case) |

"Latest" is defined by Appwrite's server-assigned creation timestamp, not by any pipeline-semantic ordering. Two uploads from the same forecast run (or a retry racing its original) can interleave within clock resolution, after which `get_latest()` returns whichever document the server stamped later — silently, with no error and no tie signal. A consumer serving forecasts would read the wrong file while everything reports success. Tier 3 rather than 2 because the scenario requires near-simultaneous writes to the same filter set and the fix is a documented contract plus consumer guidance, not a structural redesign; it borders Tier 2 if retry logic (C-14) ever re-uploads automatically. Surfaced in the expert review (Kleppmann perspective and Long-Term Regret #5) but not previously registered.

See also C-12 (partial-failure orphans interact with "latest" selection), C-14 (retries create exactly the racing writes this needs), and C-20 (the return contract that must encode these semantics).

---

### C-25: Planned `FileMetadata` class duplicates the opaque metadata payload's role with no stated job

| Field | Value |
|-------|-------|
| ID | C-25 |
| Tier | 4 |
| Source | expert-review (2026-06-12) |
| Trigger | When implementing `metadata.py` in Phase 1, decide whether `FileMetadata` exists at all: either give it a stated responsibility distinct from the opaque `Dict[str, Any]` payload, or remove it from the plan (and from ADR-001 Category 8). |
| Location | `README.md:225` (`metadata.py # MetadataManager, FileMetadata`), `README.md:143` ("`FileMetadata` (generic, no domain fields)"), ADR-001 Category 8 (lists both `FileMetadata` and the opaque dict as Metadata Value entities) |

The design's metadata contract is an opaque `Dict[str, Any]` passed through unmodified (Decision D-3) — yet the plan also retains a generic `FileMetadata` class with no domain fields and no described purpose. Two representations of the same concept with no stated division of labor is precisely what ADR-001's non-entity clause forbids ("objects that mix or duplicate ontological roles"), and the class invites exactly the field-accretion drift (C-05 history) that motivated the opaque-dict decision. Tier 4: a design-clarity issue resolvable by one decision before any code depends on it. Surfaced in the expert review (GoF and Hickey perspectives) but not previously registered.

See also D-01 (module granularity) and C-04 (the config-side analogue of competing partial specifications).

---

### C-26: No timeout or deadline exists on any `views-pipeline-core` Appwrite call

| Field | Value |
|-------|-------|
| ID | C-26 |
| Tier | 3 |
| Source | þing-01 / orð_08 §1 (views-pipeline-core þingmaðr testimony), settled as sáttmál S24(a) (2026-07-28) |
| Trigger | When any timeout field is introduced into either source config — or into the extracted `AppwriteConfig` — treat it as a **behaviour change, not a field addition**: enumerate the call paths that currently rely on unbounded waits, and drill the hang path before declaring the change done. |
| Location | external: `views-pipeline-core/modules/appwrite/file.py` (`AppwriteConfig`, lines 218-296 — no `timeout` symbol anywhere in the module), `modules/datastore/datastore.py`; every Appwrite HTTP call made through them |

A full-text search of both pipeline-core client modules returns **zero hits for `timeout`**: the
config object has no timeout field of any kind, so every Appwrite HTTP call rides the SDK's
transport defaults — and the underlying `requests` default is **no timeout at all**. A hung Appwrite
call inside a delivery therefore has **no deadline**: it does not fail, it waits, and the pipeline
stage holding it waits with it.

This is split out of **C-04** deliberately. C-04 is about *merging two config objects*; this is a
live property of one of them today, independent of whether extraction ever happens, and folding it
into a migration-risk entry would bury an operational exposure inside a planning concern. Tier 3
rather than 2: it degrades loudly (a stuck run is visible, if slowly) rather than corrupting data,
and no incident has yet been attributed to it. It borders Tier 2 in combination with **C-14** (no
retry policy) — an unbounded wait plus naive retries is the shape of a coordinated stall against a
shared endpoint.

Registered here because the config merge is this repo's problem; **views-pipeline-core is registering
its own instance** (its ledger row C4), since the exposure is live in its runtime now and does not
wait for extraction. Cross-refs: C-04 (re-derivation §(a)), C-14.

---

### C-27: Rotating a secret *value* has no propagation mechanism (PLATFORM-001 open item O1)

| Field | Value |
|-------|-------|
| ID | C-27 |
| Tier | 2 |
| Source | þing-01 adversarial re-weighing (`rýni`), ruled in `dómr_endurmat` E7-O1 (2026-07-28) |
| Trigger | Before the first key reissuance under the three-tier model (`PLATFORM-001` §5), design the propagation path — secret store, injection at launch, or per-process slots — or the cutover is manual multi-environment surgery performed under time pressure. |
| Location | `docs/ADRs/platform/appwrite_seam_contract.md` §9 (O1); the registry carries secret **slots**, never values |

The contract this repo now hosts moves *coordinates* out of the copy-chain into an owned registry —
but the **key value** remains fanned into every process environment by copy and borrow (þing-01
S22: one physical key, propagated). `PLATFORM-001` §5 names the operator as rotation owner, which
assigns a responsibility while designing **no mechanism**. A first real rotation today is manual
surgery across every environment that holds a copy, with no way to verify completeness — and the
failure mode of an incomplete rotation is a process authenticating with a revoked key, which fails
loudly, or worse, a process still holding a key that was meant to be revoked, which fails not at all.

Recorded at Tier 2 on this register because `PLATFORM-001` §9 assigns O1 to *"the seam-home
register"* and this repo is the seam home. **This repo cannot fix it** — it is an operator design
task (issue #9) plus a small mechanism decision the þing deliberately declined to pre-judge. Until
it closes, `PLATFORM-001` §5 declares rotation **manual and operator-coordinated** rather than
pretended-solved. Cross-ref: C-28 (the same gap at its highest-stakes instance).

---

### C-28: The FAO external-caller credential is unmodelled (PLATFORM-001 open item O2)

| Field | Value |
|-------|-------|
| ID | C-28 |
| Tier | 2 |
| Source | þing-01 adversarial re-weighing (`rýni`), ruled in `dómr_endurmat` E7-O2 (2026-07-28) |
| Trigger | Before any additional external party (World Bank, UNHCR, or a second FAO consumer) is issued a key, settle: who issues, at what scope, with what rotation story — and whether faoapi should authenticate the caller and then act under **its own read credential** rather than re-using the caller's. |
| Location | `PLATFORM-001` §2 and §9 (O2); external: views-faoapi's `X-API-Key` validation path (`_validate_api_key` → `client.set_key(caller_key)`), views-faoapi #279 |

þing-01 *recorded* the mechanism — an external caller presents `X-API-Key`, and faoapi re-uses that
key to read the bucket (S4) — but never governed it. Nothing states who issues keys to external UN
parties, under what scope, or how they rotate. And the re-use itself is a **confused-deputy
pattern**: faoapi performs storage access under a credential supplied by the caller, so the caller's
scope, not faoapi's policy, bounds what the read can reach.

The adversarial pass called this the sharpest single finding in either `rýni`, on the grounds that
**the highest-stakes key on the platform is the least-modelled one**. Registered here because this
repo hosts the contract that names it; **owned by views-faoapi plus the operator**, not by this
repo. It bears directly on this repo's eventual design: the extracted client's `AuthManager`
hierarchy (ADR-001 Category 6) is where a "authenticate the caller, act under our own credential"
split would have to be expressible, so O2's resolution is an input to Phase 1, not merely adjacent
to it. Cross-refs: C-27 (rotation, same absence), `PLATFORM-001` §2/§5/§9.

---

### C-29: A value-less slot in the registry's `[target]` table kills every reader — it did, platform-wide, for a day

| Field | Value |
|-------|-------|
| ID | C-29 |
| Tier | 1 |
| Source | `incident` — self-inflicted in `2186d45`, found 2026-08-02 while preparing epic #26 story S6 |
| Trigger | Adding any entry to `[connection]` or `[target]` without a `value` — most likely when declaring coordinates for a consumer that does not exist yet, which is exactly what caused it. Also: any change to what the three readers scan. |
| Location | `docs/ADRs/platform/coordinate_registry.toml`; readers at `views-models/tools/credentials/registry_to_env.py` (moved there by views-models#309 — this entry previously cited the pre-move path `tools/registry_to_env.py:28,39-40`, the same stale path that made C-52 vacuous), `views-faoapi/deployment/registry_to_env.py`, `views-crafdapi/deployment/registry_to_env.py`; consumers at `views-models/postprocessors/un_fao/run.sh:24-26,67,83`, `views-faoapi/deployment/bootstrap.sh:24` |

Commit `2186d45` declared four `APPWRITE_CRAFD_*` slots in `[target]` with `status = "planned"` and
no `value`, to give an incoming consumer somewhere to read a coordinate from on day one. **All three
canonical readers scan exactly `connection` and `target`, and raise on any entry there lacking a
value** — `ValueError: registry coordinate 'X' (class 'target') has no value`. The registry was
therefore unreadable by every consumer on the seam from `2186d45` until PR #31.

**Why it was silent, which is what makes it Tier 1.** `un_fao/run.sh` sources `.env` but exports
only `GITHUB_TOKEN` and `APPWRITE_DATASTORE_API_KEY`, so coordinates reach the delivery process
**only** from the registry; `views-faoapi/deployment/bootstrap.sh` provisions the production server
the same way. A crashed reader therefore means *no coordinates at all* — and `run.sh` prints a
WARNING and continues (**C-47**, views-models#308). A total coordinate outage produced no error
signal for roughly a day, on `main` and `development`, across the delivery path **and** the
production provisioning path.

**Two properties of this repo made it invisible here.** It has no runtime, so nothing local
exercises the registry; and the readers live in three other repositories, so no test in any single
repo covered the contract between them. The registry is a *data file with consumers* and was being
edited as though it were prose.

**Fix and guard.** Planned slots move to `[planned]`, a table no reader scans; a slot with no value
is a declaration of intent, not a coordinate. `tests/test_registry_reader_contract.py` asserts the
invariant and was **proven to bite** — re-introducing the exact break turns it red. That test also
caught a defect in itself on first run: it *skipped*, because `tomllib` needs 3.11 and this suite
runs 3.10, so it now falls back to `tomli` and fails loud if no parser exists.

Closes when PR #31 reaches **`main`**, not merely `development` — both were broken.

> **Status update, 2026-08-02 — do not read the paragraph above as settled.** Two of the three claims
> it makes are no longer true. **(a)** *"Planned slots move to `[planned]`"* — the `[planned]` table
> now contains nothing and does not exist in the parsed file, so an auditor cannot tell "fixed" from
> "reverted" (**C-54**), and the guard covering it skips permanently (**C-55**). **(b)** *"All three
> canonical readers … raise"* — they no longer do. `views-models` exits 0 on that shape and emits a
> partial coordinate set (**C-51**). The companion guard written to detect exactly that has been
> pointing at a non-existent path since views-models#309 (**C-52**). The invariant test in this repo
> still bites; the cross-repo agreement claim does not.

Cross-refs: views-models C-47 (the warn-and-continue that hid it, views-models#308), C-21 (same
hazard family: registry content reachable without a deliberate check), C-51, C-52, C-54, C-55,
epic #26.

---

### C-30: `secret_scanning_non_provider_patterns` is off on the public consumer repos — the one flag þing-02 made load-bearing

| Field | Value |
|-------|-------|
| ID | C-30 |
| Tier | 3 |
| Source | `manual` — prudence sweep of epic #26, 2026-08-02; premise corrected the same day |
| Trigger | Cutting `views-productionapi`, the second clone, which will inherit whatever default the org carries. Also: any decision to treat a clean scan as evidence, since this flag governs what "clean" covers. |
| Location | `views-platform/views-crafdapi` (public); org-wide setting; þing-02 **G2(d)**, tracked at views-appwrite#12 |

**Corrected premise.** This entry was first registered as *"crafdapi went public before its scanning
controls, so prevention became retrofit."* **That was wrong.** Verified against the GitHub API rather
than the claim: `secret_scanning` **enabled**, `secret_scanning_push_protection` **enabled** — both on
before the first push, exactly as `orð_dómr §III(3)` requires. The clone's own epic
(views-crafdapi#1) states it, and the statement is true.

**The real gap is narrower and more specific.** `secret_scanning_non_provider_patterns` is
**disabled**, as are `dependabot_security_updates` and `secret_scanning_validity_checks`.

That first flag is not incidental. þing-02 **S32** recorded that *both* seats defending §5.7 withdrew
their objection on a **falsifiable condition**: that **G2(d) must include
`secret_scanning_non_provider_patterns` and `.ipynb`-cell scanning**, because those are the two that
catch the classes this platform's own history actually contained — views-datafactory's English-prose
password and views-models' notebook-cell material. Provider-pattern scanning alone misses both.

So a clean scan on these repos is a **narrower guarantee than the record assumes**, and the withdrawal
that struck §5.7 was conditioned on a flag that is not set.

**Not crafdapi's defect.** It is an org-level default, and the clone did more than the precondition
asked. It is recorded here because this repo hosts the contract whose §5.7 strike depends on it.

Cross-refs: views-appwrite#12 G2(d) (operator), C-29 (same sweep), þing-02 S32.

---

> **Numbering note.** The next ten entries start at **C-51**, not C-31. `C-31`–`C-41` were allocated
> by the `/falsify` audit of 2026-07-31 (they name the stubs in
> `tests/test_falsification_thing02_contract.py`) but were never written into this register, and
> `C-47`/`C-50` appear here only as cross-references into **views-models'** register. Reusing any of
> those numbers would make a citation ambiguous about which register it means. The gap is deliberate.
> Registering C-31–C-41 properly is separate outstanding work.

---

### C-51: The three registry readers have diverged — views-models tolerates the exact shape the other two reject

| Field | Value |
|-------|-------|
| ID | C-51 |
| Tier | 1 |
| Source | `code-review max` on `origin/main...development`, 2026-08-02; every claim re-executed independently before registering |
| Trigger | Declaring `views-productionapi`'s slots, which this registry already plans for at `coordinate_registry.toml:157-160`. The moment any value-less entry lands in `[target]`, the three readers take two different actions. |
| Location | `views-models/tools/credentials/registry_to_env.py`; `views-faoapi/deployment/registry_to_env.py`; `views-crafdapi/deployment/registry_to_env.py`; fixture at `tests/fixtures/registry_valueless_target.toml` |

Executed against the value-less fixture under a 3.11 interpreter:

| Reader | Exit | Behaviour |
|---|---|---|
| `views-models/tools/credentials/registry_to_env.py` | **0** | emits a **partial** coordinate set |
| `views-faoapi/deployment/registry_to_env.py` | 1 | `ValueError: registry coordinate 'FIXTURE_NO_VALUE' (class 'target') has no value` |
| `views-crafdapi/deployment/registry_to_env.py` | 1 | identical `ValueError` |

**This is C-29 half-reintroduced, and made asymmetric — which is worse than the original.** In the
original incident every consumer failed, so the blast radius was uniform. Now a value-less `[target]`
entry makes the **UN FAO delivery run against a silently incomplete coordinate set** while both
external APIs hard-fail at bootstrap. The loud failures are on the paths that can afford to fail; the
silent one is on the path that writes data to an external partner.

**It is not a bug to be unilaterally fixed — it is a contradiction between two ratified positions.**
`views-models/tests/test_registry_to_env.py::test_planned_reservation_is_skipped_not_fatal` pins
skip-don't-raise. `views-appwrite/tests/test_registry_reader_contract.py` pins raise-don't-skip. Both
are ratified; both are green; they disagree. Whichever way it settles, one repo's test must change,
and that is a cross-repo decision, not a patch.

Cross-refs: C-29 (the original incident), C-52 (the guard that should have caught this and cannot),
D-05 (the raise-vs-skip disagreement).

---

### C-52: The reader-agreement guard is vacuous — it points at a path that does not exist and grades two identical clones

| Field | Value |
|-------|-------|
| ID | C-52 |
| Tier | 1 |
| Source | `code-review max`, 2026-08-02; confirmed by direct filesystem check |
| Trigger | Any future reliance on a green `test_registry_readers_agree.py` as evidence that the readers agree — including the next `ship-it` in this repo. |
| Location | `tests/test_registry_readers_agree.py:60`; also propagated into C-29's own Location field |

`READER_PATHS` names `views-models/tools/registry_to_env.py`. **That file does not exist.** The real
reader is at `views-models/tools/credentials/registry_to_env.py`, moved there by views-models#309.
`_present()` filters on `is_file()` and drops missing readers **silently**, so all four tests grade
only `views-faoapi` and `views-crafdapi` — which are byte-identical clones. They agree trivially.

The file was written for epic story **S6**, whose entire purpose was to detect reader divergence.
Divergence exists (**C-51**) and the guard is blind to it. `test_at_least_one_reader_is_present`
does not fire either, because two of three are present.

**Trap on repair, recorded so the next person does not fall into it.** Correcting the path turns two
tests red, and the red message *misattributes the cause*: it reads *"these readers ACCEPTED a
value-less `[target]` slot"*, when what views-models actually did was honour a reservation marker —
`status = "planned — …"` at `tests/fixtures/registry_valueless_target.toml:18` is verbatim the token
its `_is_planned()` matches. The tempting one-line fix is to delete that `status` line from the
fixture, which greens the suite **and destroys the only artifact that exposes C-51**. Fix the path
and settle raise-vs-skip in the same change, or not at all.

Cross-refs: C-51, C-29, D-05, epic #26 story S6 (#28).

---

### C-53: Four coordinates were added with no version bump, defeating the one cross-repo drift detector

| Field | Value |
|-------|-------|
| ID | C-53 |
| Tier | 2 |
| Source | `code-review max`, 2026-08-02 |
| Trigger | Merging `development` to `main`. Three consumers resolve this file through `/blob/main/`, so the merge itself is what changes their meaning. |
| Location | `docs/ADRs/platform/coordinate_registry.toml:21,24`; `docs/validate_docs.sh` check 7; `views-postprocessing/views_postprocessing/{crafd,unfao}/appwrite_env.py` |

Four `APPWRITE_CRAFD_*` coordinates became canonical. `[meta] version` stays `1.3.0` and `amended`
stays `2026-07-31` for a 2026-08-02 change. This violates two rules stated in the artifacts
themselves: the registry header line 15 (*"Changes: by PR to this file + a seam-contract version
bump"*) and seam contract **§10:413** (*"every change bumps the version. The registry and this
contract version together"*).

**The guard is green because it asks the wrong question.** `validate_docs.sh` check 7 asserts the two
version numbers are *equal*. Bumping neither satisfies it perfectly. A check that compares two mutable
values to each other, and to nothing external, cannot detect that both stood still.

**Concrete downstream cost.** `views-postprocessing` pins `SEAM_CONTRACT_VERSION = "1.3.0"` and built
a drift test that compares the registry's `meta.version` against that pin — its own docstring calls it
*"the check that catches everything the other one cannot"*. Four new targets landed; it stays green.
Separately, `views-pipeline-core`, `views-postprocessing` and `views-datafactory` link to
`/blob/main/` rather than a pin (confirmed red by
`test_falsify_c40_every_consumer_pins_the_contract`), so **merging to `main` silently changes what
those three resolve to, with no version change they could detect.**

**Fixed in v1.4.0**, with a note on how hard the guard was to write. `validate_docs.sh` gains a check
that the version *value* moved when the file changed. Three drafts, two of them wrong in opposite
directions, both caught by `review-diff` before commit:

| Draft | Test | How it failed |
|---|---|---|
| 1 | any changed line matching *version.*semver* | passes on prose like *"byte-identical to v1.3.0"* while the declaration stands still |
| 2 | the declaration line appears in the diff | passes when that line changes for an unrelated reason — **editing the trailing comment on `version = "1.3.0"` satisfied it** |
| 3 | compare the extracted value across revisions | correct; mutation-proven against both cases above |

Draft 2 is the instructive one: it is *stricter* than draft 1 and still wrong, and it reported **OK**
on the exact violation this entry describes. A guard that asks "was this line touched?" is not asking
the question consumers ask, which is "is what I pinned still what I would get?" Recorded because this
register already contains two entries (C-52, C-55) about guards that were green and blind.

Cross-refs: C-29, C-52, C-55, seam contract §10, `test_falsify_c40_*`.

---

### C-54: The load-bearing C-29 warning now asserts the opposite of the data beneath it

| Field | Value |
|-------|-------|
| ID | C-54 |
| Tier | 2 |
| Source | `code-review max`, 2026-08-02 |
| Trigger | The next consumer needing a reserved slot — `views-productionapi`, which this file explicitly anticipates at lines 157-160. |
| Location | `docs/ADRs/platform/coordinate_registry.toml:76-112`; `reports/technical_risk_register.md` C-29 |

Line 76 heads the section `INCOMING CONSUMERS (values pending)`. Line 78 reads
`⚠ THESE LIVE IN [planned.*], NOT [target.*], AND THAT IS LOAD-BEARING`. Forty-three lines below it
sit four `[target.*]` entries carrying values. **The `[planned]` table no longer exists at all.**
Lines 102-106 warn *"Do NOT fill these with plausible-looking placeholders"*, where *"these"* now
resolves to filled `[target]` entries.

The prose that explains a Tier 1 incident is now contradicted by the file it lives in. A reader
arriving to add `views-productionapi`'s slots meets a caps-lock warning the data visibly disobeys,
concludes it is stale, and writes a value-less `[target]` entry — **commit `2186d45`, exactly.**

**Compounding.** C-29 in this register states the fix as *"Planned slots move to `[planned]`, a table
no reader scans."* An auditor opening the registry today finds no `[planned]` table and **cannot
distinguish "fixed" from "reverted."**

Cross-refs: C-29, C-55.

---

### C-55: The planned-slot guard skips itself into dormancy the moment there is nothing to guard

| Field | Value |
|-------|-------|
| ID | C-55 |
| Tier | 3 |
| Source | `code-review max`, 2026-08-02; confirmed by test run |
| Trigger | Writing the first new `[planned]` entry after this commit — the guard is off at exactly that moment. |
| Location | `tests/test_registry_reader_contract.py:102` |

`test_planned_slots_are_outside_the_scanned_tables` calls `pytest.skip` when no `[planned]` slots
exist. With the table gone it skips on every run — confirmed:
`SKIPPED [1] … no planned slots declared right now — nothing to check`.

A guard that stands down whenever it is not already being satisfied is off during the only window
that matters: after the last planned slot graduates and before the next author writes one. That
author gets no feedback, which is the precise population the test exists to serve.

Cross-refs: C-54, C-29.

---

### C-56: The CRAFD caller key as issued cannot authenticate a single request

| Field | Value |
|-------|-------|
| ID | C-56 |
| Tier | 2 |
| Source | `code-review max`, 2026-08-02; call path and registry evidence both re-verified |
| Trigger | views-crafdapi **S11** (#12) — the first deploy and smoke test. Its acceptance criterion is `smoke ALL PASS`, which cannot be met. |
| Location | `docs/ADRs/platform/coordinate_registry.toml:279`; `views-crafdapi/src/views_crafdapi/managers/api.py:297` |

The registry records the issued scopes as `databases.read, rows.read, documents.read, files.read` —
**no `buckets.read`**. But `_validate_api_key` validates every key by calling
`manager.list_buckets(limit=1)` and raises `HTTPException(401)` if it fails, and it is reached through
`Depends` on **every** route, including `/health`.

**This registry proves the consequence itself.** Lines 249-250 record the operator's own live probe:
`GET /v1/storage/buckets` without `buckets.read` returns
`general_unauthorized_scope, "missing scopes ([buckets.read])"`. FAO's key masks the requirement
because it holds `buckets.read` (line 214), so the existing deployment gives no warning.

Also missing: `tables.read`/`collections.read`. This file's own read-only recipe at line 239 names
four scopes a read consumer needs; the issued key satisfies two of them.

**Operator console action, not a code change.** Tick `buckets.read` and `tables.read` on
`crafd-caller-read`.

> **REMEDIATED AT SOURCE 2026-08-03 — verification pending deploy.** The operator ticked both
> scopes; the key now carries six. Recorded in the registry at **v1.4.1**.
>
> **This entry stays open, deliberately.** The console is authoritative for what the key *carries*,
> and that is fixed. It is not authoritative for whether CRAFD's requests *succeed* — that is S11's
> smoke test (views-crafdapi#12), and views-crafdapi is not deployed yet. Closing on the console
> alone would be recording a verification that was never performed, which is the habit this register
> exists to break. **Closes when the smoke test passes.**
>
> **No probe was run, on purpose.** One was drafted: a `curl` against `GET /v1/storage/buckets` with
> the key. It was discarded because it would have had the operator paste a live secret into a shell
> to re-learn what the console already displays. The platform has spent weeks removing
> credential-handling steps from humans (views-models ADR-018, seam contract §2); reintroducing one
> as ceremony — for a check that answers nothing the console does not — is a bad trade even when
> technically harmless. Worth recording because the pull toward "verify it with a probe" was strong
> and wrong, and it will recur at the next key.
>
> **The generalisable finding**, which is why this is not merely a config slip: a read-only key
> needed a permission unrelated to reading data. `buckets.read` is required because the API
> *authenticates* by listing buckets. Nobody choosing scopes from the key's purpose would tick it,
> and the next per-party key will hit this unless its issuer reads the registry slot first.

Filed as **views-crafdapi#29** (the end-to-end verification that closes this) and raised on
views-crafdapi#12 (the deploy story it sits inside).

Cross-refs: C-28 (external-caller credential unmodelled), C-58, views-crafdapi#12, views-crafdapi#29.

---

### C-57: Graduating the slots created a fourth holder of the over-scoped key, and the record still says three

| Field | Value |
|-------|-------|
| ID | C-57 |
| Tier | 3 |
| Source | `code-review max`, 2026-08-02 |
| Trigger | Executing the key split (views-faoapi#338), which is sized from the `serves_identities` list. |
| Location | `docs/ADRs/platform/coordinate_registry.toml:171-177`; `views-postprocessing/views_postprocessing/crafd/managers/crafd.py` |

While the four CRAFD names sat in `[planned]`, no reader emitted them, so
`assert_env_declared(CONNECTION_ENV + CRAFD_ENV)` could only raise and the CRAFD writer path was
unreachable. **This diff is what makes it resolvable.** `_crafd_appwrite_config` builds the
`crafd_bucket` writer with `credentials=os.getenv("APPWRITE_DATASTORE_API_KEY")`.

`serves_identities` (lines 171-175) still lists three, and `observed` (line 177) still reads
*"VIOLATES seam contract §5.3 — one key, three identities"*. Whoever executes the split cuts over the
three named holders, narrows or revokes the old key, and the CRAFD delivery — now the sole writer of
`crafd_bucket` under that key, on nobody's list — stops uploading.

The same commit that gives CRAFD a clean per-party read key silently gives the platform's most
over-scoped key a fourth holder.

Raised on **views-faoapi#338** — that issue is sized from `serves_identities`, and executing it
against the stale three-entry list stops the CRAFD delivery silently.

Cross-refs: C-27, C-28, views-faoapi#338.

---

### C-58: The secret's recorded destination contradicts its own carrier field

| Field | Value |
|-------|-------|
| ID | C-58 |
| Tier | 3 |
| Source | `code-review max`, 2026-08-02 |
| Trigger | An operator executing views-crafdapi S11 literally. |
| Location | `docs/ADRs/platform/coordinate_registry.toml:276,284` |

Line 284 says the key *"goes into the views-crafdapi deployment env at first deploy, S11"*. Line 276
declares `carrier = "X-API-Key request header (presented by the caller, re-used by the API)"` — the
key belongs to **CRAFD**, not to the host.

`_REQUIRED_APPWRITE_ENV_VARS` in views-crafdapi contains no caller-key variable; the key arrives via
`Header(...)` and goes straight to the SDK; and `grep -rn CRAFD_CALLER_API_KEY` across the workspace
returns **no code hits at all** — only the registry slot and this entry. **There is no env slot to
fill.** Following S11
literally installs the key where nothing reads it and never sends it to the party that must present
it: every request 401s while the checklist reads done.

**The obvious repair is the dangerous one.** Adding an env var to make the sentence true answers O2's
confused-deputy question in the direction this slot's own `note` claims it is not deciding. Fix the
sentence, not the code.

Cross-refs: C-28 (O2), C-56, seam contract §9.

---

### C-59: Documents still describe the CRAFD slots as planned, and one issue reference cannot be resolved

| Field | Value |
|-------|-------|
| ID | C-59 |
| Tier | 4 |
| Source | `code-review max`, 2026-08-02 |
| Trigger | A new consumer following `joining_the_seam.md` as the onboarding checklist it is advertised to be. |
| Location | `docs/ADRs/platform/joining_the_seam.md:47-49`; `docs/ADRs/platform/coordinate_registry.toml:283` |

`joining_the_seam.md` still describes the four CRAFD slots as `status="planned"`, and views-crafdapi's
own ADR-034 §7 does the same. Separately, the bare `#338` at registry line 283 resolves to nothing
from this repo — its referent is **views-faoapi#338**. (The `#10` references at lines 118 and 274 are
fine: the surrounding prose repo-qualifies them.)

Cross-refs: C-54, ADR-011 (identifiers must be readable at the point of use).

---

### C-60: views-crafdapi tells developers to populate a `.env` the application never reads

| Field | Value |
|-------|-------|
| ID | C-60 |
| Tier | 3 |
| Source | `code-review max`, 2026-08-02 — adjacent finding, outside this diff |
| Trigger | The first developer onboarding to views-crafdapi by following its README. |
| Location | `views-crafdapi/README.md:50` vs `views-crafdapi/src/views_crafdapi/managers/model.py:254`; same shape at `views-faoapi/README.md:42` |

The README says the `.env` is *"located in `views-models`"*. `model.py:254` resolves it with
`pyprojroot.here()`, which returns **the caller's own root** — `views-crafdapi/.env`. A developer
following the README populates a file the app never reads, and views-models' single-writer gate then
rejects those names as a second writer.

Stale inheritance from when faoapi lived inside views-models. **Not this repo's to fix** — recorded
here because this repo owns the seam these READMEs describe.

Cross-refs: views-models ADR-018 (single writer), C-53.

---

### C-61: `_is_planned()` decides a coordinate's fate by prefix-matching prose

| Field | Value |
|-------|-------|
| ID | C-61 |
| Tier | 2 |
| Source | `expert-code-review` of D-05, 2026-08-03 (Gang of Four + Hickey, independently) |
| Trigger | Writing any `status` on a value-less entry that begins with the letters "plan" — `"planned-for-deletion"`, `"planning removal"`, `"plan: drop this"`. |
| Location | `views-models/tools/credentials/registry_to_env.py:31-38` |

```python
return str(entry.get("status", "")).strip().lower().startswith("planned")
```

A coordinate is silently withheld from the emitted environment if a human wrote seven particular
characters at the start of a prose field. `"planned-for-deletion"` — a plausible thing to write about
a coordinate being retired — reads as a reservation and the name vanishes.

The deeper problem is the one Hickey names: **the marker is not evidence.** A value-less entry with
`status = "planned"` carries no more information than one without; it is the same absence with an
excuse attached. Treating the excuse as authoritative is how views-models lost the ability to
distinguish *"legitimately reserved"* from *"the registry is broken and I could not tell"* — the
platform's own **Cluster J**, in its own code.

Resolved by the D-05 recommendation (delete the predicate). Registered separately because the
stringly-typed predicate is a defect on its own terms even if D-05 somehow settles the other way.

Filed as **views-models#331** — standalone, because if D-05 settles the other way and reservations
stay skippable, this defect survives the ruling and would otherwise be tracked nowhere.

Cross-refs: C-51, D-05, views-models#327, views-models#330 (the validator that cannot catch it).

---

### C-62: `platform_env_validate()` validates the reader against its own output

| Field | Value |
|-------|-------|
| ID | C-62 |
| Tier | 2 |
| Source | `expert-code-review` of D-05, 2026-08-03 (Ousterhout + Martin, independently) |
| Trigger | Relying on a green `platform_env_load` as evidence the delivery has every coordinate it needs — which `un_fao/run.sh:132` does on every run. |
| Location | `views-models/tools/credentials/platform_env.sh:273-278`; consumed at `views-models/postprocessors/un_fao/run.sh:132` |

```bash
coords="$(platform_env_coordinates)"        # runs registry_to_env.py
for name in $(echo "$coords" | cut -d= -f1) "$PLATFORM_ENV_SECRET_NAME"; do
  platform_env_is_exported "$name" || missing="$missing $name"
```

The required-name list is derived from the reader's own output. A name the reader dropped is not in
`$coords`, so it is not in the loop, so nothing notices. **The function structurally cannot detect a
skip** — the one failure mode a validator on this path exists to catch.

**Worse than a weak check, because of its name.** `platform_env_load` runs it as the final step of
"the whole contract, in the one correct order", and the delivery gates on it. A reader emitting 12 of
16 coordinates passes every gate and exits 0. A function whose name overstates its guarantee occupies
the slot a real check would fill, and is *believed*.

**Independent of D-05, deliberately.** The circularity remains whichever way the reader question
settles — it cannot catch a missing name arising from a typo'd table, a future class-filter change,
or a partially-written file either. views-faoapi and views-crafdapi each declare
`_REQUIRED_APPWRITE_ENV_VARS` independently of the reader; views-models has no equivalent.

Filed as **views-models#330**.

Cross-refs: C-51, C-47 (views-models#308, the warn-and-continue this was meant to replace).

---

### C-63: No reader checks the registry's `[meta] version`

| Field | Value |
|-------|-------|
| ID | C-63 |
| Tier | 3 |
| Source | `expert-code-review` of D-05, 2026-08-03 (Kleppmann — the only perspective to reframe D-05 this way, and uncontradicted) |
| Trigger | Adding any construct to the registry that an existing reader does not understand — a new class, a new field with semantics, a new table. |
| Location | all three `registry_to_env.py` copies; `coordinate_registry.toml` `[meta] version` |

The registry is versioned and consumers pin by version and commit. **The readers ignore the version
entirely.** A reader written against v1.x will silently mis-process a registry using a construct
added later, exactly as the three readers now disagree about `status = "planned"`.

This reframes D-05 as a **schema-evolution** problem rather than a failure-semantics one: can a
reader written at time T correctly process a registry written at T+1? The standard answer — refuse a
document you cannot fully interpret — is implemented by none of them. D-05 is one instance of the
class, and settling it leaves the class open.

Not folded into D-05 on purpose: a compatibility policy is a larger decision and should not ride on
a specific dispute.

Filed as **views-appwrite#45**.

Cross-refs: C-51, D-05, seam contract §10 (versioning).

---

### C-64: views-faoapi's reader cites a þing verdict that does not cover its case

| Field | Value |
|-------|-------|
| ID | C-64 |
| Tier | 3 |
| Source | `expert-code-review` of D-05, 2026-08-03 — checked against the þing record rather than taken from the docstring |
| Trigger | Weighing the D-05 dispute, where this line is the strongest-looking evidence on one side. |
| Location | `views-faoapi/deployment/registry_to_env.py:29-30`; identical clone at `views-crafdapi/deployment/registry_to_env.py`; source text at `þingit/01_identity_secrets_config/orð_dómr.md:103` |

The docstring reads *"fail loud rather than emit a half-built environment **(verdict D5)**."* D5's
actual text: *"**A wrong coordinate must RAISE**, naming the offending coordinate… **A
half-succeeded write must raise.**"*

D5 governs a coordinate whose value is **wrong**, and a **half-succeeded write**. An entry with **no
value at all** is a third case — absence, not incorrectness. The extension may well be right; it was
not ratified.

**The concrete cost, which is why this is not cosmetic.** In an open cross-repo dispute, one side
appears backed by a ratified þing verdict and the other does not. That asymmetry is an artifact of
this docstring, not of the record — and it nearly weighted this review before the source was checked.
An unsupported citation is how a rule decays into folklore, which is the failure ADR-011 exists to
name.

Filed as **views-faoapi#358**.

Cross-refs: D-05, ADR-011, C-51.

---

### C-65: Both platform keys expire on the same afternoon, and the recorded date was 13 days late

| Field | Value |
|-------|-------|
| ID | C-65 |
| Tier | 2 |
| Source | operator console read, 2026-08-05 — þing-02 A3(i), the gate that had been open since 2026-07-31 |
| Trigger | **2026-11-17 12:35.** Not a hypothetical — a scheduled, certain, dated total loss of Appwrite access. Also triggered earlier by any rotation plan sized against the old `~2026-11-30` figure. |
| Location | `docs/ADRs/platform/coordinate_registry.toml` — `APPWRITE_DATASTORE_API_KEY.expiry`, `FAO_CALLER_API_KEY.observed` |

| Key | Expires |
|---|---|
| `VIEWS Pipeline Core` | 2026-11-17 **12:35** |
| `UN FAO` | 2026-11-17 **16:10** |

Three hours thirty-five minutes apart. **104 days from this entry.**

**There is no stagger and no fallback.** At 16:10 that day every identity on the seam is dead at
once: every model and ensemble write, the un_fao delivery, the CRAFD delivery, all preflights, and
FAO's own read access. The two keys cannot cover for each other — a rotation plan that leans on one
while replacing the other has no ground to stand on. Consistent with the earlier inference that both
were issued together on a 12-month term (~2025-11-17).

**Why this is a register entry and not just a calendar note.** For four months the record said
`~2026-11-30`, relayed and unverified, and §2 carried a standing warning that its figures were
*"operator testimony relayed by a seat"*. **The real date is thirteen days earlier.** Anyone sizing
the rotation against the record believed in slack that does not exist — and the FAO half needs
**external coordination**, which is precisely the part that cannot be compressed at the end. The
approximation was never wrong in a way any check could detect; it hardened into a planning figure by
being repeated.

That is the same failure shape as C-64 (a docstring citing a verdict that did not say what it
claimed) and C-53 (a version that could stand still through a content change): **a soft fact quoted
until it reads as a hard one.**

**What this does not change.** No clause, no obligation. §5 already requires the key split and the
narrowing; D4 already fixes their order. This fixes the *deadline* for work that was already owed,
and removes thirteen days from it.

**Ordering consequence for D4.** Whatever sequence is chosen must **complete** before 2026-11-17 —
it cannot straddle the date, because there is no surviving key on the far side.

Recorded in registry **v1.4.3** / `appwrite-seam-v1.4.3`. Cross-refs: C-27 (rotation has no
propagation mechanism — that gap now has a date), C-28, views-appwrite#12 (e-caller), views-faoapi#338
(the split, whose deadline this is).

---

## Disagreements

### D-01: Decomposition granularity — eight modules vs depth-driven boundaries

| Field | Value |
|-------|-------|
| ID | D-01 |
| Source | expert-review (2026-06-12) |
| Perspectives | Martin/GoF (eight one-concern modules per `README.md:216-237` is clean separation aligned with ADR-001/002), Ousterhout/Hickey (`auth.py` and `compat.py` are shallow modules — interface proliferation without hiding; merge until depth justifies splitting) |
| Resolution | Unresolved. Proposed: defer to what the Phase 1 decomposition reveals; pre-authorize boundary merges via ADR update rather than treating ADR-002's layer list as fixed file boundaries. Revisit at the Phase-1 decomposition review, when actual module depth is observable. |

---

### D-02: Bucket auto-creation — resilience convenience vs fail-loud constitution

| Field | Value |
|-------|-------|
| ID | D-02 |
| Source | expert-review (2026-06-12) |
| Perspectives | ADR-008:38 as written (auto-create is "explicit, documented behavior", not a hidden fallback — keep faoapi's behavior per `README.md:550`), Nygard (the typo'd-`bucket_id` scenario converts a config error into permanent silent data divergence — exactly what ADR-003 forbids; default must raise) |
| Resolution | **RESOLVED 2026-07-28 (þing-01 / issue #5).** Nygard's position wins, now ratified beyond this repo: a missing coordinate raises and names itself; provisioning is opt-in, default off, reachable only from a deliberate setup entrypoint. `ADR-008:38`'s blessing parenthetical is **struck and replaced** (ADR-008 Amendment Log, 2026-07-28); the rule is platform law at `PLATFORM-001` §6. The disagreement is closed: the position ADR-008 held was contradicted by a settled fact of the record — þing-01 sáttmál S8 (amended) established that **both** client lineages auto-provision on write-path misses, so the behavior was never the "documented, explicit" choice the clause claimed but a fallback hiding semantic failure. Live-code fixes belong to the lineages (views-faoapi #275; views-pipeline-core ADR-046 §5 + write path) and flip independently per `dómr_endurmat` E4; **C-13 carries the remaining code-side exposure** until they ship. |

---

### D-03: Improve during extraction vs after — error channels and cache structure

| Field | Value |
|-------|-------|
| ID | D-03 |
| Source | expert-review (2026-06-12) |
| Perspectives | Feathers (change nothing during characterization: extract faithfully, get contract tests green against known behavior, improve afterward), Hickey/Nygard (the single-error-channel consolidation and cache-as-decorator restructuring are cheapest to make *during* the decomposition that is happening anyway) |
| Resolution | Proposed: extract faithfully first; land improvements as contract-test-visible changes in v0.2 — with one exception: the C-13 fail-loud bucket default ships in v0.1 because the ratified constitution demands it. |

---

### D-04: Governance weight before code — walking skeleton vs constitution-first

| Field | Value |
|-------|-------|
| ID | D-04 |
| Source | expert-review (2026-06-12) |
| Perspectives | Beck (a walking skeleton — scaffold + CI + one passing compat test — should precede ~3,100 lines of binding documentation; feedback loops beat doctrine), Governance corpus position (the source copies diverged precisely from under-documentation; the constitution is the product the roadmap says is most at risk — see README R5/C-02) |
| Resolution | Unresolved tension, accepted: governance landed first as a deliberate choice. Revisit if CIC/register/ADR maintenance falls behind code reality (cross-ref C-09's stale-gate risk). **Update 2026-07-28 (þing-01):** briefly resolved in Beck's favour — the verdict approved a scaffold commit (walking skeleton: `pyproject` + CI + a reference validator + tests), which would have closed C-02 and C-18's open half. The adversarial re-weighing then **deferred it back** (`dómr_endurmat` E6): the scaffold's whole justification was hosting the validator, and the validator deferred behind *operator ∧ test project*, so the skeleton has nothing to walk toward yet. **D-04 therefore stays open**, with its resolution now trigger-tied rather than merely undecided — which is a better state than it was in, since the condition under which Beck wins is now written down (issue #8). |

---

### D-05: A reserved slot with no value — hard error, or skip and continue?

| Field | Value |
|-------|-------|
| ID | D-05 |
| Source | `code-review max` (2026-08-02), surfaced by C-51 |
| Perspectives | **views-appwrite position (raise):** a value-less entry in a scanned table is malformed data; the reader's job is to refuse it, because the consumer that receives a partial coordinate set has no way to know it is partial. Pinned by `tests/test_registry_reader_contract.py` and by C-29's incident narrative — the *silence* is what made that outage Tier 1. **views-models position (skip):** a reservation is a legitimate, expected state; hard-failing every consumer because some *future* consumer's slot is not yet filled couples unrelated repos and makes the registry impossible to edit incrementally. Pinned by `tests/test_registry_to_env.py::test_planned_reservation_is_skipped_not_fatal`, and by views-models' role as the one reader on the FAO delivery path. |
| Resolution | **Open — but the framing above is withdrawn. See the update.** |

> **UPDATE 2026-08-03 — after `expert-code-review`. This was posed as a two-sided dispute; on the
> evidence it is not one.**
>
> **The original framing, now withdrawn.** Both positions ratified, both suites green, needs a þing.
> An intermediate proposal was drafted — *"readers skip reservations and report what they withheld;
> consumers fail loudly on names they declare and did not receive"* — and **it is also withdrawn.**
> Three perspectives killed it independently: Nygard (a stderr announce has **already failed at this
> exact boundary** — C-29 was silent because of a warn-and-continue, C-47), Ousterhout (pushing the
> assertion to consumers distributes the same omission N ways), Beck (a three-repo change plus a
> permanent consumer obligation, to fix a shape the source-side gate already blocks).
>
> **Recommended ruling.** *Reservations live in `[planned]`. A value-less entry in `[connection]` or
> `[target]` is malformed regardless of any `status` it carries, and every reader raises on it.
> `status` is documentation and carries no semantics.*
>
> **Why it dissolves rather than settles the dispute.** The registry's own standing rule already says
> this, and `test_every_reader_scanned_entry_has_a_value` **passes and mutation-bites**, so the
> tolerated shape cannot be committed. `_is_planned()` therefore defends against an input the gate
> rejects — and by defending, converts a gate failure into silent data loss. It is defence-in-depth
> inverted: the second layer absorbs the first layer's failure instead of reporting it.
>
> **The coupling objection, stated fairly, and why it fails.** Raising couples unrelated repos: a
> reservation for `views-productionapi` would break the FAO delivery, which does not need that
> coordinate. This is what persuaded the original framing. It fails only because a correctly-filed
> reservation lives in `[planned]`, which no reader scans — so it is invisible and breaks nobody. The
> coupling exists only if reservations in scanned tables are accepted, which is the premise rejected.
>
> **Cost:** one deletion in one repo (`_is_planned()` + its test, views-models). faoapi and crafdapi
> already comply; views-postprocessing has no reader. Compare the withdrawn proposal: additions to
> three readers plus every future consumer. **With three WET copies, prefer the change that shrinks
> them.**
>
> **Governance.** May need less than a þing — it codifies text already in the registry rather than
> adding an obligation, which plausibly makes it clarification, not amendment. **That is the
> lawspeaker's call, not this repo's**, and views-appwrite has been wrong about exactly this before
> (PR #30, withdrawn).
>
> Posted for argument at **views-models#327**. Until the readers converge, C-51 stays Tier 1 and the
> two `xfail(strict=True)` markers stay — they fail on the unexpected pass, so the decision cannot
> quietly rot. Split out and filed separately: **C-62** (views-models#330) and **C-63**, both of
> which outlive this ruling either way.

---

## Resolved Concerns

### C-08: Entire governance corpus exists only as untracked files in a zero-commit repository — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-08 |
| Resolved | 2026-06-12 |
| Resolution | Initial commit `7d63643` created with the full corpus (README, docs/, reports/) and pushed to `git@github.com:views-platform/views-appwrite.git` (private repo, branch `main`). |

---

### C-11: Starting development contradicts the roadmap's recorded "hold" recommendation with no recorded reversal — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-11 |
| Resolved | 2026-06-12 |
| Resolution | README Decision Log #8 now records the honest current state: governance scaffolded ahead of any extraction trigger; Phase 1 start deferred pending in-flight work on adjacent repositories; the hold recommendation stands. No undocumented reversal remains. |

---

### C-22: No documented sequencing for the first commit's interlocking gates — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-22 |
| Resolved | 2026-06-12 |
| Resolution | "Gate Sequencing for Pre-Code Commits" added to `docs/contributor_protocols/carbon_based_agents.md`: falsification stubs are expected-red until their finding is resolved; docs-only commits may land with the pytest gate waived (recorded in the commit message); from the scaffold commit onward ADR-005 + CI apply in full with explicit expected-failure quarantine. Enforcing stub `test_falsify_r2_04` rewritten as a real check, now green. |

---

### C-23: README dependency URLs referenced the `prio-data` org — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-23 |
| Resolved | 2026-06-12 |
| Resolution | All three `prio-data` URLs replaced with `views-platform` (README publish step and both Phase 2/3 dependency lines); the open org-preference question in the publish step replaced with the recorded decision. |

---

## Register Conventions

- **ID format:** `C-xx` for concerns, `D-xx` for disagreements. IDs are permanent — gaps in numbering indicate merged or resolved entries.
- **Sources:** `repo-assimilation`, `expert-review`, `test-review`, `falsification-audit`, `clean-architecture-review`, `pr-review`, `tech-debt-audit`, `incident`, `manual`, **`þing-01`** (cross-repo assembly testimony — entries sourced here carry another seat's sworn account of its own code; treat the seat as the authority for its repo, and cite the `orð`/`sáttmál` item).
- **Resolution:** Move to "Resolved Concerns" with resolution date and summary when addressed. Two entries (C-10, D-02) are marked resolved **in place** rather than moved, because their narratives carry the amendment history that made them resolvable; the header counts treat them as resolved.
- **Header counts:** Manually maintained — update whenever a concern is added or resolved.
- **Note:** Many concerns reference locations in external repos (`views-pipeline-core`, `views-faoapi`) because this repository is a roadmap for a package not yet extracted. Confirm those locations when extraction (Phase 1) begins. **As of 2026-07-28 several are external by *ownership*, not merely by location** (C-13, C-26, C-27, C-28): this repo tracks them because it hosts `PLATFORM-001`, but cannot fix them — the fix belongs to a lineage owner or to the operator.
- **Governed by:** ADR-010 (`docs/ADRs/010_technical_risk_register.md`).
