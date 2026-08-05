# The Consumer-API Deployment Pattern — coordinates, secrets, and what a box can prove about itself

> **SCOPE BANNER: this is a platform pattern, not this repository's architecture.** It describes how
> *any* VIEWS consumer API reaches production and where its configuration comes from. It is
> referenced **by URL at a pinned tag** from each consumer repo's own concrete deployment ADR. It
> imposes nothing on this repository, which has no runtime.

| Field | Value |
|---|---|
| Status | **Accepted** — operator decision, 2026-08-05 |
| Version | **1.0.0** (changes by supersession + version bump; **never silent edit** — consumers pin) |
| Companion | [`appwrite_seam_contract.md`](appwrite_seam_contract.md) — governs *identity and credentials*; this document governs *how a box is built*. Related, **separately versioned** (§7) |
| Applies to | `views-faoapi`, `views-crafdapi`, `views-publicapi` (planned), and every future clone |
| Requested by | views-appwrite#54, from the views-crafdapi seat, after the ADR-035 review (views-crafdapi#34) |

---

## 0. Why this document exists here, and the fact that it is provisional

**The gap.** `views-faoapi` and `views-crafdapi` realize the same deployment pattern. It is written
down only as *per-repo concrete ADRs* — crafdapi's ADR-035 and faoapi's twin. A third clone's author
must therefore reverse-engineer the principle from two implementations, and will reasonably copy
whichever box they looked at. That is how `views-faoapi`'s hand-built environment nearly became the
platform's convention by default rather than by decision.

**Why here.** Operator decision, 2026-08-05: this repository's charter is *platform contracts and
consumer-API strategy*, not the Appwrite seam alone.

> **This charter is explicitly provisional.** The operator's words: *"maybe we'll shuffle around
> responsibilities in the future, but for now this seam is the lesser of a bunch of evils."*
>
> That sentence is recorded rather than smoothed away, because on this platform a provisional
> arrangement stated once and repeated becomes a permanent one nobody remembers choosing. It has
> happened three times in the week before this ADR was written: a relayed key expiry that was
> thirteen days wrong, a docstring citing a þing verdict that did not say what it claimed, and a
> version number that could stand still through a content change. **If this document is ever moved,
> that is the plan working, not a reversal.**

**What this is not.** It is not a rulebook for how a repo lays out its own deployment scripts. §5.4
of the seam contract's reasoning applies: the concrete realization is duplicated-with-variation
across repos on purpose (CCP — they change for different reasons and at different times). This
document states the **properties** each realization must have, never the code that produces them.

---

## 1. The pattern in one paragraph

A consumer API needs a set of **non-secret coordinates** (endpoint, project id, bucket and collection
ids and names, metadata database) and exactly **one secret** in its process environment. Coordinates
are **read from the owned, versioned registry**. The secret comes **only from the operator**. Both
are assembled **once, at bootstrap**, into a static environment file that the service unit reads. The
box then **records which version of the registry built it**, so the question *"am I current?"* has an
answer that does not require a human to remember.

---

## 2. Coordinates come from the registry — and the box records which version

**Rule.** Coordinates are read from `coordinate_registry.toml` at a **pinned tag or commit**. They
are never typed by hand, never copied from another box, never baked into code, an example, or a
dataclass default.

**Rule.** The environment a bootstrap produces **must record the registry version it was built
from** — a stamped `APPWRITE_REGISTRY_VERSION` line, or equivalent.

### Why the stamp is the load-bearing half

The first rule is widely agreed and easy to state. The second is the one that keeps being skipped,
and without it the first is unenforceable.

A registry file with no recorded version is indistinguishable from a stale one. Between 2026-08-02
and 2026-08-05 the registry moved through **five versions** — v1.4.0, v1.4.1, v1.4.2, v1.4.3,
v1.4.4. A box provisioned on any of those days looks exactly like a box provisioned on any other. No
inspection of the box can tell you which, so no operator can answer whether it needs re-provisioning
without going and comparing values by hand — which is the work the registry exists to remove.

