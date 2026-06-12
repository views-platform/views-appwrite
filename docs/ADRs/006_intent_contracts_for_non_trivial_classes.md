
# ADR-006: Intent Contracts for Non-Trivial Classes

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

The two source implementations this package will be extracted from drifted partly
because behavior lived in their authors' heads. `FileMetadata` quietly acquired domain
fields; the `_as_dict` compat guard existed in one copy but not the other; "auto-create
the bucket vs raise" differed silently between repos. Tests verify *current* behavior,
not *intended* behavior — they would not have caught the divergence of intent.

To prevent the same drift in the consolidated package, non-trivial classes require an
explicit, human-readable declaration of intent. This matters acutely here because the
package will be edited by multiple maintainers and by silicon-based agents (ADR-007),
and because its classes are the shared foundation many consumers depend on.

No classes exist yet. This ADR establishes the requirement and the infrastructure
(`docs/CICs/`); contracts are written when the classes are implemented in Phase 1.

---

## Decision

All **non-trivial and substantial classes** in this repository must have an explicit
**intent contract** (a CIC under `docs/CICs/`).

An intent contract is a short, human-readable description of what the class is intended
to do, what it is explicitly *not* responsible for, and the guarantees it provides to
callers. It need not be a full technical specification, but it must be unambiguous,
human-readable, and consistent with tests and implementation.

---

## What Qualifies as a Non-Trivial Class

A class is **non-trivial** if it meets one or more of:

- Encodes domain or decision-relevant logic
- Orchestrates multiple components
- Maintains internal state across operations
- Enforces or assumes semantic invariants
- Acts as a boundary between major subsystems
- Could cause silent failure or misuse if misunderstood

When in doubt, treat the class as non-trivial.

**Anticipated CIC subjects in this package (from ADR-001 ontology, once implemented):**
`DatastoreManager` (orchestrator/public surface), `StorageManager`, `MetadataManager`,
`CacheManager` (state-owning resource managers), `AppwriteClient` (SDK boundary), and the
`AuthManager` strategy hierarchy. `AppwriteConfig` and `OperationResult` are closer to
value objects but, given `AppwriteConfig.__post_init__` normalisation and its
single-source-of-truth role, it likely warrants a contract too. The `compat` functions
are not classes and are governed by tests rather than a CIC.

---

## Form of an Intent Contract

At minimum: **Purpose**, **Non-goals**, **Inputs and assumptions**, **Outputs and
guarantees**, **Failure behavior**. Use `docs/CICs/cic_template.md`. The contract may
live as a markdown file in `docs/CICs/` referenced from the code. Format is flexible;
clarity is not.

---

## Relationship to Tests

Intent contracts and tests must agree. Tests should reflect declared intent; changes to
intent require updating the contract; changes that violate declared intent are bugs, not
refactors.

---

## Enforcement

- Introducing a non-trivial class without an intent contract is grounds for blocking a change.
- Modifying a non-trivial class in ways that contradict its contract is not permitted.
- Reviewers reference intent contracts when evaluating changes.

Enforced socially and through review.

---

## Consequences

### Positive
- Preserves the no-domain-logic intent that keeps this package generic (ADR-001)
- Makes refactoring safer and reduces reviewer load
- Prevents the silent meaning-drift that affected the source copies

### Negative
- Additional upfront writing
- Documentation must be updated alongside code

These costs are accepted intentionally.

---

## Notes

Intent contracts are a mechanism for ensuring the package continues to mean what we think it means as it changes. Because no code exists yet, `docs/CICs/` currently holds only the template and README; contracts are authored during Phase 1 implementation.
