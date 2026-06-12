
# ADR-008: Observability and Explicit Failure

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

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
- Fallback behavior must not hide semantic failure (auto-creating a missing bucket is an explicit, documented behavior — not a hidden fallback that masks an error).

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
