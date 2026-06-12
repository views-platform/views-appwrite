
# ADR-010: Technical Risk Register as a Governance Artifact

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

`views-appwrite` is currently a planning repository: a single `README.md` roadmap for a
not-yet-built shared Appwrite client to be extracted from the duplicated code in
`views-pipeline-core` and `views-faoapi`. A repo-assimilation pass (2026-06-11) surfaced
a set of forward-looking technical risks (SDK compatibility asymmetry, configuration
divergence, duplication drift, silent upload-failure behaviour). These are mostly
**latent and trigger-conditioned** — they become acute only when extraction begins or
when a consumer/SDK change fires — and several reference code in *external* repos.

Such risks have no natural home in the codebase (there is none yet) and would otherwise be
rediscovered rather than tracked. They need a durable, structured place that survives the
gap between the roadmap and the implementation.

This ADR was originally drafted standalone (as ADR-0001) during the first
`register-risk` run; it has been renumbered to **ADR-010** to sit after the
constitutional ADRs (000–009) introduced by the documentation-governance framework.

---

## Decision

Establish `reports/technical_risk_register.md` as the single, authoritative technical
risk register for this repository. All audit-derived findings (repo-assimilation,
expert-code-review, test-review, falsification, etc.) are funnelled into it through the
`register-risk` skill, which enforces deduplication, tier assignment, and trigger-quality
gating. The register is curated and prioritised via the `review-rr` skill.

### Concern format

Each entry has: an **ID** (`C-xx` for concerns, `D-xx` for disagreements; permanent, never
reused — gaps indicate merged/resolved entries), a **Tier** (1–4), a **Source** + date, an
actionable **Trigger**, a **Location**, and a grounded **Narrative**.

### Tier definitions

| Tier | Severity | Criteria |
|------|----------|----------|
| 1 | Critical | Silent data corruption or output incorrectness with no error signal. |
| 2 | High | Structural fragility that causes failures under realistic change scenarios. |
| 3 | Medium | Maintainability or coupling issues that increase cost of change. |
| 4 | Low | Code-quality observations with no correctness or reliability impact. |

Header counts (Total / Open / Resolved) are maintained manually on every change.
Resolution moves an entry to the Resolved section; the ID is never reused.

---

## Rationale

This ADR makes the risk register a first-class governance artifact rather than an ad-hoc
note. It complements the constitutional ADRs: where ADR-003/008 mandate fail-loud and
ADR-009 mandates validated boundaries, the register tracks the *known gaps* against those
principles until they are closed. It is the operational counterpart to the roadmap's own
"Risks and Things to Be Mindful Of" section, with enforced structure and triggers.

---

## Consequences

### Positive
- Forward-looking risks survive the planning→implementation gap and are re-checked when their triggers fire.
- Deduplication and tiering keep the register honest and prioritisable.
- The register is the seed of future project-specific ADRs (010+) when a risk graduates into a ratified decision.

### Negative
- Many entries reference external repos (`views-pipeline-core`, `views-faoapi`); those locations must be confirmed when extraction (Phase 1) begins.
- Requires discipline: entries are removed only by resolution, not silent deletion.

---

## Implementation Notes

- Register file: `reports/technical_risk_register.md` (seeded 2026-06-12 with seven concerns C-01…C-07 from the repo-assimilation pass).
- Add risks via the `register-risk` skill; curate/prioritise via `review-rr`.
- If the register file is moved under a gitignored path, stage it with `git add -f`.

---

## References

- `reports/technical_risk_register.md`
- `README.md` (roadmap §"Risks and Things to Be Mindful Of", R1–R7)
- repo-assimilation output, 2026-06-11
