# Logging & Observability Standard — views-appwrite

**Status:** Active  
**Governing ADRs:** ADR-003 (Authority of Declarations Over Inference), ADR-005 (Testing), ADR-008 (Observability and Explicit Failure)  

---

## 1. Purpose

This document defines operational standards for logging behavior, log levels, error
propagation patterns, and observability expectations in `views-appwrite`. It
operationalizes:

> Structural failures must be raised explicitly and logged persistently. (ADR-008)

It does not redefine architectural principles.

---

## 2. Core Principles

### 2.1 Fail Loud and Persist

- Structural failures must be logged at `ERROR` or higher **and** raised as exceptions.
- Logging is not a substitute for raising; raising is not a substitute for logging.
- Silent degradation inside the package is prohibited. (A *consumer* may degrade gracefully — e.g. `AppwriteSaver` — but the package raises; see ADR-008.)

### 2.2 Logs Must Support Understanding

Logs must provide enough context to reconstruct state and include relevant identifiers —
for this package: `bucket_id`, `collection_id`, `database_id`, `file_id`, operation name
(upload/download/search/delete), detected SDK major version, and cache hit/miss. Logs
must not rely on tribal knowledge to interpret.

### 2.3 Logs Must Not Leak Sensitive Data

- API keys and session credentials (`AppwriteConfig.credentials`) must **never** be logged.
- Endpoints may be logged; credentials must be redacted.
- File *contents* must not be logged (log size/hash/`file_id`, not bytes).

---

## 3. Log Levels (Normative Definitions)

### DEBUG
Development diagnostics; detailed internal state (e.g. raw-then-normalised SDK response shape). Must not be required to understand production failures.

### INFO
High-level lifecycle events: start/finish of an upload/download/search, bucket
auto-provision, cache hit vs miss, target IDs and config summary (credentials redacted).

### WARNING
Unexpected but recoverable conditions that do **not** violate an invariant (e.g. a
retryable transient SDK error before a successful retry). Must not mask structural errors
or invariant violations.

### ERROR
Structural failure within a component: config validation failure, unrecognised SDK
response shape, an operation that cannot proceed correctly. Must be raised and logged.

### CRITICAL
System-wide / irrecoverable failure (e.g. corruption of the cache directory, inability to
authenticate at all). Immediate attention required.

---

## 4. Error Propagation Pattern

Structural errors follow this minimal pattern: construct a clear message, log it
(`ERROR`/`CRITICAL`), then raise the appropriate exception with the same message.

```python
err_msg = f"AppwriteConfig missing required field 'project_id'; cannot construct client."
logger.error(err_msg)
raise ValueError(err_msg)
```

Per ADR-008, the package should raise **specific, documented exception types** (not bare
`Exception`) so consumers can catch precisely. Spacing conventions are not mandated;
clarity and consistency are.

---

## 5. Logging Scope Expectations

### 5.1 Required Logging
- Operation start/finish (upload, download, search, delete, list)
- Bucket/collection/database auto-creation events
- Cache hit/miss and cache invalidation
- SDK version detection outcome
- Configuration summary at client construction (credentials redacted)
- All structural failures

### 5.2 Optional Logging
- Per-page details during paginated listing (DEBUG)
- Timing/performance metrics
- Detailed internal diagnostics

---

## 6. Log Structure and Context

Entries should include: timestamp, level, module/component name (e.g.
`views_appwrite.storage`), and relevant identifiers (`file_id`, `bucket_id`, operation).
Structured logging (JSON or key-value) is recommended where possible.

---

## 7. Alerting

Alerting is an operational layer built on logging. At minimum: `ERROR` and `CRITICAL`
logs must be alertable; `CRITICAL` must escalate; alert routing must avoid noise
amplification. Concrete alert routing is operational (it lives with the consumer/deploy
environment, e.g. the Hetzner shadow server) and may evolve.

---

## 8. Testing Requirements

Logging behavior must be testable where meaningful. Tests should verify that errors are
both logged and raised, that level separation works, and that credentials are never
emitted. Logging tests must not rely on manual inspection. (Aligns with ADR-005.)

---

## 9. Anti-Patterns (Prohibited)

- Swallowing exceptions without logging — **the documented pipeline-core `AppwriteSaver` catch-all is a consumer policy, not a license for the package to do this** (risk register C-06)
- Logging and continuing after an invariant violation
- Downgrading errors to warnings to “keep things running”
- Using `print()` for structural diagnostics
- Logging credentials, or logging entire file contents/objects without context

---

## 10. Evolution

This document may evolve independently of ADRs. If logging semantics change in a way that
affects system meaning, ADR-008 must be revisited.
