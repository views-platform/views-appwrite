
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

## Challenges and questions

Raised during review and kept here on purpose. **These are not decisions.** They change nothing above
them. Each entry records when it was raised, what prompted it, and what would settle it.

### 2026-11-25 — A trigger condition fired on 2026-08-02 and this ADR is still Deferred

**Raised by:** a multi-expert review of `views-faoapi` and `views-crafdapi` on 2026-11-25
(`reports/2026-11-25_faoapi_crafdapi_review.md`), read back against this document.

**The concern.** "Trigger Conditions for Reconsideration" lists *"A second consumer API is cloned from
`views-faoapi`"*. **Fact, checked 2026-11-25:** `views-crafdapi` was forked from `views-faoapi` on
2026-08-02. The trigger fired nearly four months ago and this ADR is unchanged.

That is not an argument for ratifying evolution rules today — the Rationale for Deferral still holds,
since no code exists here. It is an argument that **a deferral with trigger conditions needs something
that checks them**, or the deferral silently becomes a permanent absence. This ADR was written to
"prevent ad-hoc or implicit policies from emerging unnoticed", and in the four months since the
trigger fired, two consumer repositories have evolved independently under no ratified policy at all.

**What would settle it.** Either a mechanism that tests the trigger conditions on a schedule, or an
honest amendment saying the triggers are advisory and the activation point is publication of `v0.1.0`
alone.

### 2026-11-25 — The evolution rules being deferred are all rules about adding. The measured need is a rule about removing.

**Raised by:** the same review.

**The concern.** Every item under "Non-Decisions" governs how the package may **grow or change
compatibly**: versioning schemes, release processes, migration tooling, deprecation mechanics, API
stability guarantees. Deprecation is the closest thing to removal, and it is about how to retire a
published promise gracefully.

None of it governs the failure actually observed in the consumers.

**What was measured in the consumers. Fact, checked 2026-11-25.** `views-faoapi` has **122 open
issues**, of which 50 are labelled `story`, 12 `epic` and 31 `planning`; `views-crafdapi` has 72.
Reading all 122 titles, **not one proposes removing a capability.** Every issue is a correct response
to a real finding, and every one adds a guard, a proof, a runbook or a test. Over the same period the
repository reached 14,855 source lines against 29,171 test lines, of which **1,656 source lines are
not reachable from the running application at all** — `plotting.py`, `smoke.py`, `client.py`, a
`wandb` dependency on a serving box, and five smaller modules.

The maintainer's own description of the effect, 2026-11-25: *"every time I do, their code base just
grows and grows and grows. Nothing ever stops."*

**The structural reading.** A governance system made entirely of additive obligations — ADR-005
requires tests, ADR-008 requires observability, ADR-010 requires risk-register entries, ADR-006
requires intent contracts — produces exactly this. Each obligation is individually right. Together
they mean the cheapest correct response to any finding is to add something, and the most expensive is
to delete something, because deletion has to argue against every obligation at once. **The governance
is not failing; it is working, in one direction only.**

**What would settle it.** A rule in whichever ADR eventually supersedes this one that makes removal a
first-class move. The review's proposal, recorded here as a candidate and not as a decision: *a commit
that closes an issue must reduce the line count, or state in its message why it cannot.* It is cheap,
it is checkable, and it does not forbid anything — it only forces the growth to be deliberate.

**What this does not settle.** Whether that rule belongs in this ADR's successor, in ADR-000's rules
for the ADR process, or in `contributor_protocols/`. Nor whether it should apply to tests, where the
line count is not the cost that matters. And it is explicitly not a licence to delete: the same review
found that two of the nine unreachable modules have dozens of references in notebooks and delivered
documentation, and should be moved rather than removed.

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
