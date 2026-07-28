
# ADR-008: Observability and Explicit Failure

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  
**Amended:** 2026-07-28 — §1 auto-provisioning clause (þing-01 / PLATFORM-001 D5). See Amendment Log.  

---

## Context

`views-appwrite` performs network I/O against a remote store on behalf of every VIEWS
consumer. The dangerous failures are the quiet ones: an upload that fails but is logged
and swallowed, a metadata write that partially succeeds, a cache that serves a stale file
as current, an SDK-14 response that normalises to "empty" instead of raising. Stack
traces alone are insufficient — these operations run inside long-lived pipelines and
shadow-deployed APIs where a swallowed error surfaces, if at all, as wrong data
downstream.

The roadmap documents a real, deliberate instance of this tension: pipeline-core's
`AppwriteSaver` catches all upload exceptions and logs instead of raising (risk register
C-06). That graceful-degradation policy belongs to the *consumer*. This ADR governs what
the *package* must do: fail loud and record.

---

## Decision

The repository adopts the following invariant:

> Structural failures must be both **logged persistently** and **raised explicitly**.

### 1. Explicit Failure

- Invariant violations must raise exceptions (e.g. missing required `AppwriteConfig` fields, unrecognised SDK response shapes).
- Structural failures must not be downgraded to warnings.
- Errors must not be silently swallowed inside the package.
- Fallback behavior must not hide semantic failure.
- **A missing bucket, database, collection, or attribute is a *coordinate failure* and must raise,
  naming the offending coordinate.** This holds on every path, read and write alike.
- **Provisioning is opt-in, default off.** Creating a bucket, database, collection, or attribute is
  reachable *only* from a deliberate, explicitly-invoked setup entrypoint — never from an ordinary
  read or write operation, and never as a recovery step after a coordinate miss.
- **A half-succeeded write must raise.** A file that lands whose metadata write fails is a failure,
  not a logged warning.

Fail-loud (ADR-003) applies fully to runtime behavior. **`DatastoreManager` and the
resource managers must raise specific, documented exception types** so that a consumer
that *chooses* to degrade gracefully (like `AppwriteSaver`) can catch precisely those
types rather than a bare `Exception`. The package must never make the silent-degradation
decision on the consumer's behalf.

### 2. Persistent Observability

- Raised structural failures must be logged at `ERROR` level or higher.
- Critical, irrecoverable failures must be logged at `CRITICAL`.
- Logging must occur before or at the point of raising.
- Logging is not a substitute for raising; raising is not a substitute for logging.

### 3. Scope

Applies to: configuration validation failures, SDK response normalisation failures,
storage/metadata operation failures, cache-consistency failures, auth failures, and other
structural failures. It does not prescribe formatting or specific logging utilities
(see `standards/logging_and_observability_standard.md`).

---

## Amendment Log

### 2026-07-28 — §1: auto-provisioning is no longer blessed

**Cause:** þing-01, the platform assembly on identity, secrets and configuration across the VIEWS
Appwrite seam (verdict `orð_dómr.md` D5, as amended by `dómr_endurmat.md`; ratified by all six
seats, human sign-off Simon Polichinel von der Maase). Governing contract:
`docs/ADRs/platform/PLATFORM-001_identity_secrets_configuration_contract.md` §6.

**Struck.** The parenthetical that read:

> *"(auto-creating a missing bucket is an explicit, documented behavior — not a hidden fallback that
> masks an error)"*

**Replaced by** the four bullets now in §1: coordinate failures raise and name the coordinate;
provisioning is opt-in and default off, reachable only from a deliberate setup entrypoint;
half-succeeded writes raise.

**Why the original clause was wrong.** It treated auto-creation as *documented*, therefore
acceptable. þing-01 established (sáttmál S8, amended) that on the seam's write paths **both** client
lineages auto-provision on a miss, so a single wrong character in a `bucket_id` **succeeds** into a
newly-created phantom bucket while readers of the intended bucket see stale data indefinitely — no
error raised anywhere in the system. Documented or not, that is a fallback that hides semantic
failure, and it contradicted ADR-003's fail-loud invariant that this ADR exists to enforce. The
clause was the one place in this repository's constitution that blessed the platform's most
dangerous property.

**Register effect.** Resolves **D-02** (the standing disagreement between this clause and ADR-003)
in favour of the fail-loud reading. The related **C-13** (typo'd `bucket_id` → silent data
divergence) now has a ratified fix direction; it closes when the code lineages ship it.

**Scope of this amendment.** It binds *this repository's* doctrine — which, this repo having no
code, means it binds the eventual extraction and any contributor reasoning from ADR-008. The two
live lineages fix themselves independently: views-faoapi gates its `create_*` helpers (faoapi #275),
views-pipeline-core amends its ADR-046 §5 and write path. Per `dómr_endurmat` E4 those
cross-references are **informational, not a coordination barrier** — each lineage flips on its own
schedule, and a repo that raises early is strictly safer than one that waits.

**Declaration discipline (PLATFORM-001 §6), for whoever implements this.** Each lineage's change is
preceded by a characterization test enumerating its `create_*` call sites, and is declared done only
after real-exception-type tests and a live drill run **in this order: amend → ship the raise change
→ drill the raise path → (test project exists) → drill the provisioning path.** Drilling before
shipping would itself provision a phantom bucket in production.

---

## Consequences

### Positive
- Persistent traceability of structural failures across consumers
- A clean division: the package fails loud; the consumer owns any degradation policy
- Strong alignment with the fail-loud invariant (ADR-003)

### Negative
- Slight increase in boilerplate (log-then-raise)
- Requires defining a documented exception taxonomy for the package

These costs are accepted.

---

## Notes

This ADR defines architectural requirements for failure handling; operational logging
conventions live in `standards/logging_and_observability_standard.md`. The
`OperationResult` envelope (ADR-001) carries `success`/`error`/`code` for *expected*,
caller-handled outcomes; it does not license swallowing *structural* failures, which must
still be raised. Observability must support understanding. Failure must never be silent.
