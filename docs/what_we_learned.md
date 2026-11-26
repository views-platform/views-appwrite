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

## 3. Hohpe & Woolf, *Enterprise Integration Patterns* — read 2026-11-25 and 2026-11-26

Chapters 2 (Integration Styles) and 10 (Messaging Endpoints), from the extracts at
`~/Desktop/views_blueprints/reading/`. Every quotation below was taken from those files during the
reading, not from memory.

### What the source says

**Ch. 2 names four integration styles** — File Transfer, Shared Database, Remote Procedure
Invocation, Messaging — ordered by increasing sophistication, *"each pattern builds on the last,
looking for a more sophisticated approach to address the shortcomings of its predecessors."* The
governing advice is per-integration, not per-platform: *"The trick is not to choose the one style to
use always, but to choose the best style for a particular integration opportunity."*

File Transfer's benefit is stated as total decoupling — *"integrators need no knowledge of the
internals of an application... The files effectively become the interface of each application"* — and
its costs are itemised as work you must do yourself: *"The applications must agree on file naming
conventions and the directories they appear in. The writer of a file must implement a strategy to keep
the filenames unique. The applications must agree on which one will delete old files... The
applications will need to implement a locking mechanism or follow a timing convention to ensure that
one application is not trying to read the file while another is still writing it."* Its named failure
is staleness: *"updates tend to occur infrequently, as a result systems can get out of
synchronization."*

**Ch. 10's Messaging Gateway** is *"a class that wraps messaging-specific method calls and exposes
domain-specific methods to the application"*, the worked contrast being a method called
`GetCreditScore` rather than one that makes the caller set `Message.MessageReadPropertyFilter.AppSpecific`.
Four of its clauses are operative for us and are quoted in full in the findings below: the
domain-vocabulary rule, the exception-translation rule, the interface/implementation split for
testing, and **Chaining Gateways** — a low layer that abstracts the vendor's syntax, wrapped by a
high layer that offers a narrow domain API.

### What it changes for us

**First, a correction to the preliminary note this section replaces.** That note said the four styles
place our delivery path *"closer to file transfer than to shared database."* **That is wrong, and the
error is the finding.** The path is **both, simultaneously, for one integration**: the Parquet file in
the bucket is File Transfer, the metadata table that indexes it is Shared Database. The vendor's file
identifier is the **join between the two styles** — it exists only because both are running. The
identity-scheme problem recorded in ADR-012 is therefore structural rather than accidental.

Worse, we pay File Transfer's whole invoice and receive none of its benefit. The four self-imposed
costs map one-to-one onto our code: unique names (outsourced to Appwrite, which is `fileId`, which is
why the vendor is expensive to leave), who deletes old files (`remove_other_deliveries`), the
write/read interlock (the manifest-last commit marker), and format agreement (the 13 metadata
fields). But the files are **not** the interface — the SDK is, at roughly 2,400 lines per consumer
repository — so consumers need deep knowledge of a vendor, which is the one thing the style exists to
prevent.

**Four places ch. 10 says plainly what we did, and what the alternative is.** These are the most
actionable sentences either chapter contains.

1. **Domain vocabulary, not vendor identifiers.** `get_file_metadata(file_id)` and
   `get_latest_file_id()` are the `MessageReadPropertyFilter` case, not the `GetCreditScore` case.
   Right: `latest_forecast(run, level, outcome)`, with no vendor handle crossing in either direction.
2. **Translate the vendor's exceptions at the boundary.** *"the Messaging Gateway has to catch any
   messaging specific exception and throw an application-specific (or a generic) exception instead.
   This code can get a little tedious, but it is very helpful if we ever have to switch the underlying
   implementations."* We hard-code `storage_file_not_found`, `storage_bucket_not_found` and
   `collection_not_found` in three repositories. The book both prescribes the fix and predicts why it
   gets skipped.
3. **Separate interface from implementation so a stub exists.** *"one 'real' implementation that
   accesses the messaging infrastructure and a 'fake' implementation for testing purposes... allows us
   to test the application without any dependency on messaging."* We have no such split, so 2,046
   lines of views-faoapi tests mock the vendor SDK instead — and did not catch views-faoapi#660.
4. **Two thin layers, not one thick class.** Chaining Gateways describes a syntax layer wrapped by a
   domain layer. `AppWriteFileManager` is 1,273 lines being both at once, plus provisioning. This is
   the same object Ousterhout §9.4 calls a special-general mixture, named independently by two books.

**It also supplies the acceptance test, which is the part worth keeping.** The chapter claims exactly
two payoffs for a gateway — a stub to test against, and a replaceable implementation. So "have we
built one?" has two pass/fail answers, and they are already written up as tests 4 and 5 in
`boundary_tests.md`: install a consumer with the SDK absent and import it; put a fake store in the
real one's place and run the suite. **Neither has been run.** Until one of them has, every claim in
this section is an argument rather than a measurement.

