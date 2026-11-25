# What We Learned

**A working document. Not a decision record.** Nothing here obliges anyone to anything, and nothing
here has been ratified. It is where reading turns into something usable before it is clear which ADR,
if any, it belongs in.

**Status:** open and expected to grow. Started 2026-11-24.

---

## What this is for

The effort this document serves is one thing: **getting Appwrite out of the repositories that
currently contain it, and behind a single boundary, so that the vendor can be replaced and the same
fix never has to be written five times.** ADR-012 is the decision record for that effort. This is not.

We are reading the software-design literature against the platform's actual code, one book at a time.
Some of what comes out is specific enough to belong in a particular ADR's *Challenges and questions*
section, and goes there. Some is more general — a criterion, a reframing, a thing we now know we were
wrong about — and has no obvious home yet. Writing it into an existing ADR would overstate its
settledness; writing a new ADR would be premature. It goes here instead.

**Where the code checks live.** This document records what the literature says. It does not record
how to check whether our own code complies — that is `boundary_tests.md`, a catalogue of tests that
can be run against a repository, with what each one has said so far and what it cannot tell you.
Added 2026-11-25 after the tests accumulated past the point where they could be remembered.

**An entry graduates** when it becomes a decision, at which point it moves into an ADR and the entry
here says where it went. An entry can also die, and saying so is useful.

## How to add an entry

One section per source, in the order read. Each section answers three questions and no others:

1. **What the source says** that bears on this effort, quoted where it matters.
2. **What it changes for us**, concretely, with reference to our own code or documents.
3. **What it does not settle.** This is the part most likely to be skipped and most worth having.

Date each section. Where an entry corrects something we previously believed, say so plainly rather
than quietly replacing it.

---

## 1. Ousterhout, *A Philosophy of Software Design* — read 2026-11-23 and 2026-11-24

Chapters 4 (Modules Should Be Deep), 5 (Information Hiding and Leakage), 8 (Pull Complexity
Downwards) and 9 (Better Together or Better Apart?).

### What it changes for us

**The first question is not library-or-service. It is how wide the interface is.**

§4.4 defines a module's worth as a ratio: *"The benefit provided by a module is its functionality.
The cost of a module (in terms of system complexity) is its interface."* A module that hides a lot
behind a narrow interface is deep and earns its keep; one whose interface is nearly as complicated as
what it hides is shallow and does not.

Applied here: if the shared Appwrite component's operations mirror the SDK one for one, it is shallow
in either form. As a service it would add a network hop, a host that can fail and a release process,
while hiding nothing. As a library it would add a dependency and hide nothing. The duplication it was
built to remove would reappear, with every consumer still knowing the vendor's shape through a
different door.

ADR-012 currently has *"what operations it offers"* under **Still open**, beside which host the
service starts on. Those are not comparable in weight. Everything ADR-012 claims rests on an answer
it does not give.

**We now know what the shared component must actually own, and it is narrower than "the Appwrite
client".**

Measured on 2026-11-24 by comparing every identifier-like string literal in the Appwrite-facing and
delivery code of the writing side (`views-pipeline-core`, `views-postprocessing`) against the reading
side (`views-faoapi`, `views-crafdapi`). 73 appear on both sides; most are coincidence. Two clusters
are not, and they turned out to be very different in character.

*Cluster 1 — the vendor's error vocabulary — is real leakage.* `storage_file_not_found`,
`storage_bucket_not_found` and `collection_not_found` are hard-coded in three repositories.
`views-pipeline-core` holds them as named constants in one module
(`modules/appwrite/file.py:134-135`) and then bypasses its own constants twice
(`modules/datastore/datastore.py:413`, `modules/appwrite/provisioning.py:568`). The two APIs re-encode
them inline. A vendor rename reaches all three — which is the October TablesDB rename, the event
ADR-012 was written about, waiting to recur.

*Cluster 2 — the metadata record's shape — mostly dissolved on inspection, and the first version of
this finding was wrong.* `views-pipeline-core` declares its 13 fields in code
(`modules/appwrite/provisioning.py:108` and `:135`) under a governing contract
(`documentation/CICs/AppwriteProvisioner.md:46`). `views-postprocessing` has a module whose explicit
job is to be the only place that knows the document's shape
(`contract/store_metadata.py`, docstring: *"This is the only place that knows that shape."*). What is
missing is not a declaration but a cross-reference: the Appwrite Seam Contract points at neither.

