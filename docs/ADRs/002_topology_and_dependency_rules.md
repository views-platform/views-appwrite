# ADR-002: Topology and Dependency Rules

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

The entire point of `views-appwrite` is to fix a dependency problem. Today two repos
(`views-pipeline-core`, `views-faoapi`) each carry their own ~90%-identical copy of the
Appwrite client because `views-faoapi` was deliberately decoupled from the pipeline-core
"God-repo." The copies drift. The roadmap's target is a clean **DAG**: `views-appwrite`
depends on nothing in the platform, and every consumer depends *down* onto it.

That inter-repo discipline only holds if the package's *internal* topology is also
controlled. Without explicit dependency rules, the facade and managers can grow circular
references, the compat layer can start reaching back into business logic, and the
package can re-acquire a dependency on a consumer concept (as it once did via
`ModelPathManager`). A clear rule is required to define **who may depend on whom**, both
inside the package and across the platform.

---

## Decision

This repository enforces a strict, directional dependency structure, at two levels.

> Dependencies must follow declared architectural direction.
> No component may depend on a layer above it.

**Inter-repo (the platform DAG):**
- `views-appwrite` depends only on the Appwrite SDK. It must **never** import from
  `views-pipeline-core`, `views-faoapi`, `views-postprocessing`, or any consumer.
- Consumers depend down onto `views-appwrite`. Consumers do not depend on each other
  through it.

**Intra-package (the module layers):**
- `compat` and `auth` are the lowest layer (depend only on the SDK / stdlib).
- `client` depends on `compat`/`auth`.
- the resource managers (`storage`, `metadata`, `cache`) depend on `client`/`compat`.
- `datastore` (the facade) sits at the top and depends on the managers.
- Nothing lower may import the facade.

Dependency direction must remain acyclic. Violations are architectural defects.

---

## Layering Principle

Where layers exist, the following invariant applies:

- Higher-level modules may depend on lower-level modules (`datastore` → `storage`).
- Lower-level modules must not depend on higher-level modules (`compat` must not import `datastore`).
- Cross-layer shortcuts are forbidden (a manager must not bypass `client` to call the SDK directly in a way that skips auth/version handling).

Dependency direction must remain acyclic.

---

## Architectural Boundaries

Each component must:

- Declare its responsibility zone (see ADR-001),
- Respect dependency direction (this ADR),
- Avoid implicit cross-layer coupling.

This ADR governs **structural dependency direction only**.

> The definition and validation of boundary contracts (the `AppwriteConfig` schema, configuration validation, the `OperationResult` handshake) are governed separately by ADR-009.

Topology defines *who may depend on whom*.  
ADR-009 defines *what must be true at the boundary*.

---

## Forbidden Patterns

Examples of architectural violations specific to this package:

- Any module under `views_appwrite` importing from a consumer repo (re-acquiring `ModelPathManager` is the canonical example to avoid).
- `compat` importing from `datastore`, `storage`, or `metadata` (the shim must stay at the bottom).
- A resource manager importing the `DatastoreManager` facade.
- A consumer reaching "through" `views-appwrite` to couple to another consumer.

If a dependency feels “convenient but wrong,” it probably is.

---

## Consequences

### Positive

- The platform DAG is preserved: SDK upgrades and bug fixes propagate by a version bump, not N copy-pastes.
- `views-faoapi` and `views-pipeline-core` stay independent of each other.
- Internal layering keeps the evolving `compat` layer from contaminating the stable facade.

### Negative

- Consumers must inject what they previously imported (e.g. pass `cache_dir` instead of a path manager).
- May require additional abstraction at the consumer boundary.

These costs are accepted intentionally.

---

## Notes

This ADR defines structural direction of dependencies.

It does not define:

- boundary contract validation (ADR-009),
- semantic authority (ADR-003),
- or testing obligations (ADR-005).

Topology governs structure.  
Contracts govern interaction.
