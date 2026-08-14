# Technical Risk Register

| Register Info     | Details                              |
|-------------------|--------------------------------------|
| Project           | views-appwrite                       |
| Owner             | Polichinl                            |
| Last Updated      | 2026-08-14                           |
| Total Concerns    | 62                                   |
| Open Concerns     | 51 — of which **36 live, 15 dormant** (see *Dormancy*) |
| Resolved Concerns | 11                                   |
| Disagreements     | 5 (3 open — 2 of them dormant; 2 resolved — D-02, D-05) |
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

Clusters group open concerns by shared root cause; fixing the root cause resolves — or fully specifies the fix for — every member entry. Membership reflects open entries only.

> **Recurated 2026-08-08.** The block below was written on 2026-06-12, when this repository was
> pre-þing, pre-registry-incident and private. It covered 24 of 24 open entries then. By today it
> covered **24 of 48** — every concern from C-29 onward, which is the entire credential, registry and
> publication era, sat in no cluster at all. Clusters A–F are **kept unchanged** because their
> analysis of the pre-þing corpus is still correct; **G–K** cover the second half, and **L** (2026-08-13) the third.
>
> Note what the gap itself demonstrates: the register grew by 24 entries in seven weeks and its
> *organising layer* did not move once. A flat list of 48 is a write-only artifact.

