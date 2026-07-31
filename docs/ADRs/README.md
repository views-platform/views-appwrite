
# ADR README and Governance Map — views-appwrite

This repository uses Architecture Decision Records (ADRs) to govern structural, semantic,
and operational behavior. Because `views-appwrite` is currently a roadmap (no code yet),
these ADRs describe the **intended** architecture; when Phase 1 implementation begins,
code must conform to them.

ADRs are divided into:

1. **Constitutional ADRs (000–009)** — foundational architectural rules.
2. **Governance ADRs (010)** — the technical risk register.
3. **Project-Specific ADRs (011+)** — domain/implementation decisions (none yet).

---

## Constitutional ADRs

- **ADR-000** — [Use of ADRs](000_use_of_adrs.md). Establishes the ADR practice.
- **ADR-001** — [Ontology of the Repository](001_ontology_of_the_repository.md). The closed set of allowed categories (Configuration, Result Envelope, SDK Client Adapter, Compatibility Shims, Resource Managers, Auth Strategies, Facade, Metadata Value) and the explicit non-entities (domain logic, env-var loading, domain vocabulary).
- **ADR-002** — [Topology and Dependency Rules](002_topology_and_dependency_rules.md). The platform DAG (depend down onto `views-appwrite`) and the intra-package layering.
- **ADR-003** — [Authority of Declarations Over Inference](003_authority_of_declarations_over_inference.md). Consumer owns metadata meaning; fail loud on ambiguity.
- **ADR-004** — [Rules for Evolution and Stability](004_rules_for_evolution_and_stability.md) — **Deferred** (activate at `v0.1.0` when a consumer pins it).
- **ADR-005** — [Testing as Mandatory Critical Infrastructure](005_testing_as_mandatory_critical_infrastructure.md). Red/beige/green doctrine; contract tests during migration.
- **ADR-006** — [Intent Contracts for Non-Trivial Classes](006_intent_contracts_for_non_trivial_classes.md). CIC requirement.
- **ADR-007** — [Silicon-Based Agents as Untrusted Contributors](007_silicon_based_agents_as_untrusted_contributors.md). Anti-truncation rule for the Phase 1 decomposition.
- **ADR-008** — [Observability and Explicit Failure](008_observability_and_explicit_failure.md). Package fails loud; consumer owns degradation.
- **ADR-009** — [Boundary Contracts and Configuration Validation](009_boundary_contracts_and_configuration_validation.md). `AppwriteConfig` as a validated first-class artifact.

## Governance ADRs

- **ADR-010** — [Technical Risk Register](010_technical_risk_register.md). Formalises `reports/technical_risk_register.md` (seeded with C-01…C-07).
- **ADR-011** — [Cross-Repo Contracts Are Named, Not Numbered](011_naming_of_cross_repo_contracts.md). Retires the `PLATFORM-NNN` scheme; the seam contract becomes *The Appwrite Seam Contract*. Constitutional ADRs stay numbered — they are a series a reader traverses.

---

## Governance Structure (Conceptual Map)

- **Ontology (001)** defines what exists.
- **Topology (002)** defines structural direction.
- **Authority (003)** defines who owns meaning.
- **Boundary Contracts (009)** define interaction rules.
- **Observability (008)** enforces failure semantics.
- **Testing (005)** verifies system integrity.
- **Intent Contracts (006)** bind class-level behavior.
- **Automation Governance (007)** constrains silicon-based agents.
- **Risk Register (010)** tracks known gaps against the above.

Together, these define the invariant layer of the system.

---

## Suggested Project-Specific ADRs (011+) — candidates for when Phase 1 begins

These are *candidates* surfaced from the roadmap and risk register, not yet written:

- **ADR-011 (candidate):** SDK compatibility & version-pinning strategy — ratify `appwrite>=5.0.0` broad pin + runtime normalisation in `compat` (roadmap §SDK Compatibility; risk C-03).
- **ADR-012 (candidate):** `AppwriteConfig` schema & the `path_manager`→`cache_dir` migration (roadmap D-4; risk C-04).
- **ADR-013 (candidate):** Metadata is opaque `Dict[str, Any]` — no enforced schema (roadmap D-3; the formal statement behind ADR-001 Category 8).
- **ADR-014 (candidate):** Exception taxonomy for `DatastoreManager` so consumers can catch specific types instead of bare `Exception` (risk C-06; ADR-008).
- **ADR-015 (candidate):** Versioning & release policy / semver for consumers — likely supersedes the deferred ADR-004 (risk register R4/C-05).

---

## Recommended Adoption Order

Constitutional ADRs are designed to be adopted incrementally:

- **Foundation:** ADR-000, ADR-003, ADR-008 (load-bearing fail-loud invariants).
- **Structure:** ADR-001, ADR-002.
- **Testing & Intent:** ADR-005, ADR-006.
- **Boundaries & Automation:** ADR-007, ADR-009.

ADR-004 (Evolution & Stability) is intentionally deferred; activate it when `v0.1.0` ships
and external consumers begin pinning the package.
