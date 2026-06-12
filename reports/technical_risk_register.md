# Technical Risk Register

| Register Info     | Details                              |
|-------------------|--------------------------------------|
| Project           | views-appwrite                       |
| Owner             | Polichinl                            |
| Last Updated      | 2026-06-12                           |
| Total Concerns    | 11                                   |
| Open Concerns     | 10                                   |
| Resolved Concerns | 1                                    |

---

## Tier Definitions

| Tier | Severity | Description |
|------|----------|-------------|
| 1 | Critical | Silent data corruption or model output correctness risk. Requires immediate attention. |
| 2 | High | Structural fragility that will cause failures under realistic change scenarios. |
| 3 | Medium | Maintainability or coupling issues that increase cost of change. |
| 4 | Low | Code quality concerns that do not affect correctness or reliability. |

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

---

### C-03: SDK 13→14 compatibility layer exists in only one of the two source copies

| Field | Value |
|-------|-------|
| ID | C-03 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When `views-pipeline-core` upgrades its Appwrite SDK to 14+, verify that `_as_dict()`/`_get()` normalisation is present on every SDK response access path before deploying. |
| Location | external: `views-pipeline-core/modules/appwrite/file.py` (SDK 13 only); compat asset at `views-faoapi/managers/appwrite.py:31-72`; documented at `README.md:463-485,624` |

The Appwrite SDK changed responses from plain `dict` (SDK 13) to Pydantic models (SDK 14+) (`README.md:467-471`). `views-faoapi` handles both via `_as_dict()`/`_get()`, but `views-pipeline-core` is SDK-13-only and lacks this layer (`README.md:473`). If pipeline-core upgrades to SDK 14+ before the extraction happens, dict-style access (`response["$id"]`) against Pydantic models breaks across pipeline-core's Appwrite paths. This is the README's own trigger #2 for starting the extraction (`README.md:624`) and the stated reason faoapi was chosen as the extraction base (D-1, `README.md:598`). Latent today because pipeline-core remains on SDK 13. Currently unmitigated except by not upgrading.

---

### C-04: `AppwriteConfig` field divergence will break call sites during extraction

| Field | Value |
|-------|-------|
| ID | C-04 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When defining `views_appwrite.client.AppwriteConfig`, diff the field sets of both source repos' configs and confirm the new dataclass is a superset; then update every `AppwriteConfig(...)` construction site to pass `cache_dir=` instead of `path_manager=`. |
| Location | external: `views-pipeline-core` (`AppwriteConfig` with `timeout_seconds`, `path_manager`), `views-faoapi` (`AppwriteConfig` with `timeout_seconds` + `connect_timeout_seconds`, `path_manager`); documented at `README.md:148-155,421-422,578-582` |

The two source repos define `AppwriteConfig` with different fields: pipeline-core has `timeout_seconds` but not `connect_timeout_seconds`; both pass a `path_manager: ModelPathManager` that the extracted package intends to replace with `cache_dir: Optional[Path]` (D-4, `README.md:601`). The new config must be a superset (`README.md:421`), and every construction site across at least three repos must change `path_manager=...` to `cache_dir=path_manager.cache / "appwrite"` (`README.md:383,422`). A missed call site fails at construction time (`TypeError`). This is structural fragility with a concrete migration trigger. The README proposes a transitional config accepting both fields (R6 mitigation, `README.md:582`) — not yet implemented.

---

### C-05: Duplicated Appwrite clients drift, and cloning faoapi adds further copies

| Field | Value |
|-------|-------|
| ID | C-05 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When a bug is fixed in one Appwrite client copy, check whether the other copy has the same bug; and when `views-faoapi` is cloned for a new consumer API (e.g. World Bank, UNHCR), confirm whether the clone copies the Appwrite client a third time. |
| Location | external: `views-pipeline-core/modules/appwrite/file.py` (~3,047 lines), `views-faoapi/managers/appwrite.py` (~2,000 lines); documented at `README.md:39-45,128-155,540-552,622-639` |

