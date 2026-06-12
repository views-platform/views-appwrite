# Class Intent Contracts (CICs) — views-appwrite

This directory contains **Intent Contracts** as defined in [ADR-006](../ADRs/006_intent_contracts_for_non_trivial_classes.md).

An Intent Contract is a human-readable, unambiguous declaration of:

- what a non-trivial class is meant to do,
- what it must never do,
- its invariants,
- and its failure semantics.

Intent Contracts are architectural artifacts. They are not implementation documentation.

---

## Status: infrastructure only (no contracts yet)

`views-appwrite` currently contains no code — it is a roadmap (see `README.md`). This
directory holds the template (`cic_template.md`) and this README. **Contracts are authored
during Phase 1**, as each class is implemented by decomposing `views-faoapi`'s
`appwrite.py`.

---

## When Is an Intent Contract Required?

Mandatory for: core domain classes, architectural boundary classes, orchestration
components, state-owning components, classes that enforce invariants, and classes that
modify semantics or transformation. Trivial value objects and pure utility functions do
not require one.

---

## Structure of an Intent Contract

Use `cic_template.md`. Each contract must define at minimum: Purpose, Responsibility
Boundary / Non-Goals, Inputs and Assumptions, Outputs and Guarantees, and Failure
Semantics. For this brownfield-bound package, each CIC must also include a **Known
Deviations** section once it documents real code.

---

## Active Contracts

None yet. Contracts will be created in Phase 1.

Anticipated subjects (from the ADR-001 ontology — names provisional, no files exist yet):
DatastoreManager (facade/orchestrator), StorageManager, MetadataManager, CacheManager
(state-owning resource managers), AppwriteClient (SDK boundary), the AuthManager strategy
hierarchy, and probably AppwriteConfig (non-trivial due to `__post_init__` normalisation
and its single-source-of-truth role). The `compat` functions are not classes and are
governed by tests, not a CIC.

---

## Governance Relationship

Intent Contracts are governed by:

- ADR-006 (Intent Contracts for Non-Trivial Classes)
- ADR-003 (Authority of Declarations)
- ADR-005 (Testing Doctrine)

If a class changes meaning, its Intent Contract must be updated.
