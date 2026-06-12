
# ADR-009: Boundary Contracts and Configuration Validation

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

`views-appwrite` is almost entirely *boundary*. Its reason to exist is the interface
between consumer repos and Appwrite: consumers hand it an `AppwriteConfig` and opaque
metadata; it hands back `OperationResult`. The roadmap is explicit that the package must
**not** read environment variables or hold hidden defaults — "the consumer constructs
`AppwriteConfig` with values it obtained however it likes." This makes the configuration
boundary the single most important contract in the system, and the place silent drift
would do the most damage (it caused the two source copies' configs to diverge — risk
register C-04).

Ambiguous configuration, hidden defaults, and implicit contracts introduce silent
semantic drift and runtime fragility. To preserve fail-loud guarantees (ADR-003), all
boundaries must be explicit and validated.

---

## Decision

This repository adopts the following invariants:

> All architectural boundaries must declare explicit contracts.  
> All configuration must be validated at entry.  
> No semantic defaults may exist silently.

---

## 1. Boundary Contracts

The package's boundaries and their contracts:

- **Consumer → package (config):** `AppwriteConfig` is the explicit input schema (endpoint, project_id, credentials, auth_method, bucket/collection/database IDs, cache TTL, timeouts, `cache_dir`). No field is sourced implicitly.
- **Package → consumer (results):** every operation returns `OperationResult{success, data, error, code}`; `.data` contains plain dicts only, never raw SDK objects.
- **Package → SDK:** all calls go through `AppwriteClient`; responses cross back through the `compat` layer so the rest of the package sees one normalised shape.
- **Consumer → package (metadata):** an opaque `Dict[str, Any]` whose schema the consumer owns (ADR-003). The contract is precisely that the package makes *no* schema demand.

Implicit contracts are prohibited. If a boundary assumption cannot be declared clearly, the boundary must be redesigned.

---

## 2. Configuration as First-Class Artifact

`AppwriteConfig` is an architectural artifact, not a convenience layer. It must be:

- Explicit — every connection value is a declared field.
- Externally constructed — no `os.getenv`/`load_dotenv` inside the package (ADR-001 non-entity).
- Validated before use — see §3.
- Free of hidden defaults that change meaning. Derived conveniences (e.g. `bucket_name`/`database_name` defaults, `auth_method` string→enum) are computed explicitly in `__post_init__`, not guessed at call time.

Changing configuration must not silently alter system meaning.

---

## 3. Validation at Entry (Handshake Principle)

`AppwriteConfig` and external inputs must be validated at the boundary — before any SDK
call or state mutation. The system must fail early if required fields are missing, types
are incorrect, redundant parameters disagree, or declared invariants are violated.

Borrowed or assumed state is prohibited. In particular, the migration replaces the
`path_manager` field with an explicit `cache_dir: Optional[Path]`; the package must not
reach back into a consumer's path manager to derive state (ADR-002).

---

## 4. Separation of Configuration Domains

Configuration domains must be conceptually separated. For `AppwriteConfig`, illustratively:

- Connection parameters (endpoint, project_id, credentials, auth_method)
- Target parameters (bucket_id, collection_id, database_id)
- Behavioral parameters (cache TTL, timeouts, `cache_dir`)

Cross-domain coupling must be explicit. Behavior-affecting configuration must not be disguised as informational.

---

## 5. Redundancy and Consistency Checks

Where ambiguity risk is high, explicit redundancy is preferred and must be validated for
consistency. The salient case here: during migration, `views-appwrite`'s `AppwriteConfig`
must be a documented **superset** of both source repos' config fields (risk register
C-04). Field presence and compatibility must be checked, not assumed.

---

## 6. Failure Semantics

Configuration validation failures must be logged (ADR-008), raised explicitly (ADR-008),
and halt execution. Warnings are insufficient for structural configuration errors.

---

## Consequences

### Positive
- Eliminates the hidden configuration drift that diverged the source copies
- The no-env-vars rule makes the package testable and portable across consumers
- Strengthens fail-loud guarantees at the most important boundary

### Negative
- Consumers must supply complete, explicit configuration
- Adds validation boilerplate in `AppwriteConfig.__post_init__` and at entry points

These costs are accepted.

---

## Notes

This ADR does not prescribe specific configuration libraries or schema frameworks. It
governs *what must be true at the boundary*; ADR-002 governs *who may depend on whom*.
