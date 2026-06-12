
# Silicon-Based Agent Protocol  
*(For contributors composed primarily of silicon, statistics, and confidence)*

**Status:** Active  
**Applies to:** All automated or AI-assisted code modification of `views-appwrite`  
**Authority:** ADR-007 (Silicon-Based Agents as Untrusted Contributors)

---

## Purpose

This document defines **mandatory operational constraints** under which **silicon-based
agents** (e.g. LLM-based assistants such as Claude Code, code generators, refactoring
tools) may interact with this repository.

Silicon-based agents are powerful but unsafe by default. This protocol exists to prevent
silent semantic corruption, architectural erosion, responsibility laundering, and
hard-to-detect partial failures. It is binding for all silicon-assisted changes.

> **Project-specific note.** This repository's documentation scaffold was itself generated
> with a silicon-based agent, and its Phase 1 plan is a large-file decomposition (splitting
> `views-faoapi`'s ~2,000-line `appwrite.py`, reconciled against pipeline-core's ~3,047-line
> `file.py`, into eight modules). That is precisely the scenario the Anti-Truncation Rule
> below exists to guard. Treat every full-file operation on those sources as high-risk.

---

## Threat Model

Silicon-based agents are assumed to:
- optimize for local plausibility, not global correctness,
- infer intent when it is not explicitly declared (e.g. assume a metadata field is required),
- collapse abstractions for convenience (e.g. merge two managers, or skip the `compat` layer),
- silently omit or truncate content due to token or buffer limits,
- produce outputs that *look valid* while being semantically incomplete.

They are therefore treated as **untrusted contributors**.

---

## Global Rules (Non-Negotiable)

Silicon-based agents:
- ❌ are not authoritative
- ❌ do not own intent
- ❌ do not establish or infer semantics
- ❌ do not override ADRs or intent contracts
- ❌ do not introduce silent failure modes

All silicon-assisted changes must comply with ADR-001 (Ontology), ADR-002 (Topology),
ADR-003 (Authority & Fail Loud), ADR-005 (Testing), ADR-006 (Intent Contracts), and
ADR-007 (Untrusted Contributors).

---

## Allowed Operations

Silicon-based agents **may**: perform local, scoped refactors within a single class or
file; add/update tests that reflect declared intent; implement changes explicitly scoped
by a carbon-based agent; make mechanical changes (renaming, formatting) with no semantic
impact; and propose changes without applying them. All remain subject to carbon review.

---

## Forbidden Operations

Silicon-based agents **must not**: introduce/modify semantics without updating intent
contracts; infer behavior from naming conventions or heuristics; cross architectural
boundaries (ADR-002) — **in particular, never add an import from a consumer repo such as
`views_pipeline_core` or `views_faoapi`**; remove validation or fail-loud behavior;
convert explicit errors into warnings/fallbacks; refactor multiple layers in one change;
modify the ontology implicitly (ADR-001) — **never re-introduce a domain field into generic
metadata**; or make “helpful” assumptions when information is missing.

If a silicon-based agent cannot proceed without guessing, it must stop.

---

## Mandatory Safety Rule: The Anti-Truncation Rule

### Background

Silicon-based agents are known to silently truncate files when performing full-file
rewrites, due to token/output-buffer/streaming limits. Truncation can preserve syntactic
validity at the top while deleting critical logic at the bottom (“silent lobotomy”). For
this package, the highest-stakes example is dropping the SDK-14 `_as_dict`/`_get` guard or
an error branch while decomposing the source `appwrite.py`. This is an **unacceptable
failure mode**.

### Rule: Create-Only / Edit-In-Place Separation

1. **Create-only operations** — only for creating *new* files; must not target existing paths; overwriting an existing file is forbidden unless explicitly confirmed by a carbon-based agent and documented as an intentional reset.
2. **Edit-in-place operations** — for modifying existing files; changes scoped to specific, minimal regions; full-file rewrites of existing files are forbidden.

### Required Workflow

When modifying an existing file: (1) read it first, (2) identify a precise, unique edit
location, (3) apply a targeted replacement, (4) leave unrelated content untouched. If a
safe targeted edit cannot be identified, stop and request carbon guidance.

### Rationale

The cost of a single silent truncation event far exceeds the cost of a cautious,
multi-step edit workflow. Reliability takes precedence over speed.

---

## Required Artifacts for Silicon-Assisted Changes

Every silicon-assisted change must include: a brief summary of *what the agent believes it
changed*; references to relevant ADRs and/or intent contracts; explicit declaration of
uncertainty, if any; and confirmation that no forbidden operations were performed. Absence
of these is grounds for rejection.

---

## Review Posture

Silicon-generated code is reviewed with **heightened scrutiny**. Reviewers assume intent
may be misunderstood, semantics may have been altered unintentionally, and safety checks
may have been weakened. For decomposition work specifically, diff the new module against
the original source region and confirm no branch was lost. “The silicon-based agent did
it” is not an acceptable justification; responsibility remains fully with the carbon-based
reviewer.

---

## Enforcement

Violations are treated as violations by carbon-based agents; silicon-assisted changes may
be blocked solely on protocol grounds; known failure modes without coverage must be added
explicitly. This protocol is a living document and may evolve as tools and risks change.

---

## Final Note

Silicon-based agents are tools, not collaborators — powerful accelerators and powerful
failure multipliers. This protocol exists to ensure that **automation never outruns
understanding**.