**The stamp costs one line and converts an unanswerable question into a `grep`.** It does not require
a git checkout on the box; it does not require network access at runtime; it does not require any
tooling that does not already exist.

**Worked precedent.** `views-postprocessing` declares `SEAM_CONTRACT_VERSION` and
`SEAM_CONTRACT_COMMIT` beside its coordinates and checks them. On **2026-08-03 that check fired
correctly** — it caught the registry moving to v1.4.0 and turned its own `development` red rather
than letting the divergence sit. That is the only genuine drift catch the platform has recorded, and
it is the model.

### A copied registry file is a weaker form, permitted with the stamp

The registry's own header says *"Never copy it into a repo… Reference by pinned URL/commit."* The
reason is **provenance, not secrecy** — a copied file cannot say where it came from.

A copy placed on a box is therefore acceptable **only** when the stamp is present, because the stamp
restores the property the copy destroyed. A **pinned checkout** is preferred and should be the
long-term form: it carries provenance intrinsically and makes re-deploys repeatable without
re-copying anything.

**Never copied under any circumstance: the secret.** Copying a *secret* between machines is the
retired copy-chain that þing-01 #275 exists to prevent, and no stamp makes it acceptable.

---

## 3. The secret comes from the operator, once, and never from a file that travels

**Rule.** The single secret is supplied by the operator at bootstrap. It is never sourced from a
`.env` that was authored elsewhere, never committed, never logged, never emitted by any generator.

**Rule.** The registry records secrets as **slots** — a name and its required scopes — and never as
values. A reader emits coordinates only; it must never emit a secret, and the mechanism that
guarantees this is that readers scan only the non-secret classes.

> **Precision that matters.** It is tempting to say "secrets are never emitted because their entries
> have no value." **That is the wrong mechanism and a dangerous thing to teach.** A secret carrying a
> value would still not be emitted, because its *class* is not scanned. And a value-less entry in a
> *scanned* class is a **fatal error**, not a safely-ignored one — conflating the two produced
> views-appwrite **C-29**, a day-long platform-wide registry outage in which every consumer silently
> received no coordinates at all.

### Rotation is a property of this pattern, not an afterthought

A bootstrap-time secret baked into a static environment file means **a rotated secret does not reach
a running service.** Re-running bootstrap on each box is the propagation mechanism, and there is no
other.

That is an accepted consequence, not a defect — but it must be stated, because it sets the cost of
every rotation. As of this version, both platform keys expire on **2026-11-17** within a
three-and-a-half-hour window (views-appwrite C-65), and every box provisioned under this pattern must
be re-bootstrapped before then.

---

## 4. Deploys are tag-gated

**Rule.** A deploy is identified by a **tag**, and the tag, the version in `pyproject.toml`, and the
lockfile must agree. A box records the tag it is running.

The point is not ceremony. It is that "what is running?" and "what should be running?" must be
answerable by comparison rather than by recollection, and a tag is the only artifact that survives
the person who deployed it.

---

## 5. Serving is fail-visible: empty or stale is never served as if it were correct

**Rule.** A consumer API that cannot serve correct data must **fail visibly** — an error status, not
an empty success. Empty results, stale results, and missing coordinates are all failures, and each
must be distinguishable from a legitimate empty answer.

This is the platform's **Cluster J** defect class, named in views-pipeline-core: *"a system that
cannot distinguish 'no' from 'I could not tell', and answers anyway."*

**Why this belongs in a deployment ADR rather than only in an application one.** The most likely
cause of silently-wrong serving is not application logic — it is a **misconfigured box**. A
coordinate that is wrong but present does not raise. It resolves. The service starts, answers
requests, and returns data from the wrong container, and every health check passes.

