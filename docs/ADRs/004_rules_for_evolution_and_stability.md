
# ADR-004: Rules for Evolution and Stability

**Status:** Deferred  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  
**Informed:** All contributors  

---

## Context

The preceding ADRs establish:

- **ADR-001:** the ontology of the repository (what exists)
- **ADR-002:** the topology of the repository (how components may relate)
- **ADR-003:** semantic authority (who owns meaning and how it is declared)

Together, these decisions define the system’s structure and semantics at a point in time.

What they do **not** yet define is how the system is allowed to **change over time**:
- which components are expected to be stable (ADR-001 marks `compat` and metadata as evolving)
- what constitutes a breaking change to the public API (`AppwriteConfig`, `DatastoreManager`, `OperationResult`)
- when compatibility guarantees apply to consumers that pin a version
- when a new ADR is required

These questions are especially live for `views-appwrite` because its whole purpose is to
be a *shared* dependency: the moment a consumer pins `views-appwrite @ ...@v0.1.0`, its
evolution rules start to matter. The roadmap already sketches a policy (semantic
versioning, `>=0.1,<1.0` during 0.x, broad SDK pin `appwrite>=5.0.0`, fixes land once in
`compat`). That sketch is the raw material for the eventual decision — but it has not yet
been ratified as an architectural rule.

---

## Decision

No decision is made at this time.

Rules governing stability, evolution, and backwards compatibility are **explicitly deferred**.

This ADR exists to:
- acknowledge the importance of this dimension
- reserve a place for a future, explicit decision
- prevent ad-hoc or implicit policies from emerging unnoticed

---

## Rationale for Deferral

At the time of writing, **no code exists** — the repository is a roadmap. Versioning and
deprecation rules cannot be meaningfully ratified before there is a published artifact to
version. Premature guarantees would either be ignored or constrain the Phase 1
extraction. Deferring preserves design freedom while keeping the absence of rules
explicit rather than accidental.

---

## Trigger Conditions for Reconsideration

This ADR should be revisited when one or more of the following become true. Several are
explicitly anticipated by the roadmap and are likely to fire soon after Phase 1:

- **`v0.1.0` is published and a consumer pins it** (roadmap Phase 1/2). This is the natural activation point — at that moment the semver and pinning policy sketched in the roadmap should be ratified here.
- A second consumer API is cloned from `views-faoapi` (roadmap trigger #1; risk register C-05).
- `views-pipeline-core` upgrades to Appwrite SDK 14+, forcing the `compat` layer's evolution policy to be explicit (risk register C-03).
- Breaking changes to `AppwriteConfig` begin to incur coordination/migration costs across consumers (risk register C-04).
- Contributors express uncertainty about what is safe to change in the public API.

At that point, a new ADR should supersede this one.

---

## Non-Decisions (Explicitly Out of Scope for Now)

This ADR does **not** define:
- Versioning schemes (the roadmap's semver sketch is not yet ratified)
- Release processes
- Migration tooling (e.g. the transitional `path_manager`→`cache_dir` shim in risk R6)
- Deprecation mechanics
- API stability guarantees

Those topics are intentionally postponed.

---

## Consequences

### Positive
- Avoids premature or brittle guarantees before any code exists
- Preserves flexibility during the Phase 1 extraction
- Makes the absence of rules explicit rather than accidental

### Negative
- Contributors must exercise judgment when making breaking changes
- Some uncertainty remains about long-term guarantees

These consequences are accepted intentionally.

---

## Notes

This ADR is a placeholder by design.

Its purpose is to ensure that when rules for evolution and stability are introduced, they are explicit, deliberate, and consistent with ADR-001 through ADR-003. Until then, change is governed by those ADRs and by careful review. The strongest signal that it is time to activate this ADR is the publication of `v0.1.0` with at least one consumer pinning it.