**So the thing to remove from consumers is the vendor's mechanics and vocabulary, not the agreement
about what a delivery record is.** That is a narrower and clearer target than ADR-012's framing of
roughly 2,300 duplicated lines, and it is a better one, because lines of duplicated client code are
cheap to tolerate while duplicated vendor knowledge is what actually breaks on a rename.

**The answer to "what operations it offers" may already be written, twice.**

`views-postprocessing`'s store port is five methods. `views-pipeline-core`'s `DatastoreModule` is
twelve. Both are expressed in delivery and forecast terms rather than in Appwrite terms. ADR-012
points at both in passing and calls them *"interfaces that already exist in the right shape"*.

§4.3 explains why they are the right shape: an abstraction *"is a simplified view of an entity, which
omits unimportant details"*, and the vendor's vocabulary is precisely what is unimportant to a caller
who wants a forecast. So the open question has two candidate answers already implemented, and the
work is to reconcile five methods with twelve rather than to invent an interface.

**Two acceptance tests ADR-012 could adopt, which it currently lacks.**

- *Vocabulary.* The component's interface is expressed in forecasts and deliveries, never in buckets,
  files, collections or rows. This is checkable by reading the operation names.
- *Depth.* Count the operations the component offers against the number of distinct Appwrite calls
  they subsume. A ratio near one means a pass-through.

**A method, not just a conclusion.** §5.2 defines information leakage as the same design decision
reflected in several modules, with the canonical example being one module that writes a format and
another that reads it. That is the shape of this platform's delivery path, which is what made the
measurement above possible. The general move — *compare what the writing side and the reading side
both know* — is reusable and should be re-run when the component is designed, as the check that it
actually removed something.

### What it does not settle

**Library or service.** Nothing in Ousterhout decides it. This corrects a claim made in session on
2026-11-23, that the literature settles the question in favour of a library; it does not. Martin's
chapter 27 and Newman's chapter 1 lean against a service, and ADR-012's counter-argument — that the
measured pain came from consumers pinning versions across three separate hosts, which a service
removes and a library preserves — is real and is not answered by anything read so far.

The working view is that this question is downstream of the interface question anyway. Decide the
operations first; how chatty the component turns out to be will inform whether a process boundary is
affordable.

**Whether the remaining clusters are worth acting on now.** The vendor-vocabulary cleanup is filed as
`views-faoapi#596`/`#597` and `views-crafdapi#259`/`#260`, all four on hold behind
`views-pipeline-core` story #603, which reworks the same error classification upstream and has not
started.

### Where parts of this went

- ADR-012, *Challenges and questions* — the depth argument, the network-hop overstatement, and the
  full leakage measurement with its corrections.
- ADR-006, *Challenges and questions* and *Relationship to the literature* — the anticipated class
  list as a classitis risk, and the CIC form as a written-down informal interface.
- `views-postprocessing#341` — the "only place that knows the shape" claim not quite holding.
- `views-hydranet#674`, `#675`, `#676` — unrelated to the Appwrite effort; recorded there because the
  same reading produced them.

### A methodological lesson, recorded because it cost the most

Three replies of architectural reasoning on 2026-11-23 rested on a premise nobody had checked: that
the serving APIs read the producer's shared bucket. They do not; each reads its own. The error came
from reading a **default value in a config class** — `bucket_id: str = "production_forecasts"` — that
production never uses, because the environment overrides it.

A default in source is not evidence of runtime behaviour. The rule adopted for the rest of this
effort: verify in code and configuration, state which claims were checked and which were read, and
treat anything from another session or another repository's documents as a lead rather than a
finding. Filed as `views-faoapi#593` and `views-crafdapi#253`.

---

## 2. Martin, *Clean Architecture* — in progress

Chapters 17 (Boundaries: Drawing Lines), 24 (Partial Boundaries), 27 (Services: Great and Small),
30 (The Database Is a Detail).

*Not yet written. Things to watch for while reading, so they are not missed:*

- The FitNesse case in ch. 17 — eighteen months with no database behind one interface, then MySQL in
  a day — is the direct analogue of moving the prediction store off Appwrite to Hetzner. ADR-012
  deliberately leaves that store alone; ch. 17 is the argument for why that is right.
- Ch. 24 prices what ch. 17 recommends. Read as a pair, or ch. 17 alone will argue for more
  boundaries than are affordable. Its *skip the last step* option — full component design, deployed
  together — is directly relevant to the library-or-service question.