That is not hypothetical. `views-faoapi`'s production environment file has been byte-identical since
2026-07-20, was hand-authored rather than generated, and contains duplicated variable names — where
a duplicate key resolves last-wins, silently. Its values have **never been compared against the
registry** (views-faoapi#360). The service is up. Nobody has established that it is right, and
"the service is up" has been doing the work of "the values are correct" for four months.

**Corollary.** A deployment is not verified by the service starting. It is verified by comparing
what the box holds against what the registry says it should hold.

---

## 6. Per-caller isolation

**Rule.** Where a consumer API serves multiple callers, anything cached must be **partitioned by
caller**, so no caller can observe another's data through a shared cache.

The executable statement of this invariant is the seam's conformance vector
([`conformance_vector.md`](conformance_vector.md)), which a consumer runs against its own
implementation. This document does not restate the invariant; restating it would create a second
source of truth, which is the failure this whole family of documents exists to prevent.

---

## 7. Consumers reference this by pinned tag — and that is the rule most likely to decay

**Rule.** Each consumer repo's concrete deployment ADR **references this document by URL at a pinned
tag**, never by name alone, never at `/blob/main/`, never by copying its text.

**Rule.** This document is **versioned independently of the seam contract.** They govern different
things and change for different reasons: the seam contract governs identity and credentials, this
governs how a box is built. Forcing them into lockstep would make every deployment clarification
appear to be a credential change, and vice versa.

### Why this rule needs a check, not just a sentence

The seam contract's §10 already requires pinning, and it has decayed at every opportunity:

| Consumer | State when audited |
|---|---|
| views-pipeline-core | pinned to a tag — and stranded three versions back, because no newer tag existed until 2026-08-03 |
| views-faoapi | pinned to a commit that was four versions stale |
| views-datafactory | linked to `/blob/main/` — not a pin |
| views-models, views-postprocessing | commit pins |
| crafdapi ADR-035 | **states twice that it references the contract "by URL at a pinned commit" and contains no URL at all** |

The last row is the instructive one: the document asserting compliance was the document not
complying, and nothing could have noticed.

**So: a pin rule without a mechanical check is a wish.** Consumers are encouraged to add one — a test
that scans for pins rather than listing them, asserts they name a single tag, and does *not* check
freshness (that needs a network call, and §10 reserves the upgrade decision to the consumer).
`views-pipeline-core`'s `tests/test_seam_contract_pin_is_coherent.py` is the reference
implementation: it makes the upgrade decision **atomic and visible without making it**.

---

## 8. What this document deliberately does not specify

Named so that silence is not read as permission:

- **How a repo structures its deployment scripts.** Duplicated-with-variation, per CCP.
- **Which process manager, host, or platform.** Not platform surface.
- **The wire format, payload eligibility, or data contracts.** Governed elsewhere, by repos that own them.
- **Whether a given repo should exist.** Not a deployment question.

---

## 9. Change process

Supersession, never erasure. Every change bumps the version. Consumers reference a pinned tag and
upgrade deliberately. **A published tag is never moved** — to correct a published version, cut a new
one and supersede.

Where this document records **observed state** rather than obligation, that state is marked as such,
and a version bump driven only by an observation carries no new obligation.

Disputes return to the þing.

---

## 10. Amendment Log

### v1.0.0 — 2026-08-05 — first version

Written in response to views-appwrite#54, which identified that the pattern existed only as two
per-repo realizations with no repo-agnostic statement, so a third clone author would have to
reverse-engineer it.

Content drawn from crafdapi ADR-035 (the concrete realization), its review at views-crafdapi#34, and
the platform's recorded incidents: **C-29** (a value-less coordinate killing every reader), **C-53**
(a version that could stand still through a content change), **C-65** (a relayed expiry that was
thirteen days wrong), and the faoapi environment divergence (views-faoapi#360).

**Two things this version states that were not in any prior document**: that the registry-version
stamp is the load-bearing half of "read from the registry" rather than a nicety (§2), and that a
deployment is verified by comparing the box against the registry rather than by the service starting
(§5).