**What we already do correctly**, recorded so the section is not only an indictment:
`views-postprocessing/views_postprocessing/{unfao,crafd}/store_port.py` is a five-method port in
forecast terms, and the 2026-11-25 count found those five are the complete set anything calls.
`contract/store_metadata.py` says in its own docstring *"This is the only place that knows that
shape."* Both predate anyone here reading the book.

### What it does not settle

- **Whether to keep two integration styles or collapse to one.** Ch. 2 sanctions mixing — per
  opportunity. It does not say whether this opportunity justifies it. Collapsing to File Transfer
  alone requires VIEWS to issue its own names, which is ADR-012's open question and is not decided.
- **Whether a gateway should be a library or a service.** Ch. 10's Messaging Gateway is *a class
  inside the application*. ADR-012 proposes a separate process. The chapter is simply not evidence
  either way, and reading it as support for ADR-012's shape would be a misuse of it.
- **Whether the metadata table is needed at all** once a filename carries identity. Nobody has
  checked what the two partner APIs read from it beyond "which file is newest".
- **Anything about Messaging**, the fourth style. Monthly batch with three consumers does not need
  it. Worth recording as a decision rather than an omission.

### Where parts of this went

The identity-scheme consequence is ADR-012's challenge entry of 2026-11-24. The lapsed-premise
finding about `views-pipeline-core` ADR-046 is that repository's issue #627, cross-referenced from
ADR-012 and from `views-publicapi/SPECS.md` §10 item 9. The two acceptance tests are tests 4 and 5 of
`boundary_tests.md`. **Nothing from this section has graduated into a decision**, and the four
numbered findings above are the ones that should, when the gateway's shape is settled.

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

## What four books did to the question — the synthesis, and why it was late

**Written 2026-11-27**, after the maintainer pointed out that four books had been read and no
hypothesis had become more likely than any other. He was right, and the fault was in the method
rather than in the sources: each section above was written as a book was finished, and **nothing ever
asked what all of them say together.** Reading without a synthesis step produces criteria, and
criteria can only ever tell you that what you have is wanting. This section is the step that was
missing.

### The question

What should `views-appwrite` be? ADR-012 answers: a published package, installed on exactly one
machine, run there as a service, reached by everyone else over HTTP, imported by nobody. Status
Proposed.

### What the reading did to each candidate

| Candidate | Before | After | What moved it |
|---|---|---|---|
| **Remove the vendor entirely** | plausible | **ruled out** | It is the only partner authentication and the only revocation mechanism. Checked 2026-11-26. |
| **Leave it as it is** | plausible | **ruled out** | Five copies of the client; 2,046 test lines mocking a pinned SDK; one upstream rename that became a platform incident. |
| **Contracts only, no shared code** | plausible | **unlikely** | The seam contract exists and the two APIs drifted anyway. Agreement without shared code has already been tried here. |
| **A service** | the proposal | **downgraded** | Martin ch. 27; Newman ch. 4 on payload size and on interfaces that cannot change atomically. |
| **A library** | barely considered | **the leader** | Hohpe & Woolf's gateway is *a class*; Freeman & Pryce's adapter is a layer inside the application; Newman's two objections do not apply to it. |

**Three of the four sources point at a library. The ADR of record proposes a service.** That is the
plainest result of the whole exercise and it took four days to state.

### The bigger reduction: the question was malformed

Ranking the candidates matters less than this. **The vendor is doing four jobs, and "what replaces
it" has a different answer for each.**

| Job | Where the evidence points |
|---|---|
| File storage | out of the consumers entirely — the strongest conclusion available |
| The index of which file is newest | collapses into storage; a file-based index with an atomic commit marker already exists in the run manifest, and the database is a second index doing the same work |
| Partner identity | stays, for now. Nobody has proposed a replacement and this is the genuine lock-in |
| Revocation | rides on identity |

So the converged position, stated as a position and not a decision: **a small library on the write
side where the SDK is genuinely needed; readers obtaining files and importing nothing; the APIs
continuing to use the vendor to check who is calling.** Narrower than ADR-012's points 1 to 3, and
arrived at from the reading rather than from preference.

### What remains open, and it is two things rather than six

1. Whether the write-side library is worth building at all, against leaving the producer's code where
   it sits.
2. What eventually replaces the vendor as the partner identity provider. This is the real cost of
   leaving and **it is priced in no document on this platform**, ADR-012 included: external
   organisations hold the vendor's own credentials, so leaving is a re-credentialing of outside
   parties on their timetable, not a data migration.

### The methodological lesson, which is the part worth keeping

**Reading serially and reporting serially is not reading.** Four sources were summarised one at a
time, each producing a list of ways the current system falls short, and the distribution over answers
never moved because nobody computed it. The synthesis is cheap — it is the table above — and it
should be written after the second source, not the fourth. Recorded here because this document's
whole purpose is to turn reading into something usable, and for four days it was turning reading into
more reading.

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