- Ch. 27's claim that *"architectural boundaries do not fall between services"* is the strongest
  argument against the gateway-as-service form and should be engaged with rather than quoted past.

---

## 3. Hohpe & Woolf, *Enterprise Integration Patterns* — not yet read in full

Chapters 2 (Integration Styles), 10 (Messaging Endpoints).

*Not yet written.* Preliminary note from the extracted claims, to be checked against the chapters:
their **Messaging Gateway** is a thin layer inside each application, not a separate process, and its
two stated benefits — testable with a stub, vendor replaceable without touching application code —
are the two reasons this effort exists. Their four integration styles place this platform's delivery
path closer to *file transfer* than to *shared database*, which matters because file transfer is the
most decoupled of the four and its named cost is staleness, not coupling.

---

## 4. Newman, *Building Microservices* — not yet read in full

Chapters 1 (What Are Microservices?), 4 (Communication Styles), 12 (Resiliency).

*Not yet written.* ADR-012 already cites chapters 4, 5 and 12 and quotes p. 42 in support of a
service. That quotation should be read in context before the ADR is advanced.

---

## 5. Freeman & Pryce, *Growing Object-Oriented Software* — not yet read

Chapter 8 (Building on Third-Party Code), four pages.

*Not yet written.* Expected to bear directly on the vendor-vocabulary cluster: a thin adapter layer
expressed in the application's own terms, tested against the real third-party API, with the rule
*do not mock types you cannot change*.

---

## The governance works in one direction only

**Recorded 2026-11-25**, from a multi-expert review of the two partner services
(`reports/2026-11-25_faoapi_crafdapi_review.md`). This is a lesson about our own documents rather
than about a book, which is why it sits outside the per-source sections.

**What was measured.** `views-faoapi` has 122 open issues and `views-crafdapi` has 72. Reading all 122
titles, **not one proposes removing a capability.** Every issue is a correct response to a real
finding and every one adds something — a guard, a proof, a runbook, a test, an ADR.

**Why that is our doing, not theirs.** Our obligations are all additive. ADR-005 requires tests.
ADR-006 requires intent contracts. ADR-008 requires explicit failure. ADR-010 requires register
entries. Each is right on its own. Together they make adding the cheapest correct response to any
finding and deleting the most expensive, because a deletion has to argue against all of them at once.

**The consequence, in the maintainer's words on 2026-11-25:** *"every time I do, their code base just
grows and grows and grows. Nothing ever stops."* Four weeks behind schedule, with paying partners
unserved, on a codebase whose engineering standard is high throughout.

**Where this went.** ADR-004's challenges section, as the second entry of 2026-11-25, since ADR-004 is
the deferred home for rules about how the system may change. A candidate rule is recorded there and is
not a decision: *a commit that closes an issue must reduce the line count, or say in its message why it
cannot.* Also into `views-publicapi/SPECS.md` §11.6, which generalises that spec's own existing rule —
*"A fifth parameter needs a named person who wants it"* — from one parameter to everything the service
publishes.

**What it does not settle.** Whether the rule belongs in ADR-000's process rules, in a successor to
ADR-004, or in `contributor_protocols/`. And whether it should apply to tests at all, where line count
is not the cost that matters.

---

## Still open across all of it

- **Library or service.** Unresolved. See §1.
- **What operations the component offers.** The load-bearing question. Two candidate answers exist in
  the platform already.
- **Whether `views-publicapi` is the first consumer of the component or the third clone.** Asked of
  the maintainer on 2026-11-23, not yet answered.
- **The seam contract's silence on the record's shape.** It fixes the coordinates and points at no
  declaration of what sits at them. This repository's to fix.
- **views-datafactory has not been assessed.** Requested by the maintainer on 2026-11-25. It
  references Appwrite in several places, so it is in scope and has simply not been looked at. Tracked
  with a starting point in `boundary_tests.md`.
- **The prediction store's move off Appwrite to Hetzner.** Out of scope for ADR-012 by its own point
  4, and marked *not decided* on the platform target drawing. Named here so the deferral stays a
  decision rather than becoming a gap.

## Sources on disk

- Extracted reading copies, by chapter: `~/Desktop/views_blueprints/reading/`
- Full books: `~/brain/9_library/full_books/`
- Per-chapter PDFs and the claim index: `~/brain/9_library/papers/` and
  `~/brain/9_library/library_system/index.db`
- Platform drawings, as built and target: `~/Desktop/views_blueprints/`