| Cluster | Root cause | Members | Highest tier | Fix strategy |
|---------|-----------|---------|--------------|--------------|
| A. Corpus freshness | External facts snapshotted in prose, never re-verified | C-09, C-17 (evidence also in C-03, C-05) | 2 | Reconcile roadmap with reality once upstream work settles; extend `validate_docs.sh` past `ADR-00[0-9]` |
| B. Unratified public contracts | Interfaces named but contracts never written (ADR-012/014 and CICs missing) | C-04, C-12, C-15, C-19, C-20, C-24, C-25 (+D-01, D-03) | 2 | One contract-writing session: ADR-012 (config schema), ADR-014 (exception taxonomy, envelope rules), `DatastoreManager` CIC |
| C. Inherited behavior vs fail-loud constitution | Source-repo behaviors conflict with ADR-003/008 | C-06, C-13, C-14 | 2 | **Doctrine settled 2026-07-28** (þing-01: ADR-008:38 amended, D-02 resolved, `PLATFORM-001` §6 ratified). Remaining work is *code-side and external* — the two client lineages ship raise-by-default; C-14's retry policy still needs ADR-014 |
| F. Platform seam contract — open items (new 2026-07-28) | The seam contract this repo now hosts names two hard problems it did not solve | C-27 (O1: secret-value rotation has no propagation mechanism), C-28 (O2: the FAO external-caller credential is unmodelled) | 2 | Not this repo's to fix: C-27 is an operator design task (issue #9), C-28 is views-faoapi + operator (faoapi #279). This repo tracks them because it hosts `PLATFORM-001` |
| D. Extraction inputs unsecured | Phase 1 inputs (source SHAs, divergence audit, source governance) uncaptured | C-03, C-05, C-07, C-16 | 2 | Divergence-audit artifact as the first act of Phase 1, when upstream settles |
| E. Scaffold mechanics unowned | No document owns sub-architectural setup decisions | C-02, C-18 (C-10 resolved 2026-07-28) | 3 | One scaffold session: `pyproject.toml`, CI workflow, ADR-numbering alignment. **Deferred by ratified decision** (`dómr_endurmat` E6, issue #8, trigger: operator ∧ test project) — the scaffold was priced against hosting the reference validator; the validator deferred, so the scaffold defers with it |

### Clusters G–K — added 2026-08-08

| Cluster | Root cause | Members | Highest tier | Fix strategy |
|---------|-----------|---------|--------------|--------------|
| **G. Guards that are green and blind** | A check is written to confirm a state, never to detect its absence. Nobody asks *"what input would make this fail?"* before trusting it | **C-55, C-62, C-67, C-68, C-74, C-75, C-79, C-80** (+ **C-09**, whose vacuity half belongs here and whose staleness half stays in A) · *resolved members, kept as the cluster's evidence: C-52, C-53, C-70, C-77, C-78* | 2 | **One rule, applied retroactively: a guard is not finished until it has been shown to fail.** **C-70 closed 2026-08-11** — every guard *that existed then* runs on every PR and the blocking ones are required, each proven by mutation in CI. **That sentence was written as "every guard" and C-77 narrowed it on 2026-08-14**: the workflow selects by filename, so the next guard module added joins no job. Corrected here rather than left standing, because the unqualified version is the one people quote. **The rule is now written down** — `docs/contributor_protocols/carbon_based_agents.md`, *"A Guard Is Not Finished Until It Has Been Shown to Fail"* (S6, #72) — together with the two recurring vacuity shapes this cluster is made of and the controls rule C-67 nearly failed. Every entry here was found by a person looking, not by the check failing; that is what the cluster is about, and the section is the correction. This is the largest cluster and the most preventable |
| **H. Soft facts hardening into hard ones** | Nothing checks prose, so a relayed or once-true statement survives indefinitely and is then planned against | **C-59, C-64, C-65, C-71** · *resolved members, kept as evidence: C-53, C-54* | 2 | Dated provenance on every factual claim. The registry's own `observed` / `scopes_enumerated` fields are the working model: they carry a read-date and say who read them. C-65 is the cost — a relayed expiry was 13 days wrong on the platform's only hard deadline |
| **I. Credential lifecycle has no owner** | Keys are created, recorded and reasoned about ad hoc; no inventory stays true and no lifecycle is defined | **C-27, C-28, C-30, C-56, C-57, C-58, C-65, C-66, C-69, C-82** | 2 | Not fixable in this repo — operator + views-faoapi#338. But this repo holds the inventory, and the inventory was wrong three times in a week (a key that could not authenticate, a fourth holder nobody listed, a destination contradicting its own carrier). **2026-11-17 is the forcing date** |
| **J. The registry's contract with its readers is unsettled** | One data file, three hand-copied readers, no agreed semantics for the edge cases | **C-29, C-51, C-61, C-63** (+ **D-05**) | 1 | Settle D-05 first — everything else here is downstream of it. views-models#327 carries the proposal; C-63 (no reader checks `[meta] version`) is the general form and deserves its own decision |
| **K. Consumers cannot tell what they consume** | This repo publishes by tag; consumers reference by hand; nothing verifies the reference | **C-60, C-72** | 2 | views-pipeline-core's `test_seam_contract_pin_is_coherent.py` is the reference implementation and the only one that exists. Two repos currently carry internally inconsistent pins |
| **L. The publisher cannot see its readers** | Every gate here verifies this repository's INTERNAL consistency, and nothing verifies what it tells anyone else. The three instances below each fired with every check green — ruff, validate_docs, pytest, three required CI jobs — because the failing thing lives in someone else's repo or in prose about this one | **C-73, C-76**, and **C-72** as the consumer-side mirror; **C-51** is the reader this repo structurally cannot see | 2 | **All three fired inside one week (2026-08-11 → 08-13), which is why this is a cluster and not three entries.** C-73: three editions shipped asserting "consumers pinned at earlier tags are unaffected" — true of the one consumer checked, false of the one that compares against a moving branch. C-76: the front page told six repositories to pin an edition seven versions stale. Both were found by accident — one by a third repo's request, one by an audit — never by a check. **Partly addressed:** `validate_docs.sh` check 9 now covers the pinning claim, mutation-proven four ways. **Not addressed:** this repo still has no publisher-side observation of whether a consumer broke, which is C-73's open half and the cluster's real subject. Cross-cutting with **G**: G is a guard that cannot see its own invariant; L is a repository that cannot see its own audience |

**Reading the three parts together.** A–F are about *documents that were never written*. G–K are
about *checks and facts that were written and then quietly stopped being true*. **L, added
2026-08-13, is a third failure mode and the newest**: things this repository says to *other people*
that nothing here can check — a pin instruction, a compatibility claim, an assumption about how a
consumer reads us.

The progression is worth naming, because it is a maturity curve rather than a list. **Absent →
stale → outward.** Each stage only becomes visible once the previous one is largely fixed: you
cannot notice that your guards are blind while your documents are missing, and you cannot notice
that your claims about others are unverified while your own guards are blind. **L's three entries
all fired within one week, immediately after the epic that closed G's acute member (C-70).**

The uncomfortable implication is that L is probably not the last stage.

Standalone: C-01 (dissolves when the scaffold exists), C-21 (README instance closed 2026-07-28; pipeline-core's dataclass-defaults instance and the fixture guard remain), C-04's re-derived remainder, C-26 (external, operational), **C-81** (a *reader* of this repository that cannot see the product — adjacent to G and L, but the failing party is neither a guard of ours nor a consumer, so it is not forced into either).

### Dormancy — added 2026-08-14 (`review-rr` strategic)

**Fifteen concerns describe a package that does not exist**, and their triggers are conditioned on
Phase 1 extraction — which is deferred behind roadmap **Decision Log #11** (three consumer APIs;
`views-publicapi` does not exist, so the count stands at two of three). **Those triggers cannot fire
today.** They are marked `> **Dormant**` beneath their field table:

`C-01 · C-02 · C-04 · C-06 · C-07 · C-12 · C-14 · C-15 · C-16 · C-17 · C-18 · C-19 · C-20 · C-24 · C-25`
— and disagreements **D-01** and **D-03**, whose resolutions both defer to what Phase 1 reveals.

**Two entries were considered and deliberately left live**, because reading them carefully is what the
marker is for. **C-03** fires when views-pipeline-core upgrades its Appwrite SDK to 14+, and **C-05**
fires when a bug is fixed in one client copy — those are roadmap triggers **T2** and **T3**, which are
*independently sufficient* to activate extraction and can fire on any ordinary working day. Marking
them dormant would have inverted their meaning: they are not waiting on Phase 1, they are among the
things that would **start** it.

**Tiers are deliberately unchanged.** A tier says *how bad if it fires*; dormancy says *whether it can
fire now*. Collapsing the two would either understate the severity of real risks or overstate the
urgency of parked ones. This is **§10.1's own move applied to this register**: `obliges_consumers_since`
separated an edition's size from whether it asks anything of you, and tier alone had the same gap.

**Why this is a marker and not a deletion.** Every one of these becomes immediately relevant the day
the trigger fires — that is what a register is *for*. What they should not do meanwhile is compete
for attention with entries that have already fired, several of them more than once.

The live set is therefore **37 concerns**, not 52.

**Every number in this section is derived, not authored** — reproduce it rather than trusting it:

```
grep -B14 '^> \*\*Dormant\*\*' reports/technical_risk_register.md | grep -o '^### [CD]-[0-9]*'
```

Stated because the alternative is what this register spent v1.4.0 learning. The count appears in the
header, twice in this section, and as an enumerated list — **four hand-maintained statements of one
derived fact, compared to each other and to nothing else, which is C-53's shape.** It was introduced
here while resolving C-53, caught by `review-diff` on this section's own branch, and is left visible
rather than tidied: the list is a convenience for reading, the markers are the source of truth, and
when they disagree **the markers win.**

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

The package's defining constraints — exactly one runtime dependency (`appwrite>=5.0.0`), zero VIEWS domain logic, and no environment-variable loading inside the package — are asserted only as prose in "What This Package Does NOT Contain" (`README.md:106-119`). The README's own R5 (`README.md:572`) identifies scope creep as "the most likely way this package fails long-term." Without an import-linter rule, a dependency allowlist in CI, or a grep gate for `os.getenv`, nothing prevents a future PR from adding pandas, a domain schema, or hidden `.env` coupling. This raises cost of change for every future maintainer. Currently mitigated by the prose contract and the Decision Log (D2–D4, `README.md:599-601`).

**Falsification evidence (2026-06-12, probe P3):** CI is *presupposed* five times in the corpus ("run in CI", "skipped in CI" — `README.md:236,491,525`, ADR-005:93-94) but specified zero times — no CI system, workflow content, lint configuration, or Python version matrix exists in any document, so this concern's own trigger cannot be satisfied from the docs as written. The gate must be authored, not transcribed. Enforced by failing stub `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_03_ci_gate_is_specified`.

**What that stub asserts changed on 2026-08-09 (C-68), and the change matters to this entry.** It
previously asserted only that *some* workflow file existed — which the secret scan satisfied, turning
it green while C-02 was untouched. It now requires the workflow set to run **`ruff` and `pytest`**,
matching its own docstring. So it is red again for the right reason, and **C-02's trigger is now
carried by a stub that tests the thing C-02 is about** rather than the existence of a file. Closing
C-02 still needs the gates themselves, which remain deferred with the scaffold (#8).

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

The two source repos define `AppwriteConfig` with different fields: pipeline-core has `timeout_seconds` but not `connect_timeout_seconds`; both pass a `path_manager: ModelPathManager` that the extracted package intends to replace with `cache_dir: Optional[Path]` (roadmap Decision Log #4, `README.md:601`). The new config must be a superset (`README.md:421`), and every construction site across at least three repos must change `path_manager=...` to `cache_dir=path_manager.cache / "appwrite"` (`README.md:383,422`). A missed call site fails at construction time (`TypeError`) — but the silent path is what grounds Tier 2: if the superset config quietly redefines a field's default or semantics between the two source variants (e.g. differing timeout defaults), consumers get changed runtime behavior with no error at all. This is structural fragility with a concrete migration trigger. The README proposes a transitional config accepting both fields (R6 mitigation, `README.md:582`) — not yet implemented.

**Falsification evidence (2026-06-12, probe P6):** the divergence already exists *inside this repository's own docs* — four partial, disagreeing field enumerations: `README.md:57` (has `auth_method`, cache TTL, timeout; omits `cache_dir`), the canonical example `README.md:268-276` (7 fields; omits `auth_method`, TTL, all timeouts), ADR-009:41 (adds `cache_dir`, plural "timeouts"), and `README.md:501` (derived `bucket_name`/`database_name` fields appearing in no list). No authoritative enumeration exists from which even a class stub could be written; candidate ADR-012 is the natural home. Enforced by failing stub `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_06_appwriteconfig_has_single_authoritative_field_list`.

---

### C-05: Duplicated Appwrite clients drift, and cloning faoapi adds further copies

| Field | Value |
|-------|-------|
| ID | C-05 |
| Tier | 2 |
| Source | repo-assimilation (2026-06-11) |
| Trigger | **(a)** When a bug is fixed in one Appwrite client copy, check whether the other copy has the same bug. **(b)** When `views-faoapi` is cloned for a new consumer API, confirm whether the clone copies the Appwrite client again — *(b) fired on 2026-08-01 when views-crafdapi was cut, and Decision Log #11 reclassified it: the trigger counts consumer APIs, not copies, so it is one clone short rather than met.* |
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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

Migrating `views-pipeline-core` to depend on `views-appwrite` requires buy-in from a different maintainer who may prefer to keep their own copy (R3, `README.md:560-564`). This is a coordination/process risk rather than a code-quality defect, so it is registered at Tier 4. It does not block the rest of the plan: the README notes consumer APIs can adopt `views-appwrite` regardless, and pipeline-core can migrate later (`README.md:564`). Currently mitigated by the documented framing strategy (present as a benefit: free SDK-14 compat, fewer lines to maintain).

---

### C-09: `validate_docs.sh` checks are narrower than a green run implies — and a green run cannot show which of them looked at anything

| Field | Value |
|-------|-------|
| ID | C-09 |
| Tier | **3** (raised from 4 on 2026-08-14 — see the exposure change below) |
| Source | repo-assimilation (2026-06-12); **extended repo-assimilation (2026-08-14), measured** |
| Trigger | When the first project-specific ADR (011+) is written, or ADR-004 is activated out of Deferred status, extend the pattern beyond `ADR-00[0-9]` and include Deferred files in the placeholder scan. **And when the first CIC is authored in Phase 1** — that is the moment check 2 first has an input, and the moment someone first trusts it. |
| Location | `docs/validate_docs.sh:60` (pattern `ADR-00\K[0-9]`), `:36` (Status filter excludes `Deferred`), `:24-35` (placeholder checks), **`:41-52` (check 2, zero inputs today)**, and the silent-success paths in checks 2, 3, 4, 6 and check 8's per-file loop |

The script was inherited from the base_docs template when only constitutional ADRs (000–009) existed. ADR-010 now exists and is referenced from `reports/technical_risk_register.md:144` and `docs/ADRs/README.md:32`, but the cross-reference check at `validate_docs.sh:60` only matches `ADR-00[0-9]`, so a phantom reference to ADR-010 — or to any of the candidate ADRs 011–015 anticipated in `docs/ADRs/README.md` — passes validation silently. The placeholder scan likewise only examines files whose Status is Accepted/Active, excluding the Deferred ADR-004. The failure mode is a false "PASSED" from the repository's only mechanical documentation gate. Currently mitigated only by manual review of cross-references.

See also C-02 (shared root cause: invariants asserted in prose with incomplete mechanical enforcement).

**Extended 2026-08-14 (`repo-assimilation`) — a second mechanism, measured, and the reason the tier moves.**

**Check 2 iterates over nothing and has never executed its body.** It resolves every CIC named in
`CICs/README.md` against a file on disk. Measured today:

```
grep -E '^- `[A-Z].*\.md`' CICs/README.md | grep -v '>'   ->  0 lines
```

`CICs/README.md` says *"Active Contracts — None yet"*, so the loop has no input and cannot fail. That
is **C-55's shape** — a guard that stands down whenever there is nothing to satisfy it — in the one
file C-55 did not examine, and it is off during precisely the window that matters: after the first
CIC is written and before anyone re-reads the script.

**And a green run does not distinguish "checked" from "scanned nothing".** Checks 7 and 9 print `OK:`
lines. Checks 2, 3, 4 and 6 print only on error, and check 8's loop prints only for files that differ
from `origin/main`. A full passing run therefore renders three bare headers with no verdict beneath
them. Those checks *do* have inputs today — 123 `ADR-00[0-9]` references, 8 protocol references, 3
files citing the retired name, measured — but **the output carries no evidence of that**, so a future
narrowing (a moved directory, a renamed heading, a `grep -P` unavailable on the runner) would present
identically to success. The repo's own question — *under what circumstance does this check report
success without having looked at anything?* — has an answer here that is visible only by
instrumenting the script.

**Why the tier moves from 4 to 3, on a dated change in exposure rather than a change of opinion.**
This entry was written on 2026-06-12, when this repository had **no CI at all** and the script was
something a person occasionally ran. Since 2026-08-11 (C-70's resolution) `guards (self-contained)`
runs it on every pull request and **`guards (self-contained)` is a required check**. A vacuous check
inside an advisory script is a curiosity; the same check inside a required gate is a green tick that
several contributors read as coverage. Still Tier 3 and not 2: nothing here corrupts data, and the
script's two load-bearing checks (8 and 9) are the two that were mutation-proven and that do print
their verdicts.

**Not merged into C-02.** C-02 is about invariants that have *no* mechanical enforcement. This is
about enforcement that exists, runs, is required, and is narrower than it looks.

Part of causal cluster **G** (guards that are green and blind) for the vacuity half; stays in cluster
**A** (corpus freshness) for the `ADR-00[0-9]` half. Cross-refs: **C-55** (the same skip-into-dormancy
shape), **C-70** (what made this a required gate), **C-77** (the same defect one layer up, in the
workflow rather than the script).

---

### C-10: ADR numbering scheme is stated inconsistently across three documents — RESOLVED

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

Zero mentions of a software license, a supported Python version range, or `.gitignore` content exist in the documentation, and none is explicitly scoped out. (**Update 2026-06-12:** the `.gitignore` half self-demonstrated — commit `1e54734` accidentally swept `tests/__pycache__/*.pyc` into history; a minimal `.gitignore` was added immediately after. License and `requires-python` remain open for the scaffold session.) The falsification dry-run (probe P1) built a wheel from documented values only: it succeeded, but the artifact was tagged `py2.py3-none-any` — with no Python floor specifiable, the package silently claims Python 2 compatibility, a wrong-by-default installability claim that surfaces as confusing downstream failures rather than a clean resolver error. For an org-distributed, pip-installable package (`README.md:326-328`), the missing license decision is reviewer-blocking. Tier 3: affects every consumer repo and contributor but fails loudly-ish at review/install time rather than corrupting data. Enforced by failing stubs `test_falsify_01_scaffold_buildable_without_invented_values` and `test_falsify_05_license_and_python_floor_decided`.

---

**Update 2026-08-11 (`repo-assimilation`) — two of the three are now decided, the third is not, and
the stub went green on the partial.**

| Item | State |
|---|---|
| **License** | **DECIDED** — `LICENSE` (MIT) added when the repo went public 2026-08-08 |
| **`.gitignore`** | **DECIDED** — present and tracked; it also carries the `CLAUDE.md` de-tracking note |
| **Python floor** | **STILL UNDECIDED** — no `pyproject.toml`, `setup.py`, `setup.cfg` or `requirements*.txt` exists anywhere in the repo |

The floor is not merely unstated, it is **contradicted in practice**: the guards need >= 3.11 for
stdlib `tomllib` and fall back to `tomli` below it, CI pins 3.12 explicitly in both guard jobs, and
the local interpreter is 3.10.14. Three different answers, none of them declared.

**And this is a C-68 event on this entry's own stub.**
`test_falsify_05_license_and_python_floor_decided` is **GREEN** today. Its name conjoins two
conditions; only one of them became true. A stub that passes when half its subject is resolved is
the exact shape C-68 registers — an assertion weaker than its own name — and it is one of the six
green stubs C-68 asks someone to audit. **Audit this one by reading it, not by trusting the colour.**

### C-19: Public API surface contradiction — `_as_dict`/`_get` are simultaneously internal and a documented consumer import

| Field | Value |
|-------|-------|
| ID | C-19 |
| Tier | 3 |
| Source | falsification-audit (2026-06-12) |
| Trigger | When writing `__init__.py` and naming the compat functions during the Phase 1 decomposition, resolve whether `_as_dict`/`_get` are public API (rename without the underscore prefix and export them) or internal (give consumers a public wrapper); update `README.md:382` and the Phase 2 migration instructions accordingly. |
| Location | `README.md:222,261-265` (3-name public surface, "Everything else is internal"), `README.md:382` (Phase 2: consumers "must" import `_as_dict`/`_get` from `views_appwrite.compat`); ADR-001 Category 4 (compat's public effect is dicts, implying no direct consumer access) |

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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

> **Dormant** — the trigger above cannot fire until Phase 1 extraction begins, which is deferred
> behind roadmap Decision Log #11 (three consumer APIs; currently two). **Tier is unchanged**: it
> states severity if this fires, not urgency today.

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
| Trigger | **Cutting `views-productionapi`**, which inherits whatever default the org carries — or **making any further repository public**, which is when the absent control next matters. *(The former second clause, "any decision to treat a clean scan as evidence", was perpetual: it describes a standing limit, not an event. That limit is now stated in `.gitleaks.toml` and in the surviving text of contract §5.7 — "a clean scanner run is a floor, not a proof".)* |
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

> **STATUS 2026-08-08 — the repository went public; this concern got *worse*, not better.**
>
> On going public, `secret_scanning` and `secret_scanning_push_protection` were enabled on this repo.
> **`secret_scanning_non_provider_patterns` could not be enabled** — and the way it failed is the
> point. `PATCH /repos/.../security_and_analysis` with that field returns **HTTP 200 and the full
> repository object, with no error**, and the setting stays `disabled`. The API accepts the request
> and does nothing. Re-reading the state is the only way to find out; a script that trusted the 200
> would report the þing-02 condition satisfied when it is not.
>
> Same for `secret_scanning_validity_checks`. Org-level defaults are `secret_scanning: false`,
> `push_protection: false`, and non-provider-patterns is not even a settable org field
> (`npp: null`) — so C-30's original framing, that the gap is an org-level default, holds.
>
> **CORRECTED 2026-08-08 — it is not an unflipped switch. It is not purchasable on this plan.**
>
> The organisation is on GitHub's **free** plan (`orgs/views-platform.plan.name = "free"`, 18 seats).
> `secret_scanning_non_provider_patterns` is part of **GitHub Secret Protection**, a paid product.
> Hence all three symptoms: the toggle is absent from the repo's Advanced Security page, the API
> accepts a PATCH and silently ignores it, and the org-level field reads `null` rather than `false`.
>
> **This entry was previously written as an operator oversight. That framing was wrong**, and it sent
> the operator hunting for a control that does not exist for them. The gap is a purchasing decision,
> not a configuration one.
>
> Partially compensated in-repo by **C-67**: `.gitleaks.toml` widens the CI scan to catch this
> platform's key shape in prose and notebook cells, which provider-pattern scanning misses. That
> covers the *key* half of þing-02's condition. It does not cover a **prose password**, which is the
> other half and the class views-datafactory actually leaked.

Cross-refs: views-appwrite#12 G2(d) (operator), C-29 (same sweep), þing-02 S32, C-67.

---

> **Numbering note.** The next ten entries start at **C-51**, not C-31. `C-31`–`C-41` were allocated
> by the `/falsify` audit of 2026-07-31 (they name the stubs in
> `tests/test_falsification_thing02_contract.py`) but were never written into this register, and
> `C-47`/`C-50` appear here only as cross-references into **views-models'** register. Reusing any of
> those numbers would make a citation ambiguous about which register it means. The gap is deliberate.
> Registering C-31–C-41 properly is separate outstanding work.
>
> **Audited 2026-08-14 (`review-rr`): the note explained 13 of the 20 missing numbers.**
> `C-42`–`C-46`, `C-48` and `C-49` were **never allocated to anything** — no audit claimed them, no
> entry cites them, and no foreign register uses them. They are simply unused. Stated because the
> whole purpose of this note is to make a gap *deliberate rather than accidental*, and seven numbers
> with no recorded reason defeat it: the next person cannot tell an unused number from a lost entry.
> **None of the twenty may be reused**, allocated or not — a citation that resolves to two different
> things in two different years is the failure this convention exists to prevent.
>
> Verified by search rather than recalled: `C-31`–`C-41` appear in this file **only inside this note**,
> so nothing anywhere cites an entry that was never written.

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

### C-52: The reader-agreement guard is vacuous — it points at a path that does not exist and grades two identical clones — RESOLVED

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

---

### RESOLVED 2026-08-14 (`review-rr` strategic) — the fix shipped and was never recorded here

**This entry sat at Tier 1, open, describing a defect that had already been fixed.** Found by a
strategic review reading the entry against the code, not by anything failing. Recorded in place
rather than moved, because the trap-on-repair paragraph above is the part worth keeping.

| The claim | State on 2026-08-14 |
|---|---|
| *"`READER_PATHS` names `views-models/tools/registry_to_env.py`. That file does not exist."* | **Corrected.** `tests/test_registry_readers_agree.py:73` names `tools/credentials/registry_to_env.py`, with the C-52 history in a comment above it |
| *"`_present()` … drops missing readers **silently**"* | **Guarded.** `test_every_declared_reader_path_resolves` distinguishes *repo absent* (fine) from *repo present, reader absent* (error) |
| *"all four tests grade only views-faoapi and views-crafdapi"* | **Guarded twice.** `_require_two_readers()` fails under CI, and `guards.yml`'s *Refuse to run against fewer readers than we cloned* fails **before** pytest |
| Proven, not asserted | C-70's resolution table records the CI mutation: *"clone one sibling instead of two → `guards (cross-repo)` **FAILED** — at the anti-vacuity gate, before pytest, naming the missing reader"* |

**What is NOT closed by this, and moved rather than lost.** The *local* path still tolerates ambient
state — the interpreter is discovered by globbing sibling virtualenvs, so a laptop run and a CI run
compare different reader sets. That is **C-79**, registered separately on 2026-08-14. And the
divergence this guard was built to detect is real and still open: **C-51**, held by the two
`xfail(strict=True)` ratchets.

**Why this mattered while it stood.** C-52 was one of three Tier 1 entries. Anyone reading this
register to decide what is dangerous met a fixed defect at the top of the list — the register doing
to its reader what **C-76** did to consumers.

Cross-refs: C-51 (the divergence, still open), C-29, C-79 (the residual, local-only), D-05,
epic #26 story S6 (#28), C-76 (same shape, outward).

---

### C-53: Four coordinates were added with no version bump, defeating the one cross-repo drift detector — RESOLVED

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

---

### RESOLVED 2026-08-14 (`review-rr` strategic) — the entry said "Fixed in v1.4.0" and then stayed open

The narrative above already recorded the fix and the three drafts it took. **It never said what
remained, so nothing did, and the entry stood at Tier 2 for eleven days describing a closed defect.**

**What closed it.** `docs/validate_docs.sh` check 8 compares the version **value** across revisions
(`_version_of origin/main` vs the working tree) for the contract, the registry and the deployment
pattern. Mutation-proven in CI and recorded in C-70's resolution table: *"registry changed with no
version bump → `guards (self-contained)` **FAILED** on check 8"*. Draft 3's discrimination — value,
not line-touched — is what makes it answer the question consumers actually ask.

**The residual went to its own entries rather than keeping this one open.** Three consumers resolving
through `/blob/main/` is **C-72** (pin incoherence, consumer side) and **C-73** (the publisher
believing every consumer pins by immutable tag — which is the discovery that a *correct* bump still
breaks a consumer comparing against a moving branch). Neither is this entry's subject.

Cross-refs: C-29, C-52, C-55, **C-72**, **C-73** (where the residual lives), seam contract §10,
`test_falsify_c40_*`.

---

### C-54: The load-bearing C-29 warning now asserts the opposite of the data beneath it — RESOLVED

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

---

### RESOLVED 2026-08-14 (`review-rr` strategic) — rewritten as a rule about the file, and then guarded

**Closed by registry v1.4.0**, whose amendment log names this entry as the reason: *"Standing
reservation rule — rewritten as a rule about the file rather than a note about four particular
entries, after it inverted against its own data (C-54)."*

The block today opens *"HOW TO RESERVE A COORDINATE THAT HAS NO VALUE YET — READ BEFORE ADDING ONE"*,
states it is a standing rule about the file's shape, and says plainly that **there are currently no
reserved slots** — the state that used to make it read as stale. The word *"THESE"* that pointed at
nothing is gone.

**And it is guarded, which is why this closes rather than merely being tidied.**
`tests/test_registry_reader_contract.py::test_the_reservation_rule_is_still_written_down` pins the
four tokens that cannot be rephrased away — `[planned.*]`, `registry_to_env.py`, `2186d45`, `C-51` —
chosen deliberately as the shortest needles carrying each fact, so the guard does not cry wolf at
innocent rewording.

**Proven, not asserted — mutation-tested 2026-08-14, reverted, registry verified byte-identical.**
The first draft of this resolution closed the entry on the guard being *green*, which is the thing
this repository does not accept. Three mutations, each on the pristine file:

| Mutation | Result |
|---|---|
| `2186d45` → `XXXXXXX` (the incident) | **RED** — `missing ['the incident']` |
| `C-51` → `C-99` (the open divergence) | **RED** — names the missing label |
| `[planned.*]` → `[reserved.*]` (the table) | **RED** — names the missing label |

Each failure names *which* fact went, not merely that something did. `git diff --quiet` on the
registry confirms nothing was left behind.

**The compounding problem is also gone.** This entry recorded that an auditor could not distinguish
*"fixed"* from *"reverted"* because `[planned]` had vanished from the parsed file. The standing block
now states the empty state explicitly, and `KNOWN_TABLES` classifies `[planned]` as *"deliberately
unscanned (D-05, C-29)"* whether or not it currently holds rows.

Cross-refs: C-29, C-55 (the guard that used to skip itself when `[planned]` was empty), C-71 (the
same prose-outliving-its-data shape, still open on the registry's minimalism claim).

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

> **RECURRED 2026-08-10, one story later, in code written by the author who registered this.**
>
> The `[contract.*]` guards added for #75 both `pytest.skip` when no facts are declared — the exact
> shape of this entry, in the same file, three months of lessons later. Caught by `review-diff` on
> its own branch and fixed before merge, so it never shipped.
>
> **The fix is the same as this entry's**, which is the useful part: an always-runs companion. While
> the seam contract declares §4.1, the registry must hold at least one fact, so deleting the last row
> fails loudly instead of silently switching two guards off. Mutation-proven.
>
> **Why this is recorded rather than quietly fixed.** The entry now has evidence about its own
> stickiness: knowing the pattern, having written it up, and having built the companion-test remedy
> once was **not** enough to stop it recurring in the next thing written. That is an argument for a
> mechanical check rather than a documented habit — and the honest counter-argument is that a check
> which verifies "every skip has a companion" would itself need proving, which is the regress S6
> declines. For now the evidence is the entry.

Cross-refs: C-54, C-29, C-68 (same family: a guard that reports without establishing).

---

### C-56: The CRAFD caller key as issued cannot authenticate a single request

| Field | Value |
|-------|-------|
| ID | C-56 |
| Tier | **3** (lowered from 2 on 2026-08-14 — the defect was remediated at source 2026-08-03; what remains is a verification, not an exposure. The key now carries six console-verified scopes; only the end-to-end proof is outstanding, and views-crafdapi is not deployed) |
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

### C-63: No reader checks the registry's `[meta] version` — RULED, ACCEPTED 2026-08-13

| Field | Value |
|-------|-------|
| ID | C-63 |
| Tier | 3 |
| Source | `expert-code-review` of D-05, 2026-08-03 (Kleppmann — the only perspective to reframe D-05 this way, and uncontradicted) |
| Trigger | **RULED 2026-08-13 — the trigger is now the VOIDING CONDITION, not an open question:** a future edition that alters the semantics of `[connection]` or `[target]` — the two tables every reader scans. Growth in unscanned tables (`[contract]`, `[edition]`) does not fire it; that is why the accepted risk has held. |
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

---

**RULED 2026-08-13 (operator): the readers do NOT refuse a newer edition. Accepted risk, with the
argument recorded.** views-appwrite#45 closed.

The ruling is that adding the check would be **worse than the exposure**, not that the exposure is
negligible:

1. **Covered from the other side now.** `[meta] obliges_consumers_since` and contract §10.1
   (v1.6.0) tell a consumer when an edition asks something of it. A reader refusing on version
   fires on *every* edition, including the seven that oblige nobody — the noise #76 was filed to
   remove. A gate that cries wolf is bypassed reflexively, and that is how its one real firing goes
   unread.
2. **A fourth pin per consumer, unchecked.** Each already carries a pinned tag or version constant
   (views-faoapi `REGISTRY_PIN_TAG`, views-crafdapi `seam_contract.py`, views-postprocessing
   `SEAM_CONTRACT_VERSION`). A second "written against" number must agree with the first and
   **nothing would check that it does** — C-53's exact shape.
3. **The live instance is not a version problem.** D-05's divergence happens on the *same* edition.
   A version gate would not have caught it.

**Why the exposure shrank without anyone acting on it.** The registry's growth has been in tables
the readers structurally ignore — they scan exactly `[connection]` and `[target]`, so `[contract]`
(v1.5.0) and `[edition]` (v1.6.0) were invisible by construction. The remaining risk is narrower
than filed: a change *within* a scanned table that an old reader misreads, of which D-05 is the only
instance.

**The cheaper alternative, offered to the reader repos and not imposed.** Their ignore-list is
implicit — the comment names `excluded`, `meta`, `test_environment`, written before `[contract]` and
`[edition]` existed, so it is three tables out of date. A reader that fails on a table it has never
heard of catches the class for one line each. **This repo shipped exactly that guard on its own
side** (`test_every_table_in_the_registry_is_classified_here`, C-75, mutation-proven both
directions). Offered as a pattern; no clause, no version bump, nothing to re-pin.

**Two of #45's three questions were already answered before the ruling**, by work that did not know
it was answering them: major-vs-minor is superseded by §10.1, and the constant's location was
settled by practice in three repos.

**Stays in the register rather than moving to Resolved.** Nothing was fixed — a risk was measured,
argued, and accepted. It is retained so the next person meets the argument rather than the question,
and reopens it if the premise changes: **if a future edition alters `[connection]` or `[target]`
semantics, this ruling is void and the question returns.**

Cross-refs: C-51, D-05, **C-53** (the unchecked-second-number shape this avoids), **C-75** (the
table-classification guard offered as the alternative), seam contract §10 and §10.1, #76.

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

### C-66: The one key held by an external party is the only one that never expires

| Field | Value |
|-------|-------|
| ID | C-66 |
| Tier | 3 |
| Source | operator console read, 2026-08-05 — visible in the API-keys list the same sitting that closed A3(i) |
| Trigger | A leak, a partner offboarding, or any decision to rotate `crafd-caller-read`. None of these has a date attached, which is the concern. Also: issuing `PRODUCTIONAPI_API_KEY` the same way, inheriting the default without deciding. |
| Location | `docs/ADRs/platform/coordinate_registry.toml` — `CRAFD_CALLER_API_KEY.expiry`; Appwrite console, API keys list |

| Key | Expires |
|---|---|
| `VIEWS Pipeline Core` | 2026-11-17 12:35 |
| `UN FAO` | 2026-11-17 16:10 |
| **`crafd-caller-read`** | **never** |

**The asymmetry runs the wrong way.** The two keys under this platform's sole control expire. The
key handed to a third party does not.

Three consequences:

1. **A leak has no natural end.** The UN FAO key's leaked value is dead today only because the key
   was reissued on a 12-month term roughly three weeks after the paste, before anyone noticed —
   recorded at `FAO_CALLER_API_KEY.history_leak`. **That accident is not available here.** An
   equivalent paste of this key would still be live, indefinitely.
2. **No forcing function for rotation.** §5.1 has no propagation mechanism for a secret *value*
   (C-27). Expiry is the only thing that has ever forced the question on this platform, and this key
   does not have one.
3. **`never` was a default, not a decision.** Nothing in the record shows anyone choosing it. It is
   the field's default and nobody looked until the key list was read.

**This entry does not argue for an expiry.** A caller key that expires without coordinated handover
breaks a partner's access on a date they did not pick — which is precisely the *"free at creation, a
migration afterwards"* cost §5.3 describes, paid at the worst moment. Both answers are defensible.
**Only the absence of a decision is not.**

**Open question for the operator:** an expiry with a scheduled renewal, or a deliberate no-expiry
recorded as such with a rotation trigger that is not a date. Whichever, decide it before
`PRODUCTIONAPI_API_KEY` is issued, or the default propagates to a third external party by inheritance.

Recorded in registry **v1.4.4**. Cross-refs: C-27 (rotation has no propagation mechanism), C-65 (the
two keys that *do* expire, together), C-28, views-appwrite#12.

---

### C-67: The secret scan misses both leak shapes this platform's history actually contained

| Field | Value |
|-------|-------|
| ID | C-67 |
| Tier | **3** (lowered from 2 on 2026-08-14 — the key half was closed by `.gitleaks.toml` in the same change, verified both ways. The residual is the **prose-password** class, which no regex closes and which is a purchasing decision tracked at C-30/C-69, not an exposure this repository can act on) |
| Source | `code-review` of PR #57, 2026-08-08 — measured against gitleaks 8.30.1 with controls, not inferred |
| Trigger | Relying on a green Secret Scan as the gate for making this repository **public**, which is irreversible. |
| Location | `.github/workflows/secret_scan.yml`; fixed by `.gitleaks.toml` in the same change |

The workflow gates publication and its failure message says *"Do NOT make this repository public
until this is green."* Before trusting it, its **default** rules were measured against the same
fabricated 265-character key in four placements:

| Placement | Default rules |
|---|---|
| `APPWRITE_DATASTORE_API_KEY=<key>` | **CAUGHT** (`generic-api-key`) |
| the same key in prose — *"I ran it with `<key>`"* | **MISSED** |
| the same key inside an `.ipynb` cell | **MISSED** |
| an English-prose password | **MISSED** |

**The two missed key shapes are exactly the two classes this platform has already leaked** — the
classes þing-02 made load-bearing when it conditioned §5.7's strike on non-provider-pattern and
`.ipynb`-cell coverage (**C-30**): views-models' notebook-cell material and views-datafactory's
prose password. The UN FAO key recorded at `FAO_CALLER_API_KEY.history_leak` was **pasted into
notebook history** — so as configured, the scan would have reported *"no leaks found"* on the very
incident that gave this platform its leaked-key story.

**On the method, because it nearly produced a false finding.** The first probe used
`AKIAIOSFODNN7EXAMPLE` as its control and that came back MISSED — gitleaks allowlists the canonical
AWS example key. A null result from a probe that cannot find a known positive is evidence about the
probe. Redone with a GitHub PAT and a PEM private key as controls; both CAUGHT; only then were the
misses interpretable.

**Also established, and narrower than feared:** gitleaks *does* read `.ipynb` files — a PAT planted
in a notebook cell was caught. The gap is rule coverage for this platform's key **shape**, not
file-type coverage.

**Fixed in this change.** `.gitleaks.toml` adds an entropy-gated rule for 100+ character opaque
tokens in any context, with 40- and 64-hex shapes allowlisted so commit SHAs and the pinned
`GITLEAKS_SHA256` cannot trip it. Verified both ways: it **catches** all three key placements, and
it produces **zero findings** against this repository's real 43-commit history. The second number is
what keeps it alive — a rule that cries wolf gets disabled, and then the repo has a config that looks
like protection and is not.

**Not closed by this fix.** A prose password is still missed and no regex closes that honestly. That
is what `secret_scanning_non_provider_patterns` is for, which is why enabling it belongs to the act
of going public rather than to a follow-up. **A green run means "no findings under these rules",
never "no secrets".**

Cross-refs: C-30 (the þing-02 condition), C-68, `FAO_CALLER_API_KEY.history_leak`.

---

### C-68: A falsification stub went green without its finding being resolved

| Field | Value |
|-------|-------|
| ID | C-68 |
| Tier | 3 |
| Source | `code-review` of PR #57, 2026-08-08 — noticed because the pytest failure count moved from 10 to 9 |
| Trigger | **When the `falsification (reporting only)` job names a green stub in its summary** — that annotation is the signal this entry exists to make audible. **And: auditing the five stubs that have been green since before 2026-08-11 and remain unread** (`r2_01`, `r2_03`, `c38`, and the two below them). *Trigger widened 2026-08-14: it named only C-02's stub, while the entry had grown to cover six.* |
| Location | `tests/test_falsification_enough_info_to_set_up_repo.py::test_falsify_03_ci_gate_is_specified` |

Adding the secret-scan workflow turned this stub green. Its assertion was:

```python
assert workflows, "No CI workflow exists; ..."
```

**Existence of any workflow file.** But its own docstring states the expectation as *"A CI workflow
exists … implementing the **ruff + pytest + boundary-enforcement** gates that ADR-005 and C-02
demand."* The secret scan runs none of those. So the stub passed on a technicality while **C-02 —
"package boundary invariants are prose contracts with no mechanical enforcement" — was untouched.**

That is the failure mode this register already carries three entries about (**C-52**, **C-53**,
**C-55**): a guard that reports success without establishing what it claims. Here the cost is
specific — a genuinely open concern reads as closed, and the falsification suite's whole contract is
that a stub turns green **only** when its finding is fixed.

**Fixed** by tightening the assertion to match the docstring: a workflow must exist **and** the
workflow set must run `ruff` and `pytest`. It is red again, which is the correct state, and it now
names what is missing rather than merely failing. The failure set is back to the long-standing 10.

**Deliberately not addressed here:** actually adding ruff/pytest CI. That is C-02's own resolution
and belongs with the scaffold decision (**#8**, gated on *operator ∧ test project*), not smuggled
into a secret-scan PR.

> **IT IS NOT ONE STUB. IT IS SEVEN — measured 2026-08-11 while building the reporting job (#70).**
>
> This entry was written about a single stub that went green when the secret-scan workflow landed.
> Running the suite by marker to build that job produced the real figure: **of sixteen falsification
> stubs, six are already green** — and had been, for an unknown length of time, with nothing
> reporting it.
>
> | Green stub | Plausibly resolved by |
> |---|---|
> | `test_falsify_05_license_and_python_floor_decided` | the MIT `LICENSE` landing |
> | `test_falsify_c41_readme_first_sentence_is_true` | epic #14 S3 rewriting the first sentence |
> | `test_falsify_c38_conformance_vector_released_with_its_consumers` | the conformance vector shipping |
> | `test_falsify_r2_04_first_commit_gate_sequencing_documented` | C-22, marked resolved |
> | `test_falsify_r2_03_integration_test_isolation_specified` | unverified |
> | `test_falsify_r2_01_roadmap_consumed_source_repo_sdk_decision` | unverified |
>
> **Each is one of two things and nobody has looked**: a finding genuinely resolved, in which case
> the stub should have been converted to a plain assertion and its register entry closed — or an
> assertion weakened until it stopped failing, which is this entry's defect. **The suite cannot tell
> them apart, and neither can I without reading each one.**
>
> The `/falsify` protocol's contract is that a stub *"turns green only by fixing the finding it
> encodes"*. Green is therefore a **signal**, and for six stubs that signal has been firing into an
> empty room. The failure-count heuristic that caught the original C-68 only detects a *change*, so
> anything already green before someone started counting is invisible to it.
>
> **#70 fixes the reporting, not the backlog.** From now on a green stub is named in the CI summary
> and raises a workflow annotation. Auditing these six — resolve-and-convert, or restore the
> assertion — is separate work and is not smuggled into a CI story.

**Update 2026-08-13 — one of the six audited: `c41`, and it is the shape this entry names.**

`test_falsify_c41_readme_first_sentence_is_true` has been green since the README's opening sentence
was fixed. Audited during `review-base-docs`; **the green was accurate and almost worthless.**

| | |
|---|---|
| What it **asserts** | one regex on one line — the first prose line must not start with `"Shared Appwrite client library"` |
| What its **docstring** demands | *"the opening sentence describes what the repo IS, before it describes what it may become"* |

The sentence was corrected; the *property* was not. The README remained **807 lines, of which 731
described what the repo may become** — so the document still failed the docstring's expectation
while the stub reported success. **An assertion narrower than its own docstring**, which is exactly
what this entry registers.

**Not weakened deliberately.** It was written as a probe against one specific sentence, and that
sentence was fixed. The defect is that a stub about a *document's shape* was implemented as a check
on *one line*, and nothing marked the gap.

**Resolved by the artifact rather than the test.** The README is now 106 lines, with the roadmap at
`docs/roadmap_shared_client.md` (**C-76**), so the docstring's property now holds. The assertion was
left unchanged: encoding "shape" needs a threshold nobody can defend, and this paragraph is the
honest record.

**One thing the audit caught that the stub could not.** Splitting the file flipped a *different*
stub — `r2_01` — from green to red, because two modules read `README.md` at module scope for content
that had moved. A **false red**, fixed by having them read both files, verified by the failure set
returning to 10 and the green set being identical. **Caught only because the baseline was re-checked
after the change** — this cluster's own lesson, arriving from the opposite direction.

**Five of the six remain unaudited.**

Cross-refs: C-02, C-52, C-55, C-67, **C-76** (the README defect this audit surfaced), #8, #70.

---

### C-69: þing-02 struck §5.7 in favour of a replacement that is not available on this plan

| Field | Value |
|-------|-------|
| ID | C-69 |
| Tier | 3 |
| Source | discovered 2026-08-08 while enabling scanning on going public; the plan limitation is the new fact |
| Trigger | Anyone relying on §5.7's strike as settled — or citing S32's withdrawals as unconditional. Also: the next repo made public, which inherits the same absent control. |
| Location | `docs/ADRs/platform/appwrite_seam_contract.md` §5.7; þing-02 `sáttmál.md` S32, `dómr_endurmat.md:147`, `rýni_00.md:118` |

**What §5.7 said**, before it was struck: *"Two mechanical checks, in every repo on the seam: a
secret scan and a registry check."*

**Why it was struck (D5),** in its own words: secret scanning does not cross the Appwrite seam, so
it is not this contract's to impose — and *"an organisation-level setting reaches **all 16 public
repos**; a seam contract reaches **6** … A clause covering a third of the problem while reading as
coverage is worse than no clause."* The replacement is named explicitly: *"an **organisation-level
default**, not a clause, and it is an operator action."*

**The new fact.** Part of that replacement **cannot be bought on the current plan.** The org is on
GitHub free. `secret_scanning` and `secret_scanning_push_protection` are available and are now on
for this repo. `secret_scanning_non_provider_patterns` — the specific control both withdrawing seats
named — belongs to the paid Secret Protection product.

**Why this is smaller than it first sounds, stated so nobody over-reacts:**

1. **The strike's core reasoning is untouched.** Secret scanning still does not cross the seam, and
   an org default still reaches more repos than a clause could. D5's argument was never *"because
   this specific flag is free"*.
2. **What §5.7 would have mandated is happening anyway, voluntarily.** §5.7's own closing line —
   *"Where a repo wants a mechanical check of its own, that is its own business"* — is exactly what
   views-appwrite and views-models have each now done, with a full-history gitleaks gate.
3. **The contract already refuses to treat a clean scan as proof.** The text surviving the strike
   says *"A clean scanner run is a floor, not a proof"* and names **prose** as limit (i), citing a
   working password that sat in an English sentence across three commits unflagged. The unmet
   condition does not contradict that sentence — **it is that sentence.**

**What is genuinely open:**

- **S32's withdrawals were conditional and the condition is now unmeetable without spending money.**
  Two seats gave up a clause on a promise that cannot be kept for free. They are entitled to know.
- **Prose passwords remain uncovered platform-wide.** C-67's rule closes the *key* half in this
  repo's CI; nothing free closes the prose half, and that is the class views-datafactory actually
  leaked.
- The gap is **org-wide, not this repo's** — 16 public repos, of which this is one.

**Three honest options, none urgent:** buy Secret Protection; record the gap as knowingly accepted
and let the per-repo CI gates carry it; or re-open D5 at a þing on the ground that its replacement
did not materialise. **Nothing is exposed today** — this repository's full history scans clean under
both the default rules and C-67's widened rule.

Cross-refs: C-30 (the flag itself), C-67 (what covers the key half), þing-02 D5 and S32.

---

### C-70: The repo now has CI, and it does not run any of the guards that protect the registry — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-70 |
| Tier | 2 |
| Source | `repo-assimilation`, 2026-08-08 |
| Trigger | The next PR that edits `coordinate_registry.toml` — including the one that declares `views-productionapi`'s slots, which this registry already anticipates. CI will show a green tick having checked nothing about the registry. |
| Location | `.github/workflows/` (one workflow only); guards at `tests/test_registry_reader_contract.py`, `tests/test_registry_readers_agree.py`, `docs/validate_docs.sh` checks 7–8 |

`secret_scan.yml` is the repository's only workflow. It scans git history for credentials. It does
**not** run `pytest`, and it does **not** run `validate_docs.sh`.

> **PARTIALLY ADDRESSED 2026-08-10 — `guards.yml` landed (S2, #68). This entry stays OPEN.**
>
> The paragraph above is no longer true as written and is kept for the record. There are now two
> workflows: `guards (self-contained)` runs the 5 registry-shape guards, the 2 test-kind meta-guards,
> and all 8 checks in `validate_docs.sh`.
>
> **What is now covered**, mutation-proven before merge: a value-less `[target]` entry — the
> `2186d45` shape that caused C-29 — turns the job red; a registry change with no version bump turns
> it red; `validate_docs.sh` check 8 **errors instead of skipping** when `origin/main` is unreachable
> and `CI` is set, which is the default state after `actions/checkout` and would otherwise have been
> a green tick with C-53's guard inert.
>
> **What is still open, and why the entry does not close here:**
>
> 1. **The new job is not a required check.** The ruleset still requires only
>    `gitleaks (full history)`, so a red `guards` job does not block a merge. Until it does, the
>    concern's own sentence — *"would merge with a green tick today"* — remains literally true.
> 2. **The cross-repo guard still runs nowhere.** `test_registry_readers_agree.py` needs sibling
>    checkouts; that is S3 (#69), and it may be **obsoleted rather than completed** — ADR-017's
>    declare-the-semantics rule applied to reader *behaviour* is D-05, and settling that would remove
>    the need for a cross-repo checkout at all.
> 3. **The workflow has been proven at the step level, not on a runner.** A workflow only proves
>    itself in CI, which is what this branch's PR is for.
>
> **Closes at S5 (#71)**, after each job is shown to bite in CI and the blocking ones are made
> required. Marking it resolved now would be the thing this entry is about.

---

### RESOLVED 2026-08-11 (S5, #71) — proven by mutation, not by inspection

**The required-checks list now reads:**

```
gitleaks (full history)
guards (self-contained)
guards (cross-repo)
```

`falsification (reporting only)` is deliberately **absent**: its stubs are red by design and a
blocking job would make deleting one the fastest way to ship, which carbon protocol §1-2 forbids.

**Every claim below was observed in CI, on a real pull request, and reverted.**

| Mutation | Result |
|---|---|
| value-less `[target]` entry — the `2186d45` shape | `guards (self-contained)` **FAILED** on `test_every_reader_scanned_entry_has_a_value` |
| clone one sibling instead of two | `guards (cross-repo)` **FAILED** — at the anti-vacuity gate, *before* pytest, naming the missing reader |
| registry changed with no version bump | `guards (self-contained)` **FAILED** on check 8 (proven earlier, PR #80) |
| `CI=1` with no `origin/main` | `validate_docs.sh` **exit 1** rather than SKIP |
| a falsification stub turning green | job stays **green**, names the stub in the summary, raises a `::notice::` |

**The acceptance test for the whole epic, which nothing but a real PR can demonstrate:**

> A pull request carrying a value-less `[target]` entry reported
> **`mergeStateStatus = BLOCKED`**. Reverting the entry returned it to **`CLEAN`**.

So the concern's own sentence — *"commit `2186d45` would merge with a green tick today"* — is now
false, and demonstrably so rather than by assertion.

**What this does not close.** `views-faoapi` is still absent from the cross-repo comparison: it is
private, and #73's credential was withdrawn on views-postprocessing ADR-017 §9 because a lapsed
token makes checks skip while the build stays green. **Two of three readers are compared**, the job
says so in its log, and **C-51** tracks the remainder. An accepted gap, stated; not a silent one.

**Four traps surfaced while building this, none visible from the issue text.** Siblings inside the
workspace made pytest collect *their* suites; a partial sibling set was still a vacuous pass that
merely looked diligent; views-models' `main` carries no reader at all (407 commits behind); and
views-crafdapi's git-LFS shapefiles failed the clone outright. Each was found by running it.

So every mechanical guard this repository has built runs **only on a laptop, or not at all**:

| Guard | Protects | Runs in CI? |
|---|---|---|
| `test_every_reader_scanned_entry_has_a_value` | the C-29 invariant — a value-less `[target]` entry kills every reader | **no** |
| `test_no_secret_carries_a_value` | secrets never appear as values | **no** |
| `test_all_present_readers_*` | the three readers still agree | **no** |
| `validate_docs.sh` checks 7–8 | contract/registry version lockstep; content cannot change without a version bump | **no** |
| `secret_scan.yml` | no credentials in history | yes |

**The specific failure this permits.** Commit `2186d45` put four value-less slots in `[target]` and
made the registry unreadable platform-wide for a day (**C-29**). The guard written afterwards would
catch it — but only if someone runs `pytest` locally before merging. Under the new ruleset, the
required status check is the **secret scan**, so that exact commit would merge with a green tick
today.

**Why this is worse than having had no CI at all**, and why it is Tier 2 rather than 3: until
2026-08-08 nobody could believe this repository was mechanically covered, because it visibly had no
workflows. It now has one, a green tick on every PR, and a ruleset that makes that tick *required*.
The appearance of coverage arrived without the coverage. That is the same shape as **C-68**, one
level up — a check that reports success without establishing what a reader assumes it established.

**Not proposing the fix here** (assimilation does not propose fixes), but noting the constraint that
makes it non-trivial: `test_registry_readers_agree.py` reads sibling repositories from the
filesystem and skips when they are absent, so a naive `pytest` step in CI would pass **vacuously** on
a runner that has only this repo checked out. Adding CI without addressing that reproduces the
problem in a new place.

Cross-refs: C-02 (the broader "rules enforced by prose" concern this is a concrete instance of),
C-29 (the outage the unenforced guard exists to prevent), C-52 and C-68 (guards green and blind),
C-53.

---

---

### C-71: Two posture statements were falsified by the repo's own first workflow

| Field | Value |
|-------|-------|
| ID | C-71 |
| Tier | 3 |
| Source | `repo-assimilation`, 2026-08-08 |
| Trigger | **When the next workflow, test or check is added** — re-read `coordinate_registry.toml:10-12` before merging. Its *"no tooling, no generators, no CI attachment"* is already false and gets falser with each one. *(The README half of this entry is closed — see the narrowing below — so the trigger no longer names it.)* |
| Location | `README.md:672`; `docs/ADRs/platform/coordinate_registry.toml:10-12` |

Two claims went stale the moment `secret_scan.yml` landed, and both sit in the sentences most likely
to be quoted:

**`README.md:672`** — *"**What is parked.** Everything else. No `src/`, no `pyproject.toml`, **no
CI**, by recorded decision — not by neglect."* There is now CI. The rest of the sentence remains
true and its reasoning is intact; only the two words are wrong, which is precisely what makes them
survivable and therefore persistent.

**`coordinate_registry.toml:10-12`** — *"Deliberately minimal (`dómr_endurmat` E3): **no tooling**,
no generators, no CI attachment."* ~~Four~~ **Three** files in this repository read the registry today:
`docs/validate_docs.sh`, `tests/test_registry_reader_contract.py`, and
`tests/test_registry_readers_agree.py` (fixtures only, plus the sibling readers it executes). **The "no
tooling" half was already false before today** — the tests and the version checks are tooling — and
today's workflow makes the "no CI attachment" half harder to read charitably.

> **Corrected 2026-08-14 (`repo-assimilation`).** This entry said **four** files and named
> `tests/test_falsification_thing02_contract.py` as the fourth. It does not read the registry.
> `REGISTRY = PLATFORM / "coordinate_registry.toml"` is defined at line 42 of that module and
> **referenced nowhere** — a dead constant that reads, on inspection, exactly like a reader.
>
> The correction is small and the shape is not: this entry is *about* a claim outliving the state it
> described, and it made one of its own, in the same sentence, by counting an import-looking line
> instead of a use. Left as a strike-through rather than a silent edit, per §10's habit. The dead
> constant itself is a Tier-4 observation and is recorded here rather than as its own entry.

Registered as one entry rather than two: same defect (a posture statement outliving the state it
described), same cause (a change that nobody thought of as touching prose), different files.

This is the fourth instance in a fortnight of a claim hardening past its truth — after **C-53** (a
version that could stand still through a content change), **C-64** (a docstring citing a verdict
that did not say what it claimed), and **C-65** (a relayed key expiry that was thirteen days wrong).
The pattern is not carelessness about prose; it is that **no check reads prose**, so only a human
re-reading it can catch these.

**Narrowed 2026-08-14 (`review-rr` strategic) — one half is closed, the other is more false than when
it was written.**

| Half | State |
|---|---|
| `README.md` — *"no CI, by recorded decision"* | **CLOSED.** The README was rewritten to 106 lines under **C-76** on 2026-08-13; the CI paragraph now describes three workflows and three required checks, and `validate_docs.sh` check 9 guards the pinning claim beside it |
| `coordinate_registry.toml:10-12` — *"no tooling, no generators, no CI attachment"* | **OPEN, and worse.** Three files in this repository read the registry, two CI jobs exercise it on every pull request, and its shape is asserted by eleven guards. The sentence has not moved since it was written |

**Why the surviving half is worth keeping open rather than just fixing now.** It is the registry's
own self-description, in the file six repositories read. The claim is inherited from `dómr_endurmat`
E3 — *"no tooling, no generators, no CI attachment"* — which was a **ratified decision about what not
to build**, and is still the right decision. What decayed is its use as a **description of the
present**. Correcting it means separating the standing rule from the stale status line, which is a
small edit to a file that versions in lockstep with the contract — so it rides the next edition
rather than being smuggled in.

Cross-refs: C-53, C-64, C-65, **C-54** (the same failure inside the registry's own warning block —
now resolved, which is the model for closing this one), C-70, **C-76** (which closed the README half),
**C-81** (the registry being invisible to tooling that reads by file type — the same file, the
opposite problem).

---

### C-72: Pin incoherence is platform-wide, and one repo has the only test for it

| Field | Value |
|-------|-------|
| ID | C-72 |
| Tier | 2 |
| Source | `repo-assimilation`, 2026-08-08 — measured across all six consumer repos |
| Trigger | Any consumer upgrading its pin, or any audit asking "which edition is this repo actually conformant to?" A partial repoint is the specific hazard, and it has already happened twice. |
| Location | views-crafdapi (`README.md:17`, `docs/ADRs/README.md:156`, `docs/ADRs/active/035_*.md`); views-postprocessing (`docs/ADRs/013_*.md:735,738` vs `views_postprocessing/{crafd,unfao}/appwrite_env.py`); views-datafactory |

Measured today, not inferred:

| Repo | Pins found | State |
|---|---|---|
| views-pipeline-core | `appwrite-seam-v1.4.1` | **coherent** — one tag, everywhere |
| views-models | `856d617` | coherent (= v1.3.0, now tag-resolvable) |
| views-faoapi | `60674b2c…` | coherent, but **v1.0.0 — four versions stale** |
| **views-crafdapi** | `60674b2c…`, `platform-001-v1.2.0`, `appwrite-seam-v1.4.4` | **three simultaneous pins** |
| **views-postprocessing** | `90fc105`, `fcf32c9` | **two simultaneous pins** |
| views-datafactory | `/blob/main/` | **not a pin** |

**The partial-repoint hazard, demonstrated.** views-crafdapi updated `ADR-035` to
`appwrite-seam-v1.4.4` — correctly, and in response to a review — but left `README.md` at
`platform-001-v1.2.0` and `docs/ADRs/README.md` at a v1.0.0 commit. Each of the three is internally
consistent and individually defensible; nothing in that repo is visibly wrong. views-postprocessing
has the same shape: its code was repointed and its ADR was not.

**views-pipeline-core is the only repo that can detect this.** It hit exactly this problem in #402,
found its pin lived in **eleven** places, and built `tests/test_seam_contract_pin_is_coherent.py` —
which scans for pins rather than listing them, asserts they name a single tag, and deliberately does
**not** check freshness, because §10 reserves the upgrade decision to the consumer. Its own summary
of why it went unnoticed for three versions: *"There was no state a reader could look at and call
wrong."*

**Why this is this repository's concern despite living in others.** Seam contract §10 already places
the obligation on consumers and scolds them for pin decay — but this repo publishes the thing being
pinned, cut the tags that made upgrading possible only on 2026-08-03, and is the only place that can
see all six pin states at once. §10's own text records the decay without recording that the pins are
also *internally inconsistent*, which is a distinct and more deceptive failure than being stale.

Cross-refs: seam contract §10, C-53 (the version bump that makes a pin meaningful),
views-pipeline-core#402 and its coherence test as the reference implementation.
**C-73** — the same subject from the publisher's side.

---

### C-73: We version this registry believing every consumer pins by immutable tag. One does not, and we broke it for a day without noticing

| Field | Value |
|-------|-------|
| ID | C-73 |
| Tier | **2** |
| Source | `manual` — found 2026-08-11 while reviewing a work request from the views-faoapi seat; the request itself asserted the opposite and was also wrong |
| Trigger | **Bumping `[meta] version` in `coordinate_registry.toml` for any reason, including a prose-only edit.** Not a future hazard — it has fired three times already (v1.5.0, v1.5.1, v1.5.2) and is latent right now |
| Location | `docs/ADRs/platform/coordinate_registry.toml` `[meta] version`; seam contract §10; the claim itself in PR #97 and PR #103 body text. The consumer: `views-postprocessing/tests/test_env_declaration.py::test_the_pinned_contract_edition_still_matches_the_registry` + `views_postprocessing/{unfao,crafd}/appwrite_env.py` |

**The false belief, in our own words.** PRs #97 and #103 both state: *"Consumers pinned at earlier
tags are unaffected because tags are immutable (§10). This is additive."* We shipped two editions on
that sentence.

**It is true of exactly one consumer.** views-faoapi reads the registry through
`git show appwrite-seam-v1.5.0:<path>` — an immutable tag, genuinely immune. We checked *that*
mechanism, found it sound, and generalised it to every consumer without looking at another one.

**views-postprocessing does not pin in that sense at all.** Its `_load_registry` reads
`(repo / _REGISTRY_RELPATH).read_text()` — the **working tree** of a sibling checkout — and its CI
checks out our `main` with `ref: main`. It then asserts `[meta].version` equals a frozen constant,
`SEAM_CONTRACT_VERSION = "1.4.4"`. So it compares **a moving branch against a fixed string**: every
edition we publish reddens it until they re-pin.

**Executed, not predicted** (their assertion replicated under Python 3.11, our `main` at v1.5.2):

```
[unfao] registry working tree = '1.5.2'  pinned = '1.4.4'  -> ASSERTION FAILURE
[crafd] registry working tree = '1.5.2'  pinned = '1.4.4'  -> ASSERTION FAILURE
```

**It went unseen for a day because of a coincidence, not a control.** v1.5.0 landed on `main`
2026-08-10 20:35; views-postprocessing's last CI run was 08:04 that morning. Nobody pushed in
between. The failure fires on their next push. **We would not have found it at all** had a request
from a third repo not sent us into their code.

**This is not their defect.** Their docstring says the strictness is deliberate — *"the edition
catches **any** other change... It fails loudly and tells you what to do rather than what broke"* —
and as a ratchet that is defensible. The defect is ours: **we are the publisher, we cut the tags,
and we asserted a compatibility property about consumers we had not read.**

**Why Tier 2 rather than 3.** It is silent from our side by construction. Our gates are all green;
nothing in this repository can go red when we break a consumer this way, because the failing
assertion lives in their suite and runs on their schedule. That is the C-52/C-55 shape aimed
outward: *a check that reports success without having looked at anything.* We have no
publisher-side observation of consumer breakage at all.

**The narrower fact worth keeping separate from the fix.** Three editions in, the *values* have
never changed — v1.5.0/v1.5.1/v1.5.2 add two `[contract.*]` rows, remove one retired `[unmodelled.*]`
entry, and edit prose. Every one of them was semantically additive for every consumer. It is the
*edition number* that breaks them, not the content. That is precisely what **#76** exists to fix
(let consumers pin an edition and mark observation-only bumps non-blocking), and this entry is the
strongest evidence yet for it.

**Fix strategy.** Not "stop bumping" — §10 requires the bump, and C-53 exists because a bump was
skipped. Three candidates, in order of honesty:

1. **Announce before merging.** The registry header already says *"Rotation of a coordinate is a
   platform event — announce before merging"*; that obligation currently covers rotations only.
   Cheapest, and entirely within this repo.
2. **#76** — the version-pinning proposal, which makes an observation-only bump non-blocking so a
   prose fix stops costing a consumer a PR.
3. **A publisher-side check** that reads each consumer's declared pin and reports which are stale.
   Tempting and dangerous: it would need every consumer checked out, and views-faoapi is private —
   the exact shape #73 was withdrawn over (**C-51**). Do not build it without solving that first.

**Told, on the day.** views-postprocessing#238 carries the failing assertion, the constants to
change, and the commit (`b703cab`). views-faoapi#379 carries the correction to their request's
claims. Neither was left to discover it.

Cross-refs: **C-72** (the same subject from the consumer side — pins internally incoherent within a
repo; this is the publisher not knowing what shape the pins are), C-53 (the bump that makes a pin
meaningful), C-51 (why a publisher-side sweep cannot see every consumer), **#76** (the proposal this
is evidence for), seam contract §10.

---

### C-74: The "secrets are never values" rule is stated by class and enforced by table, and the two sets already differ

| Field | Value |
|-------|-------|
| ID | C-74 |
| Tier | **2** |
| Source | `repo-assimilation`, 2026-08-11 — mutation-proven, mutation reverted |
| Trigger | **Giving a `value` to any entry whose declared `class` is a secret but which does not live in the `[secret]` table** — most likely when someone records the netrc credential "just so it is written down", or files a future co-resident secret under `[excluded]` because it belongs to another contract |
| Location | `tests/test_registry_reader_contract.py:259` (`test_no_secret_carries_a_value`, reads `registry.get("secret", {})`); `docs/ADRs/platform/coordinate_registry.toml` `[excluded.netrc_entry]`, `class = "secret (carrier: ~/.netrc)"` |

**The registry states the rule by class.** Its own header, in the file's most emphatic sentence:

> *"Coordinates are NON-SECRET identifiers. Secrets appear only as SLOTS (name + required scopes) — **NEVER as values. No exceptions, ever.**"*

and two lines later:

> *"class is DECLARED here, never inferred from a name's prefix or carrier."*

**The guard enforces it by table.** `test_no_secret_carries_a_value` iterates `registry.get("secret", {})` and nothing else. A secret-classed entry in any other table is outside its field of view.

**Those two sets are not equal today.** `[excluded.netrc_entry]` declares `class = "secret (carrier: ~/.netrc)"` and is the one entry the seam contract §1 calls *"the sole co-resident secret"* a full delivery runtime needs.

**Proven, then reverted.** Adding `value = "machine example.org login bob password hunter2"` to that entry:

| Gate | Result |
|---|---|
| `pytest -m guard` | **14 passed** — the baseline, unchanged |
| `docs/validate_docs.sh` | failed **only** on the unbumped version; after bumping the version, as any author making a registry edit would, it **passed** |
| full `pytest` | 10 red / 20 passed — the baseline, unchanged |

The version bump is the important half. Check 8 catches *that the file changed*; it does not care *what* changed. So the one gate that reddened does so for a reason that disappears the moment the author does the correct thing.

**The last net is gitleaks, and C-67 measured it against exactly these shapes.** A `.netrc` line and an English-prose password were the two placements gitleaks' default rules **MISSED** — they are the two classes this platform has actually leaked. The `.gitleaks.toml` rule added afterwards is entropy-gated at 100+ characters, which a netrc line does not reach.

**Tier 2, not 1.** No corruption has occurred and the entry is value-less today. It is structural fragility with a realistic trigger: the registry invites exactly this edit by carrying a secret-classed row in a non-secret table, and the file's own instruction to declare class rather than infer it makes that row look correctly filed. It is Tier 2 rather than 3 because the failure is a **secret in a public repository**, and the guard that exists to prevent it reports success without having looked.

**The enabling condition is separate and worth naming.** `class` has no controlled vocabulary. Six distinct values are in use and one is prose:

```
14 target · 7 secret · 2 connection · 2 contract · 2 policy · 1 "secret (carrier: ~/.netrc)"
```

So even a class-based guard would need to decide whether `"secret (carrier: ~/.netrc)"` is the class `secret`. Any fix must settle the vocabulary first, or it will be a guard that matches on a string nobody constrained.

**Not a variant of C-29.** C-29 is a value-less entry in a *scanned* table breaking readers — absence where presence is required. This is presence where absence is required, in an *unscanned* table, and no reader is involved at all.

Cross-refs: C-67 (the scan misses both these shapes), C-29 (the inverse defect in the scanned tables), C-30 (the paid scanning feature that is off), cluster G (a guard that reports success without having looked), seam contract §1 and §5.

---

### C-75: Nothing here notices a new table in the registry — and a consumer built that check on our file before we did

| Field | Value |
|-------|-------|
| ID | C-75 |
| Tier | 3 |
| Source | `repo-assimilation`, 2026-08-11 — mutation-proven, mutation reverted |
| Trigger | **Adding a table to `coordinate_registry.toml`** — which has happened twice in two days (`[contract]` in v1.5.0, and `[unmodelled]` removed in v1.5.1) — or a consumer asking "what tables does this file have, and which of them carry obligations for me?" |
| Location | `docs/ADRs/platform/coordinate_registry.toml`; `tests/test_registry_reader_contract.py` (`READER_SCANNED_TABLES = ("connection", "target")`, and no test enumerates the rest) |

**Proven, then reverted.** Appending a whole new table carrying a live connection-classed value:

```toml
[shadow.APPWRITE_BACKDOOR_ENDPOINT]
class = "connection"
value = "https://evil.example/v1"
```

`pytest -m guard` → **14 passed**. `validate_docs.sh` → **passed**. Nothing in this repository has an opinion about which tables exist.

**The guards know four table names between them** — `connection`, `target`, `planned`, `contract` — each hard-coded at the point of use. The registry currently has seven. `[secret]`, `[excluded]` and `[test_environment]` are partially covered or not covered at all, and no test asserts the set.

**The pointed part.** On 2026-08-11 **views-postprocessing** — a *consumer* — shipped `tests/test_env_declaration.py::test_every_table_in_the_registry_is_classified_here`, a check on **this repository's file** that fails when we add a table. Their stated reason is exact: the `[contract]` table arrived in v1.5.0 carrying an obligation for them, and their edition-equality check was *"the only mechanism here that noticed, because `_declared_classes` parses three tables and was silently ignoring four."*

So the consumer has a shape-check on our registry that the publisher lacks. Their version is directional on purpose — a new table upstream must be classified, but an ignored table vanishing is silent — which is the right asymmetry for a consumer and the wrong one for us: **we should care about both.**

**Why Tier 3 and not 2.** A new table cannot break a reader: all three canonical readers scan exactly `[connection]` and `[target]` and ignore everything else, which is why `[contract]` was safe to add. The risk is not breakage but **unnoticed charter growth** — this file's scope expanding without the expansion being a decision. §4.1 was added precisely because that had begun happening.

**Interaction with C-74 worth stating.** These two compose badly. C-74 says a secret-classed entry outside `[secret]` is unguarded; C-75 says a new table is unguarded. Together, a `[staging.SOME_KEY]` table with `class = "secret"` and a real value passes every gate in this repository.

Cross-refs: **C-74** (composes with it, above), **C-63** (the same subject one layer out — *readers* ignore constructs they do not understand; this is *our own guards* ignoring them), **C-73** (the same publisher/consumer asymmetry pointing the other way), seam contract §4.1, views-postprocessing `test_every_table_in_the_registry_is_classified_here` as the reference implementation.

---

### C-76: The README makes verifiable claims about this repository, and nothing verified any of them

| Field | Value |
|-------|-------|
| ID | C-76 |
| Tier | **2** |
| Source | `review-base-docs`, 2026-08-13 |
| Trigger | **Publishing any edition, or changing the required-check set.** Both make a README claim false, and neither produces a signal. Not hypothetical — it has fired seven times |
| Location | `README.md` (the pin instruction; the CI paragraph; the Auth section); `docs/validate_docs.sh` (eight checks, none covering README claims) |

**Three claims on the front page of a public contract repo were false, and every gate was green
throughout.** `validate_docs.sh` passed all eight checks in the same run.

| Claim | Reality |
|---|---|
| *"Pin against this tag — `appwrite-seam-v1.4.4`"* | current was **v1.7.1** — seven editions on |
| *"Two workflows… only the secret scan is required… comes after #71"* | three workflows, three required checks, #71 closed |
| `SessionAuth` listed as a class the package will contain | views-pipeline-core **deleted it**; that deletion drove registry v1.5.1 |

**The pin instruction is the acute one.** A consumer following the front page pinned an edition
predating the entire `[contract.*]` table — the thing two of them now bind their delivery names to.

**Tier 2, and the justification is the shape rather than the damage.** No corruption occurred and no
consumer is known to have followed it. It is Tier 2 because the failure is **silent and
outward-facing**: nothing in this repository can go red for it. Every check here verifies this
repo's internal consistency, and the one artifact that speaks *to other people* was unverified.
Same class as **C-73** — this repo sees its own files perfectly and cannot see what it tells anyone
else — and its third instance in a week, which is what moves it above Tier 3.

**Also structural, and the reason it persisted.** The README was **807 lines, of which 731 described
a package that does not exist.** The live artifacts got one table. Wrong facts survive in a document
whose shape means nobody reads past the first screen.

**Fixed 2026-08-13, and the fix is what closes it:**

- The three false claims corrected; the pin instruction now points at **`obliges_consumers_since`**
  rather than a tag, because a hardcoded number goes stale every edition and this one did, silently,
  for seven.
- **`validate_docs.sh` check 9** — the README references the floor mechanism; every tag it names
  resolves; the floor is itself a fetchable tag. **Mutation-proven four ways**, including
  *no tags + `CI` set → error, not skip*, and `guards.yml` now fetches tags so the check cannot take
  its skip path in CI.
- README reduced to **106 lines**; the roadmap preserved whole at
  `docs/roadmap_shared_client.md`.

**Deliberately NOT fixed by requiring the README to name the newest tag.** That would rebuild the
defect with a gate attached: most editions oblige nobody, so chasing the newest was always the wrong
advice.

**What remains open, and why this entry is not resolved.** Check 9 covers the *pinning* claim — the
one that misled consumers. **It does not cover the rest.** The CI paragraph, the file counts, the
consumer count and the class lists are still prose that nothing verifies; they were corrected by
hand and can rot by hand. The class is narrowed, not closed.

Cross-refs: **C-73** (same class, same week — the publisher blind to its readers), **C-72** (pin
incoherence from the consumer side), **C-68** (the `c41` stub, audited below), seam contract §10.1.

---

### C-77: CI selects guard modules by filename, so the next guard added would run in no job — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-77 |
| Tier | **2** |
| Source | `repo-assimilation` (2026-08-14) — **mutation-proven, mutation reverted** |
| Trigger | **Adding a new guard module to `tests/`** — the next time a registry invariant earns a test of its own, which has happened four times in three weeks (`[contract]` guards, the table-classification guard, the edition guards, the meta-guard). |
| Location | `.github/workflows/guards.yml:82` and `:188`; `tests/conftest.py:15-31`; `tests/test_test_kinds.py` |

`tests/conftest.py` replaced a filename glob with **declared markers**, and its docstring gives the
reason in the repo's own words: *"A guard added later under a name the glob does not match joins no
gate and runs nowhere — a new blind guard, introduced by the epic written to remove blind guards
(C-70, cluster G)."*

**The workflow still selects by filename.** Both jobs pass an explicit file list alongside `-m guard`:

```
guards (self-contained)  pytest -q -m guard tests/test_registry_reader_contract.py tests/test_test_kinds.py
guards (cross-repo)      pytest -q -m guard tests/test_registry_readers_agree.py
```

The marker **narrows** that selection and can never widen it. So the mechanism built to stop a guard
from running nowhere is applied at the one layer that does not decide what runs.

**Proven, then reverted.** A new module `tests/test_zz_probe_new_guard.py` carrying
`pytestmark = pytest.mark.guard` and one deliberately failing assertion:

| Command | Result |
|---|---|
| `pytest -m guard tests/` — what the marker scheme promises | **1 failed**, 18 passed, 2 xfailed |
| `pytest -m guard tests/test_registry_reader_contract.py tests/test_test_kinds.py` — **the exact CI step** | **14 passed, exit 0** — the probe was never collected |
| `pytest -m guard tests/test_test_kinds.py` — the meta-guard | **2 passed** — it accepts the module |

The module is well-formed by every rule this repository wrote, and runs nowhere. **The meta-guard
structurally cannot catch it**: `test_the_two_kinds_partition_the_whole_suite` verifies that every
module carries a marker, not that any job selects it. It is a check on the declaration, and the
defect is in the consumption.

**Latent, not live, and that is the whole tier argument.** The two file lists happen to name all
three guard modules today, so coverage is currently complete — which is also why nothing reports it.
The gap opens on the next addition and opens silently: the author's new tests pass locally, `-m guard`
looks like the selector, CI goes green, and the guard protects nothing. Tier 2 rather than 3 because
the affected surface is the registry whose breakage produced a Tier 1 platform-wide outage (**C-29**),
and rather than 1 because no coordinate is wrong today.

**Same failure as C-70, one layer up.** C-70 was *CI exists and runs none of the guards*; this is *CI
exists, runs the guards it was told about, and cannot be told about a new one*. C-70's resolution note
claims "every guard now runs on every PR" — true when written, and narrowed by this entry.

---

### RESOLVED 2026-08-14 — the workflow now selects by marker, and cannot go back silently

**Fixed in the same session it was registered, because the entry's own point was that it opens on the
next guard added — and the next guard added was one of the three below.**

**The change.** Both jobs select by marker expression over `tests/`, and the CI lane is now
*declared* the same way the kind is:

| Job | Selector |
|---|---|
| `guards (self-contained)` | `-m "guard and not crossrepo" tests/` |
| `guards (cross-repo)` | `-m "guard and crossrepo" tests/` |

`crossrepo` is registered in `tests/conftest.py` and declared on
`test_registry_readers_agree.py`, the one module that needs sibling checkouts.
**Absence is the safe default**: a new guard module with no lane marker joins the self-contained
lane rather than none, so the failure mode of forgetting it is loud (a sibling-needing test failing
in the wrong job) instead of silent (running nowhere).

**Proven both directions, mutations reverted, working tree verified clean.**

*The defect is gone* — the same probe module that exposed C-77 was re-run against the new command:

| | Before the fix | After |
|---|---|---|
| `pytest -m guard tests/` (what the markers promised) | 1 failed | 1 failed |
| **the exact CI step** | **14 passed, exit 0** — probe never collected | **1 failed, 17 passed** — probe caught |

*The fix is guarded* — three new tests in `test_test_kinds.py`, each watched failing for its own
reason:

| Mutation | Result |
|---|---|
| workflow reverted to naming test files | **RED** — `test_the_workflow_selects_guards_by_marker_not_by_filename` |
| the `crossrepo` lane selector deleted | **RED** — `test_both_ci_lanes_are_present_in_the_workflow`, naming the missing lane |
| `crossrepo` placed on a falsification module | **RED** — `test_crossrepo_is_only_ever_used_alongside_guard` |

**Why a guard on the workflow and not just a corrected workflow.** The entry's finding was that
*declarations* were checked and *selection* was not — the meta-guard verified markers while the
workflow ignored them. Correcting the workflow without checking it would leave that asymmetry
untouched and simply reset the clock: `-m` narrows the paths it is given and can never widen them, so
any future step that passes both a marker and a file list is selecting by file list again, whatever
the marker says. The first of the three tests above is the one that makes that irreversible.

**Lane arithmetic, verified:** 17 self-contained + 4 cross-repo + 2 xfailed = 21 passed + 2 xfailed,
exactly the `-m guard` union. The two lanes partition the guard set with nothing outside.

**One honest residual.** `LANE_SELECTORS` in the test and the strings in `guards.yml` are two
statements of one fact — a rename must change both. That is C-53's shape in miniature, and it is
accepted rather than hidden: the test fails loudly on divergence (mutation 2 proves it), which is
precisely the property C-53 was about. The alternative, parsing the YAML and reconstructing pytest's
marker algebra, is brittle against every legitimate way a step can be written, and a brittle guard
gets deleted.

Cross-refs: **C-70** (the resolved entry whose closing claim this qualifies — *"every guard now runs
on every PR"* is true again, and now checked), **C-52**, **C-55**, **C-68**, **C-09** (the same
defect one layer down, inside `validate_docs.sh`, still open), **C-78** (the other inert half of the
marker scheme — still open, and the reason `conftest.py` now warns against deleting the meta-guard),
cluster **G**.

---

### C-78: `strict_markers` is set where pytest does not read it, so a typo'd marker only warns — RESOLVED

| Field | Value |
|-------|-------|
| ID | C-78 |
| Tier | 3 |
| Source | `repo-assimilation` (2026-08-14) — mutation-proven, mutation reverted |
| Trigger | **Removing or weakening `tests/test_test_kinds.py` on the grounds that `conftest.py` already makes a mistyped marker an error.** That belief is what this entry is about; the behaviour is currently covered by the very test the belief would license deleting. |
| Location | `tests/conftest.py:48-60` (`pytest_configure` sets `config.option.strict_markers = True`); claim at `tests/conftest.py:29-31` |

`conftest.py` sets `config.option.strict_markers = True` inside `pytest_configure`, commented *"A
typo'd marker is exactly the silent no-op this repo keeps finding"*, and its module docstring states:
*"the kind is declared, and `--strict-markers` makes a typo an error rather than a silent no-op."*

**It does not.** A module carrying `pytestmark = pytest.mark.guardd` produced, under pytest 9.0.2:

```
PytestUnknownMarkWarning: Unknown pytest.mark.guardd - is this a typo?
1 passed, 1 warning
```

The unknown mark is applied and the run succeeds. Setting the option at `pytest_configure` time does
not reach the strictness check.

**The backstop held, and that is why this is Tier 3 and not 2.** The same probe turned **both** tests
in `test_test_kinds.py` red, naming the file — a module marked `guardd` declares neither known kind,
so the meta-guard rejects it. The outcome is correct; only the advertised mechanism is inert.

**The risk is therefore the belief, not the behaviour.** Two defences are documented, one works, and
the file says both do. The register already carries what happens next: **C-55** records a guard whose
remedy was known, written up, and *still* recurred in the next thing written, and cluster G's whole
subject is checks trusted on the strength of what they claim rather than what they were watched
doing. A contributor tidying `test_test_kinds.py` as redundant would be reasoning from a sentence in
`conftest.py` that is false. Same class as **C-64** — a docstring asserting a guarantee its source
does not support.

**The predicted harm happened the same day, and it is worth recording because it is normally invisible.**
This entry says the risk is *the belief, not the behaviour* — that a reader takes the comment as fact.
A few hours after it was written, a knowledge-graph extraction over this repository (`graphify`,
2026-08-14) produced a node for `tests/conftest.py:60` labelled:

> `strict_markers = True (a typo'd marker is an error)`

That is the claim, restated as a fact, in a downstream artifact that other people and tools will
query — with no trace of the measurement showing it is false. **A reader believed the comment,
exactly as predicted, and the reader was a program.** No human judgement was involved and none would
have caught it.

The graph is not wrong to have done this; it extracted what the source asserts, which is its job. The
point is the propagation path: **an inaccurate comment does not stay in its file.** It is copied into
summaries, graphs, onboarding notes and context packs, each of which looks like an independent
source. Recorded here rather than as its own entry because it is evidence for this concern, not a new
one — and because it upgrades the concern from "someone might believe this" to "something already
did."

---

### RESOLVED 2026-08-14 — the check is written in Python, where it works

**Not fixed by making `--strict-markers` work.** The obvious repair — a `pytest.ini` carrying
`addopts = --strict-markers` — was considered and declined: it adds a config file to a repository
that has deliberately avoided them (C-18, D-04), and it moves pytest's rootdir. The cheaper fix uses
machinery that already exists.

**`test_test_kinds.py::test_no_module_declares_an_unknown_marker`** asserts every module-level
marker is one this repository defines, reusing the `_module_level_marks()` AST parser already in that
file. `KNOWN_MARKERS` is `{guard, falsification, crossrepo}`.

**The inert line is kept, not deleted**, with a comment saying plainly that it does nothing here,
why, and where the real check lives. Deleting it would remove the only pointer to why the Python
check exists — and this entry's whole subject is a mechanism believed to work.

**Mutation-proven, reverted.** The second row is the one that matters:

| Mutation | Old kind check | New check |
|---|---|---|
| `guard` → `guardd` (the kind) | red (module declares no valid kind) | **RED**, naming `['guardd']` |
| `crossrepo` → `crossrepoo` (**the lane**) | **1 passed** — satisfied | **RED**, naming the typo |

**The lane row is why this needed its own check.** A module marked `guard` plus a mistyped
`crossrepoo` declares a perfectly valid kind, so `test_every_test_module_declares_exactly_one_kind`
passes — while the lane marker means nothing and the module lands in the wrong CI job. **That is
C-77's failure re-entering through a spelling mistake**, and it became reachable the moment C-77
introduced a third marker.

**Known limit, stated in the test rather than discovered later.** It reads module-level `pytestmark`
only. A custom marker on a single test function is invisible to it. None exists today — the one
function-level marker in this suite is `_D05`, which wraps the builtin `xfail` — and closing that
would need either the `pytest.ini` declined above or walking every decorator. Not worth it until a
custom function-level marker exists.

Cross-refs: **C-77** (the other half of the marker scheme — the lane this now protects), **C-64**
(a docstring citing a verdict that did not say what it claimed — the same propagation, by hand),
**C-68**, **C-55**, **C-81** (the same extraction run, the opposite failure — what it could not see),
**C-18** / **D-04** (why a `pytest.ini` was declined), cluster **G**.

---

### C-79: The reader comparison finds its interpreter by globbing sibling repositories' virtualenvs

| Field | Value |
|-------|-------|
| ID | C-79 |
| Tier | 3 |
| Source | `repo-assimilation` (2026-08-14) — observed in a local run |
| Trigger | **Reading a local `pytest` result as a verdict on reader agreement before opening a PR** — which is the documented pre-PR habit, and the only place all three readers are ever compared. |
| Location | `tests/test_registry_readers_agree.py:130-145` (`_interpreter_with_tomllib`), specifically the candidate line `str(p) for p in sorted(WORKSPACE.glob("*/envs/*/bin/python"))` |

The behavioural tier needs an interpreter the readers can run under (stdlib `tomllib`, ≥3.11). The
candidate list is `sys.executable`, then `python3.13/3.12/3.11` from `PATH`, then **every virtualenv
under every sibling repository in the workspace**, taken in sort order.

On this machine `sys.executable` is 3.10.14 and no `python3.1x` is on `PATH`, yet the behavioural
tests **ran and passed** — meaning the three canonical readers were executed under an interpreter
belonging to some other project, selected by whichever path sorted first.

Two consequences, both about trusting a local green:

1. **The verdict is not reproducible between two developers.** It depends on which sibling repos are
   checked out and what environments they happen to contain. A developer with no such env gets a
   `pytest.skip` and a smaller signal; a developer with one gets a full comparison under an
   interpreter nobody chose.
2. **Local and CI scope differ by design.** Locally all three readers are present and compared; CI
   sees **two of three**, because `views-faoapi` is private (**C-51**). A divergence involving faoapi
   is therefore visible on a laptop and invisible in CI — the opposite of the usual direction, and
   worth knowing before someone cites a local run as the stronger evidence.

**The `CI`-set branch is correct and is not the subject.** `_require_interpreter()` fails rather than
skips when `CI` is set, and `guards.yml` pins 3.12 — belt and braces, deliberately. This entry
concerns the local path only, which is the path used before a PR exists.

Tier 3: no correctness impact and no silent data path, but it affects every contributor's pre-PR
check and makes one guard's result depend on ambient state nobody declared.

Cross-refs: **C-51** (why CI sees two of three), **C-52** (the last time this guard's inputs were
narrower than they looked), cluster **G**.

---

### C-80: The two meta-guard tests fire together on one cause and read as two signals

| Field | Value |
|-------|-------|
| ID | C-80 |
| Tier | 4 |
| Source | `repo-assimilation` (2026-08-14) — both observed failing on a single probe |
| Trigger | **Diagnosing a red `guards (self-contained)` job by counting failures** — two reds here mean one defect, and acting on them as two would send someone looking for a second cause that does not exist. |
| Location | `tests/test_test_kinds.py:61` (`test_every_test_module_declares_exactly_one_kind`) and `:83` (`test_the_two_kinds_partition_the_whole_suite`) |

Both tests parse every `tests/test_*.py` for module-level `pytestmark` and both fail on any module
lacking a known kind — confirmed: the C-78 probe reddened both simultaneously with near-identical
messages. The second is implied by the first for every input except a module declaring *both* kinds,
which the first already rejects.

The docstrings state a real distinction of intent — one is per-module, the other is about the pair of
selectors CI uses — but the implementations do not differ, and neither observes CI's actual selection
(that gap is **C-77**). Tier 4: no correctness impact, localised, and the duplication is cheap. Worth
recording only because this repository's stated standard is that a check earns its place by failing
for its own reason, and one of these two has never failed for a reason the other did not.

Cross-refs: **C-77** (what neither of them can see), **C-78** (the probe that fired both), cluster **G**.

---

### C-81: A corpus tool reading this repository by file type sees the governance and misses the product

| Field | Value |
|-------|-------|
| ID | C-81 |
| Tier | 4 |
| Source | `graphify` knowledge-graph build (2026-08-14) — observed during the run, corrected by hand |
| Trigger | **Running any corpus-level tool over this repository** — a knowledge graph, a documentation-coverage report, an onboarding summary, an LLM context pack, a new contributor's `find`. Before trusting its output, check that `coordinate_registry.toml` and the four gate files appear in its file list. |
| Location | `docs/ADRs/platform/coordinate_registry.toml`; `docs/validate_docs.sh`; `.github/workflows/{guards,falsification,secret_scan}.yml`; `.gitleaks.toml`; `tests/fixtures/*.toml` |

**Measured, not inferred.** `graphify`'s file detector classified this repository as **35 files: 8 code (`.py`) and 27 documents (`.md`)**. The eight files it did not surface are:

| Missed | What it is |
|---|---|
| `coordinate_registry.toml` | **THE canonical artifact. The thing six repositories consume.** |
| `docs/validate_docs.sh` | the documentation gate, 9 checks, required on every PR |
| `.github/workflows/*.yml` (×3) | every CI job this repository has |
| `.gitleaks.toml` | the scan rule that gates going public |
| `tests/fixtures/*.toml` (×3) | the C-29 and D-05 evidence |

So the default reading of this repository is **all of the governance and none of the mechanism.** The seam contract is a `.md` and was seen; the registry it governs is a `.toml` and was not. Had the omission not been caught by hand, the resulting graph would have contained the contract, the ADRs, the register and the protocols — and no registry, no guards, no CI — while reporting complete coverage of a 35-file corpus.

**Tier 4, and the justification is scope rather than harm.** Nothing here corrupts data, nothing breaks, and this repository has no runtime to degrade. It is registered because the class is familiar and the cost lands on whoever audits next: **an analysis that reports coverage without having seen the thing that ships.** That is the shape of cluster G stated one level out — not a guard that cannot see its invariant, but a *reader* that cannot see the artifact. The fix is not this repository's to make; the discipline is to check the file list before believing the summary.

**Why it is worth a row rather than a note.** This repository's product is deliberately a data file and its gates are deliberately shell and YAML — those choices are ratified (`dómr_endurmat` E3: *"no tooling, no generators"*) and are not in question. The consequence is: **every generic tool that walks this tree by extension will be wrong about it in the same direction, and will not say so.** That will recur, and the next person deserves to meet the finding rather than rediscover it.

**Not merged into C-09.** C-09 is about this repository's own checks being narrower than they look. This is about *external* readers of the repository being narrower than they look, which is a different party and a different fix.

Cross-refs: cluster **G** (an instrument reporting success without having looked — the same shape, a different instrument), cluster **L** (things about this repository that nothing here can verify), **C-74** and **C-75** (the two entries that turn on what a tool does and does not enumerate).

---

### C-82: Every credential path routes through one person, and nothing anywhere says so

| Field | Value |
|-------|-------|
| ID | C-82 |
| Tier | **2** |
| Source | `review-rr` strategic (2026-08-14) — blind-spot analysis; the category was empty because nobody had looked, not because the risk was absent |
| Trigger | **By 2026-09-17 — sixty days before the keys die — establish whether the 2026-11-17 rotation can be executed if the operator is unavailable for two weeks.** Concretely: is there a second Appwrite console holder, or a written handover naming what to do? If neither, that is the answer and it should be recorded as an accepted risk rather than left unasked. **Also:** when `PRODUCTIONAPI_API_KEY` or any further external-party key is issued, record who besides the operator can revoke it. |
| Location | organizational — Appwrite console custody; `docs/ADRs/platform/appwrite_seam_contract.md` (the `Operator` header row, §5.1–§5.5, §7, §9 O1/O2); `coordinate_registry.toml` `[secret.*]` (`issued_by = "operator"` on every slot); cluster **I** in this register |

**The concentration, counted rather than asserted.** One named person holds Appwrite console custody,
key issuance, key rotation, scope narrowing, and the non-production-project decision. Every one of the
following routes to that person and to nobody else:

| Entry | What waits on the operator |
|---|---|
| **C-27** (O1) | designing the secret-value propagation path — no mechanism exists |
| **C-28** (O2) | issuing and scoping any further external-party key |
| **C-56** | the console action that fixed the CRAFD key's scopes |
| **C-65** | the rotation of **both** platform keys before **2026-11-17** |
| **C-66** | deciding whether `crafd-caller-read` gets an expiry at all |
| **C-69** | buying, or declining to buy, GitHub Secret Protection |
| seam contract §7 | creating a test project, which blocks the reference validator, the scaffold (#8), C-21's fixture guard and D-04 |

Nine open entries and one deferred scaffold decision, one holder.

**Why this is a register entry and not merely an org chart.** The seam contract names the operator in
its header and in six clauses. The registry stamps `issued_by = "operator"` on every secret slot. So
the *dependency* is recorded everywhere — and the *risk in the dependency* is recorded nowhere. No
document states that this is one person, that there is no second console holder, or what happens to a
rotation already sized in hours if that person is away for a fortnight. **A reader of this register
sees nine entries assigned to an owner and reasonably infers the owner is a role. It is a name.**

That is this platform's own distinction, applied to itself: *"an accepted gap is done; a silent gap is
not."* This gap is silent.

**Tier 2, and the justification is structural rather than dramatic.** Not Tier 1: the failure is
**loud** — at 16:10 on 2026-11-17 every Appwrite identity on the seam is dead at once and everyone
knows immediately. Nothing is silently corrupted. It is Tier 2 because the fragility is structural and
the change scenario is ordinary: **illness, leave, or a two-week absence across a fixed external
deadline that cannot be moved.** The FAO half of the rotation additionally needs coordination with an
external partner (C-65), which is the part that cannot be compressed at the end. There is no second
holder, no documented procedure, and no fallback key — C-65 already establishes that the two platform
keys cannot cover for each other because they die together.

**What this entry does not claim.** It does not argue for a second console holder — handing Appwrite
custody to a second party has its own blast-radius cost and is exactly the kind of decision §5.3's
floor exists to reason about carefully. **Both answers are defensible. Only the absence of a decision
is not** — which is the same shape as C-66, where `never` was a default rather than a choice, and
nobody looked until the key list was read.

**Why it took a blind-spot pass to find.** The register grew by tracking what its audits looked at,
and every audit so far read code, prose or config. Nothing reads the org. The category was empty
because it had not been examined, which is the difference the blind-spot analysis exists to detect.

Cluster **I** (*credential lifecycle has no owner*) — and note the inversion worth stating: cluster I
says the lifecycle has **no owner**, meaning no defined process. This entry says the process that does
exist has **exactly one**, undocumented. Those are complementary, not contradictory, and the fix for
one does not fix the other.

Cross-refs: **C-65** (the dated deadline this is measured against), **C-27**, **C-28**, **C-56**,
**C-66**, **C-69**, seam contract §5.3 (the floor that governs who may hold what), §7 and issue #8
(the test-project decision, blocked behind the same person).

---

## Disagreements

### D-01: Decomposition granularity — eight modules vs depth-driven boundaries

| Field | Value |
|-------|-------|
| ID | D-01 |
| Source | expert-review (2026-06-12) |
| Perspectives | Martin/GoF (eight one-concern modules per `README.md:216-237` is clean separation aligned with ADR-001/002), Ousterhout/Hickey (`auth.py` and `compat.py` are shallow modules — interface proliferation without hiding; merge until depth justifies splitting) |
| Resolution | Unresolved. Proposed: defer to what the Phase 1 decomposition reveals; pre-authorize boundary merges via ADR update rather than treating ADR-002's layer list as fixed file boundaries. Revisit at the Phase-1 decomposition review, when actual module depth is observable. |

> **Dormant** — this disagreement's resolution defers to what the Phase 1 decomposition reveals,
> and Phase 1 is deferred behind roadmap Decision Log #11 (three consumer APIs; currently two).
> It is not stalled; it is waiting on evidence that does not exist yet.

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

> **Dormant** — this disagreement's resolution defers to what the Phase 1 decomposition reveals,
> and Phase 1 is deferred behind roadmap Decision Log #11 (three consumer APIs; currently two).
> It is not stalled; it is waiting on evidence that does not exist yet.

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
| Resolution | **RULED 2026-08-10 by the operator. Reservations live in `[planned]`; a value-less entry in a scanned table is malformed and every reader raises. Execution is views-models#327.** |

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

### RULED — 2026-08-10, by the operator

> **Reservations live in `[planned]`. A value-less entry in `[connection]` or `[target]` is malformed
> regardless of any `status` it carries, and every reader raises on it. `status` is documentation and
> carries no semantics.**
>
> **The decision cost one deletion in one repo.** views-models' reader carries an `_is_planned()`
> predicate that skips a value-less entry when its `status` begins "planned". views-faoapi and
> views-crafdapi already behave correctly. Deleting that predicate, and the ratified test that pins
> it, makes all three agree. **Execution is views-models#327; nothing is required in this repo.**
>
> **Why this and not the two options actually tabled.** *Raise always* couples unrelated repos —
> reserving a name for a future consumer would break the FAO delivery today. *Skip always* lets a
> delivery run on partial coordinates in silence, which is the July incident (C-29). The ruling
> avoids both by removing the ambiguous case: a reservation in `[planned]` is invisible to every
> reader, so it breaks nobody, and a value-less entry in a scanned table is then unambiguously a
> mistake that everyone should stop on.
>
> **The rule was already written down.** The registry's standing block says a value-less entry
> belongs in `[planned]`, and `test_every_reader_scanned_entry_has_a_value` enforces it and passes
> today. `_is_planned()` defends against a shape the source-side gate already rejects — and by
> defending, converts a caught mistake into a silent partial delivery. That is why it is a deletion
> rather than a new rule.
>
> **What stays open until views-models ships it:** C-51 remains Tier 1, and the two
> `xfail(strict=True, raises=AssertionError)` markers in `tests/test_registry_readers_agree.py`
> remain. When the readers converge those markers fail on the **unexpected pass**, which is the
> signal to delete them and close C-51 — the decision cannot be quietly forgotten.
>
> **Not settled by this ruling:** **C-63** (no reader checks `[meta] version`) is the general form of
> the same problem and needs its own decision — views-appwrite#45.

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
- **Resolution:** Move to "Resolved Concerns" with resolution date and summary when addressed. **Six entries (C-10, C-52, C-53, C-54, C-70, D-02) are marked resolved *in place*** rather than moved, because their narratives carry the amendment history that made them resolvable; the header counts treat them as resolved, and each carries `— RESOLVED` in its heading so the count can be reproduced by `grep`. C-70 additionally anchors Cluster G and is cross-referenced by C-52, C-53 and C-68 — moved to the bottom, the cluster stops reading as one story.
- **Dormancy:** an entry whose trigger cannot fire until a deferred event may carry a `> **Dormant**` marker beneath its field table (see *Dormancy* under Causal Clusters). **It does not change the tier**, which states severity if the trigger fires. Dormant entries are open and counted as open.
- **Header counts:** Manually maintained — update whenever a concern is added or resolved. **They are reproducible:** `Total` = count of `^### C-`; `Resolved` = count of those with `— RESOLVED`; `Open` = the difference. *(Audited 2026-08-14: the convention above previously named three resolved-in-place entries while the counts honoured only two — C-10 was described as counted resolved and was not. Two numbers that must agree, compared to each other and to nothing else, is **C-53's own shape**, and it had gone unnoticed in the register that registers it. Fixed by giving C-10 the heading suffix so the count and the sentence are derived from the same thing.)*
- **Note:** Many concerns reference locations in external repos (`views-pipeline-core`, `views-faoapi`) because this repository is a roadmap for a package not yet extracted. Confirm those locations when extraction (Phase 1) begins. **As of 2026-07-28 several are external by *ownership*, not merely by location** (C-13, C-26, C-27, C-28): this repo tracks them because it hosts `PLATFORM-001`, but cannot fix them — the fix belongs to a lineage owner or to the operator.
- **Governed by:** ADR-010 (`docs/ADRs/010_technical_risk_register.md`).