Two implementations of the Appwrite client (~5,000 lines total) are ~90% identical but have already diverged: the `_as_dict` SDK-14 guard exists only in faoapi, class names differ, and timeout config exists in only one (`README.md:39-45,148-155`). Continued independent evolution risks silent behavioural divergence in production (e.g. one copy auto-creates a missing bucket while the other raises, `README.md:550`) and widens the eventual extraction diff. Cloning `views-faoapi` for a new stakeholder API copies the client a third time — the README's strongest "start now" trigger (#1, `README.md:622`). Currently mitigated only by the manual discipline in the Datafactory note: "if you fix a bug in one copy, fix both" (`README.md:639`). Subsumes the clone-creates-3rd-copy finding (RA-8) as an additional trigger/location.

---

### C-06: `AppwriteSaver` swallows all upload exceptions, hiding failures across the extraction

| Field | Value |
|-------|-------|
| ID | C-06 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | When implementing `DatastoreManager.upload()` in `views-appwrite`, define and document specific exception types, and update pipeline-core's `AppwriteSaver` to catch those specific types rather than bare `Exception`. |
| Location | external: `views-pipeline-core/managers/prediction/savers.py` (`AppwriteSaver`); documented at `README.md:423,584-588` |

`AppwriteSaver` in pipeline-core deliberately catches all exceptions during upload and logs instead of raising (graceful degradation, tied to the README's D-10/C-50 reference, `README.md:423`). The risk: if the extracted `DatastoreManager.upload()` changes the exception types or error codes it raises, the catch-all still swallows them but log messages shift, so silently-failed uploads (predictions not stored) become harder to diagnose (R7, `README.md:584-588`). This borders Tier 1 because a swallowed upload failure leaves downstream consumers reading stale data with no raised error; it is held at Tier 2 because a log signal does exist and the behaviour is an intentional, documented contract. The README itself flags catching specific types as the improvement (`README.md:588`).

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

---

### C-11: Starting development contradicts the roadmap's recorded "hold until a trigger fires" recommendation with no recorded reversal

| Field | Value |
|-------|-------|
| ID | C-11 |
| Tier | 4 |
| Source | repo-assimilation (2026-06-12) |
| Trigger | When Phase 1 work begins, record which roadmap trigger fired (or that the hold recommendation is deliberately overridden) in the README Decision Log or a new ADR, and update `Status: Planned` (`README.md:5`). |
| Location | `README.md:608-639` (Datafactory Notes: "hold off... until a concrete trigger fires"), `README.md:592-604` (Decision Log D1–D7, last entry 2026-06-01) |

The roadmap's most recent dated entry (Datafactory Notes, 2026-06-02) explicitly recommends not building this package yet, naming three concrete start triggers: a second consumer API clone, an SDK 14 upgrade in pipeline-core, or a bug fix required in both client copies. The repository is now being treated as an active greenfield development project, implying that recommendation has been superseded, but no Decision Log entry, ADR, or README status change records the reversal or names the trigger that fired. ADR-000 exists precisely to prevent undocumented reversals of recorded decisions; this would be the first one. Resolution is a single Decision Log entry.

---

## Disagreements

(No disagreements registered yet.)

---

## Resolved Concerns

### C-08: Entire governance corpus exists only as untracked files in a zero-commit repository — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-08 |
| Resolved | 2026-06-12 |
| Resolution | Initial commit `7d63643` created with the full corpus (README, docs/, reports/) and pushed to `git@github.com:views-platform/views-appwrite.git` (private repo, branch `main`). |

---

## Register Conventions

- **ID format:** `C-xx` for concerns, `D-xx` for disagreements. IDs are permanent — gaps in numbering indicate merged or resolved entries.
- **Sources:** `repo-assimilation`, `expert-review`, `test-review`, `falsification-audit`, `clean-architecture-review`, `pr-review`, `tech-debt-audit`, `incident`, `manual`.
- **Resolution:** Move to "Resolved Concerns" with resolution date and summary when addressed.
- **Header counts:** Manually maintained — update whenever a concern is added or resolved.
- **Note:** Many concerns reference locations in external repos (`views-pipeline-core`, `views-faoapi`) because this repository is a roadmap for a package not yet extracted. Confirm those locations when extraction (Phase 1) begins.
- **Governed by:** ADR-010 (`docs/ADRs/010_technical_risk_register.md`).
