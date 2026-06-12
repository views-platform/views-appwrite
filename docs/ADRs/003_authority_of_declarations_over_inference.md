
# ADR-003: Authority of Declarations Over Inference

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

This package sits at a boundary where ambiguity is easy and dangerous. Appwrite
responses come in two shapes (SDK 13 dicts, SDK 14+ Pydantic models); metadata is an
opaque `Dict[str, Any]` whose meaning is owned by the consumer, not the package;
configuration is supplied entirely by the caller. Each of these is a place where code
could be tempted to *infer* intent — guess a field's meaning, assume a default endpoint,
silently coerce a missing config value.

The roadmap already records the cost of inference-by-convention: the two source repos
diverged partly because behaviour lived "in developers' heads" rather than in explicit
declarations, and `FileMetadata` was overloaded with domain fields inferred from usage.
A clear rule is required to define **where semantic authority lives** and how ambiguity
is resolved.

---

## Decision

In this repository:

> **All meaningful semantics must be explicitly declared.  
> Inference of semantics across component boundaries is forbidden.**

Concretely:
- **The consumer owns metadata meaning.** `views-appwrite` accepts `Dict[str, Any]` and passes it through unmodified. It must not infer that a field named `loa` means a level of analysis, or require any particular field. (ADR-001 Category 8.)
- **`AppwriteConfig` is the single source of truth for connection semantics.** The package must not fall back to environment variables or hidden defaults to fill missing config.
- **The compat layer normalises, it does not guess.** `_as_dict`/`_get` map known SDK response shapes to plain dicts; they must not invent fields that are absent.

If required semantics are missing, ambiguous, or contradictory, the system **must not guess**.

---

## Global Invariant: Fail Loud on Semantic Ambiguity

In this repository, **silent failure is considered a bug**.

Whenever required semantics are missing, ambiguous, contradictory, or inconsistent
across representations, the system **must fail loudly and immediately** — by raising an
explicit error, failing validation, or refusing to proceed.

Warning-only behavior, implicit fallbacks, or “best-effort” inference are **forbidden**
for any decision-relevant semantics, regardless of environment.

> **Known tension to resolve in implementation:** the roadmap preserves a *deliberate*
> graceful-degradation behaviour in pipeline-core's `AppwriteSaver`, which catches upload
> exceptions and logs instead of raising (risk register C-06). That policy lives in the
> consumer, not in this package. `views-appwrite` itself must fail loud: `DatastoreManager`
> should raise specific, documented exceptions. The consumer may then choose to degrade
> gracefully — but the package must never swallow the failure silently on the consumer's behalf.

---

## Rules of Semantic Authority

- Semantics must be **declared**, not inferred.
- Transformations are owned by the component that performs them.
- Metadata meaning is owned by the consumer; the package treats it as opaque.
- No component may guess another component’s intent.

Inference is permitted **only within a component’s internal logic**, never across component boundaries.

---

## Examples of Forbidden Behavior

- Inferring a required metadata field (e.g. assuming every upload has a `category`).
- Defaulting a missing `endpoint`/`project_id` from an environment variable.
- Guessing the file's serialisation format from its extension to auto-deserialize (the package returns bytes; the consumer deserializes).
- Proceeding after emitting a warning when a required `AppwriteConfig` field is absent.

If behavior matters, it must be declared.

---

## Consequences

### Positive
- Eliminates the silent semantic drift that caused the two source copies to diverge
- Improves reproducibility and debuggability
- Makes the consumer/package responsibility split unambiguous

### Negative
- Requires consumers to supply complete config and own their metadata schemas
- Errors surface earlier and more frequently (by design)

These costs are accepted intentionally.

---

## Notes

This ADR does not define:
- what concepts exist (ADR-001),
- or how components depend on each other (ADR-002).

It defines **who is allowed to say what something means**, and mandates **loud failure over silent misinterpretation**. Its runtime enforcement is detailed in ADR-008.
