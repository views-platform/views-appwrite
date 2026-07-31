
# ADR-011: Cross-Repo Contracts Are Named, Not Numbered

**Status:** Accepted  
**Date:** 2026-07-31  
**Deciders:** VIEWS platform maintainers  

---

## Context

This repository hosts the platform's cross-repo seam contract. It was created under a numbered
scheme — `PLATFORM-001`, in a `docs/ADRs/platform/` tier — by analogy with this repo's
constitutional ADRs (`ADR-000`–`ADR-010`), where numbering works.

It has not worked here. Three observations, in order of weight:

**1. The identifier carries no information at the point of use.** Every citation in running code is
a bare number:

- `views-datafactory:src/datafactory_http/retry.py:23` — *"(PLATFORM-001 redaction clause: ...)"*
- `views-postprocessing:views_postprocessing/unfao/appwrite_env.py:3` — *"Names follow the
  PLATFORM-001 coordinate registry"*

A reader must leave the file to learn what was meant. The descriptive name already existed — it was
the filename, `PLATFORM-001_identity_secrets_configuration_contract.md` — and was discarded at every
citation: **144 of them across six repositories, measured 2026-07-31.**

That figure is a dated observation, not a constant, and it drifts in both directions: writing this
ADR added seven mentions to this repo, and `views-faoapi` gained three of its own while it was being
written. Re-measure before citing it; do not treat it as a fact with a shelf life.

**2. Unreadable identifiers hide staleness, and this has already cost us.**
`views-models:reports/technical_risk_register.md:1367` pinned the contract at commit `60674b2`. That
is v1.0.0. It stayed there through two version bumps and nobody noticed, because nothing about
`60674b2` signals age. The property that makes `PLATFORM-001` hard to remember is the same property
that makes a stale citation hard to spot: **neither string can be compared to anything by eye.**

**3. The number asserts a series that does not exist.** Numbered identifiers earn their keep when
there is a dense, indexed corpus to navigate — RFCs, CVEs, this repo's own constitutional ADRs,
where `ADR-003` is genuinely the third of a sequence a reader will traverse. There is **one**
platform contract. `PLATFORM-001` is an index into a set of size one.

The maintainer reported the problem unprompted on three separate occasions. An independent
multi-perspective engineering review reached the same finding from three directions — as a naming
defect, as lookup cost leaked into every consumer, and as identity complected with sequence.

---

## Decision

> **Cross-repo contracts are named for what they govern. A numbered scheme is adopted only when
> there is a real indexed series to navigate.**

Consequences of the rule:

- The seam contract is **The Appwrite Seam Contract**, file `appwrite_seam_contract.md`. *(This ADR
  fixes the name; the rename itself lands under issue #16 and ships as v1.3.0 — until then the file
  is still at its old path.)*
- **`PLATFORM-001` is retained as a recorded former name**, in the contract header and in the
  registry, so a reader arriving with the old identifier lands correctly. Aliases are kept, not
  deleted — the same discipline §10 of the contract applies to superseded clauses.
- **Historical text keeps the old name.** Amendment logs, risk-register rows and þing records
  describe what things were called at the time. Renaming history is erasure, which the contract's
  own change process forbids.
- If a second cross-repo contract is ever needed, it gets its **own descriptive name**. It does not
  get the next number in the retired scheme.

### This rule does not apply to this repository's constitutional ADRs

`ADR-000`–`ADR-010` and this file stay numbered. They *are* an indexed series: they are read in
order, they cross-reference each other by number, and `docs/validate_docs.sh` resolves those
references mechanically. The distinction the rule turns on is **whether a reader navigates a
corpus** (number it) **or resolves a single reference** (name it).

---

## Consequences

### Positive

- A citation states what it governs without a lookup. 134 mentions across six repos stop costing a
  round trip.
- Staleness becomes visible: `appwrite-seam-contract-v1.3.0` can be compared to
  `platform-001-v1.2.0` by eye. `60674b2` versus `28c897d` cannot.
- A new consumer API author reading any repo's code can tell what the referenced contract is for.

### Negative

- A rename touching six repositories. Mitigated by two facts: correctly-pinned URLs resolve against
  commits where the old path still exists, so **nothing downstream breaks**, and the alias means
  prose citations still resolve. Consumer repos update at their own pace.
- One more entry in the platform's vocabulary during the transition, until the old name falls out of
  active use.

These costs are accepted. They are one-time; the lookup cost was per-read, per-reader, forever.

---

## Notes

The rename ships as **v1.3.0** of the contract under its own change process (supersession plus
version bump, never a silent edit). The existing `platform-001-v1.2.0` tag is **not moved** — §10 of
the contract forbids moving a published tag, and anyone pinned to it continues to resolve to the
pre-rename file, correctly, indefinitely.

Recorded per `CLAUDE.md`: naming is an engineering decision, and a change that establishes a
standing rule a future contributor could violate without knowing it existed belongs in an ADR rather
than in a closed issue.
