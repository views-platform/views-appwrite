
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

## Challenges and questions

Raised during review and kept here on purpose. **These are not decisions.** They change nothing above
them. Each entry records when it was raised, what prompted it, and what would settle it. An entry may
end in an amendment to this ADR, or in a recorded "looked at it, it is fine" — both are useful
outcomes and the second should be written down rather than left implicit.

No code exists in this repository yet. Until it does, the decisions above are cheap to change, which
makes this the right moment to collect objections rather than defend positions.

### 2026-11-24 — The anticipated class list is premature, and may be classitis

**Raised by:** a reading session working through Ousterhout, *A Philosophy of Software Design*, ch. 4
against this repository's existing documents. The maintainer agreed in the same session that the list
is too early.

**The concern.** The section "What Qualifies as a Non-Trivial Class" names the classes it expects:
`DatastoreManager`, `StorageManager`, `MetadataManager`, `CacheManager`, `AppwriteClient`, an
`AuthManager` hierarchy, plus `AppwriteConfig` and `OperationResult`. Six managers and two value
types, for a package that does not exist.

Two separate problems.

*It is too early.* Nothing is built. We do not know which of these classes is needed. Naming them
inside an Accepted ADR lends a guess the standing of a decision, and a later maintainer has no way to
tell which parts of this document were reasoned and which were anticipated.

*The shape may be wrong in a way the literature names.* Ousterhout §4.6 calls it **classitis** — "the
mistaken view that 'classes are good, so more classes are better'." His argument is not that small
classes are individually bad. It is that each one carries an interface, those interfaces accumulate,
and total system complexity rises even while every file looks simple: "Small classes don't contribute
much functionality, so there have to be a lot of them, each with its own interface. These interfaces
accumulate to create tremendous complexity at the system level." Six managers is six interfaces a
maintainer must learn before using the package at all.

**What would settle it.** Write the intent contract for the package's single public entry point
first, in the caller's vocabulary, and only then ask how many classes are needed behind it. If the
answer is still six, the list stands on evidence instead of anticipation.

**Possible outcome.** Delete the anticipated list, or demote it to an illustration explicitly marked
as not binding.

### 2026-11-24 — The rule covers classes; the gateway's main interface would not be a class

**Raised by:** the same session.

**The concern.** This ADR requires an intent contract for non-trivial **classes**. ADR-012 (Proposed)
decides that the shared Appwrite client is a service reached over HTTP, which nobody installs. If
ADR-012 stands, the single most important interface in the design is a set of HTTP routes, and the
rule as written does not reach it.

**What would settle it.** Decide whether "non-trivial class" should read "non-trivial class or
service interface", and whether an HTTP surface gets an intent contract of its own. The CIC fields
(Purpose, Non-goals, Inputs and assumptions, Outputs and guarantees, Failure behavior) apply to a
route as readily as to a class.

---

## Relationship to the literature

This ADR was written in June 2026, before the sources below were consulted. They are recorded here
because they describe, in general terms, the same mechanism this ADR was built to defend against. The
agreement was arrived at independently; it is noted, not claimed as influence.

**Ousterhout, J. (2018), *A Philosophy of Software Design*, ch. 4.** §4.2 divides a module's
interface into a **formal** part — signatures and public attributes, which the language can check —
and an **informal** part: *"if a developer needs to know a particular piece of information in order to
use a module, then that information is part of the module's interface."* He adds that *"for most
interfaces the informal aspects are larger and more complex than the formal aspects"*, and that the
informal part can only be recorded in prose.

An intent contract is that prose. The CIC fields required above — Purpose, Non-goals, Inputs and
assumptions, Outputs and guarantees, Failure behavior — are a structured way of writing down the
informal interface. It is why this ADR's own diagnosis, that *"behavior lived in their authors'
heads"*, matches §4.2's account of where that information sits when nobody writes it down.

§4.3 names the failure this guards against: an abstraction that omits details the caller genuinely
needs is a **false abstraction** — *"it might appear simple, but in reality it isn't."*

---

## Notes

Intent contracts are a mechanism for ensuring the package continues to mean what we think it means as it changes. Because no code exists yet, `docs/CICs/` currently holds only the template and README; contracts are authored during Phase 1 implementation.
