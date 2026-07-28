# Technical Risk Register

| Register Info     | Details                              |
|-------------------|--------------------------------------|
| Project           | views-appwrite                       |
| Owner             | Polichinl                            |
| Last Updated      | 2026-06-12                           |
| Total Concerns    | 25                                   |
| Open Concerns     | 20                                   |
| Resolved Concerns | 5                                    |

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
| C. Inherited behavior vs fail-loud constitution | Source-repo behaviors conflict with ADR-003/008; identified but unadjudicated | C-06, C-13, C-14 (+D-02) | 2 | Fold into ADR-014; amend ADR-008:38 per D-02 |
| D. Extraction inputs unsecured | Phase 1 inputs (source SHAs, divergence audit, source governance) uncaptured | C-03, C-05, C-07, C-16 | 2 | Divergence-audit artifact as the first act of Phase 1, when upstream settles |
| E. Scaffold mechanics unowned | No document owns sub-architectural setup decisions | C-02, C-10, C-18 | 3 | One scaffold session: `pyproject.toml`, CI workflow, `.gitignore`, ADR-numbering alignment |

Standalone: C-01 (dissolves when the scaffold exists), C-21 (documentation half resolved 2026-06-12; fixture guard pending Phase 1).

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

See also C-06 (the consumer-side catch-all that would mask the partial failure).

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
| Resolution | Unresolved tension, accepted: governance landed first as a deliberate choice. Revisit if CIC/register/ADR maintenance falls behind code reality (cross-ref C-09's stale-gate risk). |

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
- **Sources:** `repo-assimilation`, `expert-review`, `test-review`, `falsification-audit`, `clean-architecture-review`, `pr-review`, `tech-debt-audit`, `incident`, `manual`.
- **Resolution:** Move to "Resolved Concerns" with resolution date and summary when addressed.
- **Header counts:** Manually maintained — update whenever a concern is added or resolved.
- **Note:** Many concerns reference locations in external repos (`views-pipeline-core`, `views-faoapi`) because this repository is a roadmap for a package not yet extracted. Confirm those locations when extraction (Phase 1) begins.
- **Governed by:** ADR-010 (`docs/ADRs/010_technical_risk_register.md`).
