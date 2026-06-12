# Instantiation Checklist — views-appwrite

Bootstrapped from base_docs templates on **2026-06-12** via the `init-base-docs` skill
(greenfield: no code exists yet; ADRs describe the intended architecture from `README.md`).

---

## Before You Start

- [x] Decide which adoption phase you're targeting — **all constitutional ADRs (000–009) adopted**
- [x] Identify the project's ontological categories — see ADR-001 (8 categories + explicit non-entities)

---

## ADR Adaptation

### All adopted ADRs
- [x] Update Status from the template placeholder to `Accepted` (ADR-004 intentionally `Deferred`)
- [x] Fill in Date (2026-06-12) and Deciders (VIEWS platform maintainers)

### Per-ADR adaptation notes
- [x] **ADR-000:** Path reference updated to `docs/ADRs/`
- [x] **ADR-001:** Ontological categories + stability defined and confirmed by user
- [x] **ADR-002:** Platform DAG + intra-package layering and forbidden patterns defined
- [x] **ADR-003:** Forbidden-behavior examples adapted (opaque metadata, no env-var fallback)
- [x] **ADR-005:** Red/beige/green examples grounded in the planned test suite
- [x] **ADR-006:** Anticipated CIC subjects listed
- [x] **ADR-007:** Contributor protocol paths verified (`contributor_protocols/*.md` exist)
- [x] **ADR-009:** Boundary examples adapted (`AppwriteConfig`, `OperationResult`)

---

## CICs

- [x] Replace placeholder active-contracts list in `CICs/README.md` — set to "None yet" (greenfield)
- [ ] Create intent contracts for non-trivial classes — **deferred to Phase 1** (no classes exist yet; subjects anticipated in `CICs/README.md` and ADR-006)

---

## Contributor Protocols

- [x] Adapt `contributor_protocols/silicon_based_agents.md` — grounded in Claude Code use + Phase 1 decomposition anti-truncation risk
- [x] Adapt `contributor_protocols/carbon_based_agents.md` — grounded in the generic-client boundary
- [x] Adapt or remove the hardened protocol template — **removed / not copied** (not ML / not reproducibility-critical; user-confirmed)

---

## Standards

- [x] Review `standards/logging_and_observability_standard.md` — grounded in package operations (upload/download/search, credential redaction, the `AppwriteSaver` anti-pattern)
- [ ] `standards/physical_architecture_standard.md` — **skipped** (user-confirmed). Deviation noted: planned `client.py` holds 3 classes and `metadata.py` holds 2, so the package is not strict 1-class-1-file.

---

## Risk Register

- [x] `reports/technical_risk_register.md` present and seeded with C-01…C-07 (from repo-assimilation, 2026-06-11)
- [x] Governing ADR present: **ADR-010** (renumbered from the standalone draft) referencing the register file

---

## Final Verification

- [x] No files still carry the unfilled template status marker (ADR-004 is `Deferred` by design)
- [x] No phantom references to non-existent files
- [x] All cross-ADR references resolve correctly
- [x] Run `validate_docs.sh` — passes (exit 0)
