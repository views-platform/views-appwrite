
# ADR-007: Silicon-Based Agents as Untrusted Contributors

**Status:** Accepted  
**Date:** 2026-06-12  
**Deciders:** VIEWS platform maintainers  

---

## Context

This repository is expected to be built and maintained with substantial help from
**silicon-based agents** (LLM-based coding assistants — this governance scaffold itself
was generated with one). The Phase 1 plan is specifically a *decomposition* task: take
`views-faoapi`'s ~2,000-line `appwrite.py` (and reconcile it against pipeline-core's
~3,047-line `file.py`) and split the monolith into eight modules. That is exactly the
kind of large-file, full-rewrite operation where silicon-based agents are most prone to
silent truncation — preserving a valid-looking top of a file while dropping logic at the
bottom (the `_as_dict` guard, an error branch, the cache-cleanup path).

Silicon-based agents differ fundamentally from carbon-based agents:

- They optimize for local plausibility, not global correctness
- They lack understanding of system intent and architectural constraints
- They may infer, invent, or collapse semantics silently (e.g. re-introduce a domain field into generic metadata)
- They may introduce partial or structurally valid failures (truncation)
- They do not experience uncertainty, responsibility, or risk

Without explicit guardrails, they introduce architectural, semantic, and safety risks
that are hard to detect post hoc.

---

## Decision

Silicon-based agents are treated as **untrusted contributors**.

They may assist in code modification **only under explicit, documented constraints**, and
**never as autonomous authorities**. All silicon-based agent activity is subject to the
same (or stricter) architectural rules as carbon-based agents, including:

- declared ontology (ADR-001) — must not re-introduce domain concepts disclaimed by the package,
- enforced topology (ADR-002) — must not add a dependency on a consumer repo,
- explicit semantic authority and fail-loud behavior (ADR-003),
- mandatory testing obligations (ADR-005),
- intent contracts for non-trivial classes (ADR-006),
- explicit failure and observability requirements (ADR-008).

The concrete operational rules are defined in the **Silicon-Based Agent Protocol**
(`contributor_protocols/silicon_based_agents.md`) — note especially its anti-truncation
rule, which is directly relevant to the Phase 1 decomposition.

---

## Scope

Applies to: LLM-based coding assistants, AI refactoring tools, code-generation systems,
and any non-carbon-based agent that proposes or applies code changes.

Does **not** regulate: carbon-based agents (`contributor_protocols/carbon_based_agents.md`),
read-only analysis/explanation tools, or tooling that does not modify repository state.

---

## Authority and Responsibility

Silicon-based agents are not authoritative, do not own intent, do not establish
semantics, and do not override architectural decisions.

Carbon-based agents remain fully responsible for the correctness of changes, adherence to
ADRs and intent contracts, and the consequences of merging silicon-assisted code. “No
carbon-based agent reviewed it” is not an acceptable justification.

---

## Enforcement

- Silicon-assisted changes must comply with `contributor_protocols/silicon_based_agents.md`.
- Violations of architectural ADRs by silicon-based agents are treated as violations by carbon-based agents.
- Reviewers apply **heightened scrutiny** to silicon-assisted changes — in particular, verifying that a decomposed module did not silently lose a branch present in the source file.

---

## Consequences

### Positive
- Prevents silent architectural erosion and accidental re-coupling to domain logic
- Preserves semantic integrity under automation
- Makes responsibility explicit and traceable

### Negative
- Limits agent autonomy
- Requires carbon-based agents to actively constrain and review agent output

These trade-offs are accepted intentionally.

---

## Notes

This ADR establishes **that** silicon-based agents are constrained. It does not define
**how** — operational rules live in the Silicon-Based Agent Protocol
(`contributor_protocols/silicon_based_agents.md`), which may evolve as tools and risks change.
