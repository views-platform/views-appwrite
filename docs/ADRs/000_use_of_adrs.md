
# ADR-000: Use of Architecture Decision Records (ADRs)

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  
**Informed:** All contributors  

---

## Context

`views-appwrite` is a planned shared library: a single, independently-versioned
Appwrite client extracted from the duplicated Appwrite code currently living in
`views-pipeline-core` and `views-faoapi`. At the time of writing the repository
contains only a roadmap (`README.md`); no implementation exists yet. This is exactly
the moment at which architectural decisions are cheapest to record and most likely to
be lost: the scope boundary, the dependency direction, the vocabulary, and the SDK
strategy are all being decided now, before any code pins them down.

Decisions in such systems are:
- Made under uncertainty
- Revised over time
- Obvious to those present at the time, but opaque later
- Revisited implicitly, often leading to regressions or duplicated debate

Without a shared record of *why* decisions were made, the project risks:
- Re-litigating settled questions (e.g. "should this package hold a DataFrame helper?")
- Accidental reversals of critical design choices (e.g. the no-domain-logic boundary)
- Accumulating invisible technical and conceptual debt
- Losing institutional memory as contributors and consumer repos change

We therefore need a lightweight but rigorous mechanism to document **significant decisions**, their **rationale**, and their **consequences**. The roadmap's own "Decision Log" (D1–D7) is the seed of this practice; ADRs formalise it.

---

## Decision

We will use **Architecture Decision Records (ADRs)** to document significant technical, architectural, and conceptual decisions in this project.

ADRs are:
- Written in Markdown
- Stored in the repository under `docs/ADRs/`
- Numbered sequentially in three tiers: constitutional 000–009; governance 010; project-specific 011+ *(amended 2026-07-28, þing-01 / C-10: the previous two-tier text collided with ADR-010's occupancy)*. Cross-repo platform-seam contracts live in a fourth, prefixed tier: `docs/ADRs/platform/` with `PLATFORM-NNN` identifiers — unambiguous when cited from another repo's ADRs.
- Treated as first-class project artifacts

An ADR records **a decision**, not a discussion or a design proposal.

---

## What Is an ADR?

An ADR is a short, structured document that captures:
- The context in which a decision was made
- The decision itself
- The rationale behind it
- The alternatives that were considered
- The consequences (positive and negative)

An ADR answers the question:

> *“Why is the system the way it is?”*

—not just *“How does it work?”*

---

## When to Write an ADR

Write an ADR when making a decision that:
- Affects system architecture or data layout
- Constrains future design choices
- Changes assumptions or invariants
- Introduces or accepts technical debt
- Is likely to be questioned or revisited later
- Has non-obvious trade-offs

Examples relevant to this project include:
- What belongs inside the package versus in consumer repos (the scope boundary)
- The SDK compatibility strategy (broad pin + runtime normalisation)
- The configuration object's shape and the removal of `path_manager`
- The decision to accept opaque `Dict[str, Any]` metadata rather than typed schemas

Do **not** write ADRs for:
- Routine refactors
- Purely local implementation details
- Temporary experiments (unless they become permanent)

---

## What an ADR Is *Not*

An ADR is **not**:
- A full design document
- A tutorial or user guide
- A speculative roadmap
- A substitute for code comments
- A place to argue indefinitely

The goal is clarity and finality, not exhaustiveness.

---

## Structure and Template

All ADRs must follow the standard ADR template defined in this repository (`docs/ADRs/adr_template.md`).

The template enforces:
- Clear separation between context, decision, and rationale
- Explicit consideration of alternatives
- Honest accounting of consequences
- Traceability to code and discussions

Consistency matters more than perfection.

---

## Lifecycle of an ADR

ADRs have a status that reflects their lifecycle:

- **Proposed** — decision under consideration
- **Accepted** — decision is active and authoritative
- **Superseded** — replaced by a newer ADR
- **Deprecated** — decision remains but should no longer be used
- **Deferred** — a placeholder reserving the decision for later (e.g. ADR-004)

Decisions are never deleted.  
If a decision changes, it is **superseded**, not erased.

---

## Relationship to Code

ADRs and code must agree.

- Code should implement the decision described in the ADR
- Significant deviations require a new ADR or an update
- ADRs should be referenced from code, issues, or PRs when relevant

If code and ADRs disagree, the ADR is the source of truth — or a new ADR is required. (No implementation exists yet, so today the ADRs describe intended structure; when Phase 1 of the roadmap begins, code must conform to them.)

---

## Why We Use ADRs

We use ADRs to:
- Preserve institutional memory
- Reduce cognitive load for maintainers
- Make trade-offs explicit
- Enable principled disagreement
- Support onboarding and handover
- Prevent silent erosion of core design principles

ADRs are a tool for **engineering discipline under uncertainty**.

---

## Consequences

### Positive
- Clearer decision-making
- Fewer repeated debates
- Easier onboarding
- Better long-term coherence

### Negative
- Small upfront cost in writing
- Requires discipline to maintain
- Forces explicitness where ambiguity may feel easier

These costs are accepted intentionally.

---

## References

- `docs/ADRs/adr_template.md`
- `README.md` (project roadmap and Decision Log D1–D7)
- Project contribution guidelines
