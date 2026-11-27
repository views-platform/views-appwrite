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

## 4. Newman, *Building Microservices*, 2nd ed. — ch. 4 read 2026-11-26; ch. 1 and ch. 3 not read

Read: **ch. 4, "Microservice Communication Styles"**, from the extract at
`~/Desktop/views_blueprints/reading/7_Newman_Ch04_communication_styles.pdf`. **Not read:** ch. 1
(the extract exists on disk and has not been opened) and ch. 3 (incremental migration, the strangler
fig), which a peer session has since named as the method for retiring the platform in pieces. ADR-012
separately cites Newman p. 42 from an earlier session; that page is not in these extracts and the
quotation there is inherited, not re-verified.

### What the source says

Ch. 4 is about what changes when a call stops being in-process. Two passages bear directly on
ADR-012 and neither appears in it.

**Payload.** *"When making calls between microservices over a network... the data actually has to be
serialized into some form that can be transmitted over a network. The data then needs to be sent and
deserialized at the other end. We therefore may need to be more mindful about the size of payloads
being sent between processes."* His own suggested remedy is the opposite of a download route:
*"offload data to a filesystem and pass around a reference to that file location instead."*

**Changeability.** *"With communication between microservices... the microservice exposing an
interface and the consuming microservices using that interface are separately deployable
microservices. When making a backward-incompatible change to a microservice interface, we either
need to do a lockstep deployment with consumers, making sure they are updated to use the new
interface, or else find some way to phase the rollout."* In a library the same change is atomic.

He also notes that an API which makes sense in-process may not survive the move: *"I can make one
thousand calls across an API boundary in-process without concern. Do I want to make one thousand
network calls between two microservices? Perhaps not."*

### What it changes for us

**It supplies the two arguments against ADR-012's service shape that nobody had written down.** A
forecast file is hundreds of megabytes; as a library a fetch is free, as a service it is the whole
payload crossing the network. And a service interface cannot be changed atomically — which is the
wrong property to buy while nobody is yet confident the operations are the right ones.

Together with Martin ch. 27 (§2) and the two gateway sources (§3, §5), this is what produced the
synthesis below: **three of four sources point at a library and the ADR of record proposes a
service.**

### What it does not settle

Whether ADR-012's own counter-argument survives. The ADR's strongest sentence — a program in front
of a store can refuse what the store cannot — is about a capability, not about deployment, and ch. 4
does not touch it. Nor does ch. 4 say a service is wrong; it says what a service costs.

---

## 5. Freeman & Pryce, *Growing Object-Oriented Software* — ch. 8 read 2026-11-26

Read: **ch. 8, "Building on Third-Party Code"**, from the extract on disk and confirmed against the
full book at `~/dev/library/incoming/FreemanPryce2010_GOOS.pdf`, p. 70.

### What the source says

The chapter has a rule with a title — **"Only Mock Types That You Own"**, subtitled **"Don't Mock
Types You Can't Change"** — and a prescription.

*The diagnosis, which is the part that makes it an instrument rather than an opinion:* **"tests that
mock external libraries often need to be complex to get the code into the right state for the
functionality we need to exercise. The mess in such tests is telling us that the design isn't right
but, instead of fixing the problem by improving the code, we have to carry the extra complexity in
both code and test."** Separately on correctness: *"we have to be sure that the behavior we stub or
mock matches what the external library will actually do"*, and that the tests must *"remain valid
when we upgrade the libraries"*.

*The prescription, with its size constraint:* **"We write a layer of adapter objects... We keep this
layer as thin as possible, to minimize the amount of potentially brittle and hard-to-test code. We
test these adapters with focused integration tests to confirm our understanding of how the
third-party API works. There will be relatively few integration tests compared to the number of unit
tests."** The stated consequence: *"a set of interfaces that define the relationship between our
application and the rest of the world in our application's terms and discourages low-level technical
concepts from leaking into the application domain model."*

*And the paragraph that is specifically about our problem*, on third-party **value** types rather
than services: *"This pattern does not apply to value types because, of course, we don't need to
mock them. We still, however, have to make design decisions about how much to use third-party value
types in our code. They might be so fundamental that we just use them directly. Often, however, we
want to follow the same principles of isolation as for third-party services, and translate between
value types appropriate to the application domain and to the external domain."*

### What it changes for us

**It converts the test suite from a cost into evidence.** `views-faoapi` carries 29,171 test lines
against 14,855 source lines, 261 `patch`/`Mock` call sites, and 2,046 lines whose subject is a
vendor SDK pinned at an exact version — and none of it caught `views-faoapi#660`, the defect where a
partner could be served the previous month's forecast. Under this chapter that suite is not
thoroughness; it is the symptom the chapter names.

**It independently corroborates §3's finding.** Hohpe & Woolf arrive at an adapter layer from
integration patterns; Freeman & Pryce arrive at the same thing from testing practice. Two routes,
same destination, which is worth more than either alone.

**And it is the fourth independent source to point at `fileId`.** An Appwrite file id is a
third-party *value* type that this platform adopted without deciding to. Ousterhout named the
informal interface a type cannot carry; Martin named what may cross a boundary; Hohpe & Woolf named
it the join between two integration styles; Freeman & Pryce name the decision nobody made.

**It also indicts a plan of record.** `ADRs/005_testing_as_mandatory_critical_infrastructure.md`
specifies five unit test files with the SDK mocked and names two of views-faoapi's vendor-mocking
suites as drop-in replacement verifiers. That is challenged in ADR-005's own challenges section,
2026-11-25, with this chapter as the evidence.

### What it does not settle

How thin is thin. `views-faoapi/src/views_faoapi/managers/appwrite/` is 2,421 lines for an adapter
over three store operations, which is plainly not thin — but the chapter gives a direction, not a
number. And it says nothing about whether the adapter is shared across repositories or written once
per repository, which is the actual open question here.

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

## What this repository is, in a name the literature supports

**Written 2026-11-27**, because the maintainer asked a question nobody had answered: *"when people
ask what this repository is, I want to be able to say it is an X."* Every citation below was checked
against the files on disk; where a source is **not** on disk that is said plainly, because the point
of the exercise is to stop inventing names that sound like terms of art.

### The short answer

> **It is a Gateway — specifically a vendor gateway for one storage product — in the sense Fowler
> gives the term, the same family as Hohpe & Woolf's *Messaging Gateway* and Martin's *Database
> Gateway*.**
>
> Today it is not that yet. Today it is the platform's contracts home, and the gateway is an
> activated but unwritten plan.

**ADR-012 is already titled "The Appwrite Gateway".** The name was chosen before any of this reading
and it turns out to be correct. What the reading adds is the lineage and the right to cite it.

### Why "Gateway", and what can actually be quoted

**Fowler, *Patterns of Enterprise Application Architecture*, p. 466** is the general pattern. **The
book is not in the library** — checked across the whole filesystem — so its definition must not be
quoted here. Two independent attestations of the locator exist and may be cited:

- `Martin2017_CleanArch_Ch23`, footnote 2, verbatim: *"Patterns of Enterprise Application
  Architecture, Martin Fowler, et. al., Addison-Wesley, 2003, p. 466."*
- EIP's annotated bibliography: *"EAA — Martin Fowler, Patterns of Enterprise Application
  Architecture, Addison-Wesley, 2003, ISBN: 0321127420"*

**Hohpe & Woolf, EIP ch. 10** is in the library in full, and says the specialisation out loud:

> *"A Messaging Gateway is a messaging-specific version of the more general Gateway pattern [EAA]."*

and states the defining consequence — the one sentence that matches what this repository is for:

> *"only the Messaging Gateway code knows about the messaging system; the rest of the application
> code does not."*

**Martin, *Clean Architecture* ch. 23** gives the other sibling and is the closest first-party
restatement available: *"These gateways are polymorphic interfaces that contain methods for every
create, read, update, or delete operation... Those gateways are implemented by classes in the
database layer."*

So the family has at least two named members already — *Messaging* Gateway for middleware,
*Database* Gateway for persistence. A **vendor gateway** for one storage product is the same move,
and naming it after Appwrite is consistent with how the family names its members.

### What it is NOT, and why — because these were the candidates

| Candidate | In the library? | Why it does not fit |
|---|---|---|
| **Anticorruption Layer** (Evans, DDD ch. 14) | yes, full book | Evans is explicit that it is *"a means of linking two BOUNDED CONTEXTS"* and *"**not** a mechanism for sending messages to another system"*. Its trigger is a foreign **domain model**, not a foreign API. Appwrite has no conflicting model of forecasts; it has files and rows. |
| **Adapter** (GoF, p. 139) | yes, full book | *"Convert the interface of a class into another interface clients expect."* One object, wrong shape, and the target interface already exists. Too small a unit — it is a component of the thing, not the thing. |
| **Facade** (GoF, p. 185) | yes, full book | Simplifies without re-expressing. Evans: *"The FACADE does not change the model of the underlying system. It should be written strictly in accordance with the other system's model."* The whole point here is to change the vocabulary. |
| **Repository** (Evans, DDD ch. 6) | yes, full book | Scoped to persistence of aggregate roots — *"the illusion of an in-memory collection"*. Narrower than a vendor whose jobs include authentication. |
| **Ports and Adapters / Hexagonal** (Cockburn) | **no primary source** | A web page, not a book; two sources on disk disagree on its date (2005 vs 2008). It is an architecture-wide stance, not a named module. Cite it only via GOOS ch. 6 p. 48 or Newman ch. 1 fn. 2. |
| **Separated Interface** (Fowler) | **not present at all** | Zero hits across 1,188 extracted texts and every full book. Do not cite it. |

One passage links three of these, and is worth keeping — **GOOS ch. 6, p. 48**: *"these two forces
will push the structure of an application towards something like Cockburn's 'ports and adapters'
architecture... we write interfaces to describe its relationships with the outside world in its
terminology (Cockburn's ports). Then we write bridges between the application core and each
technical domain (Cockburn's adapters). **This is related to what Eric Evans calls an
'anticorruption layer'**."*

### The qualification to say out loud

A gateway in all three sources is **a class inside an application**. ADR-012 proposes a separate
program reached over HTTP. That is a deployment choice the pattern does not make, and §"What four
books did to the question" records that three of four sources point the other way. So the honest
full sentence is:

> *"It is the platform's contracts home. It is also where we have decided to put the Appwrite
> gateway — a vendor gateway in Fowler's sense — though whether that gateway is a library or a
> service is not settled, and the reading so far favours a library."*

### What this does not settle

The deployment shape, as above. And whether the gateway covers the **data path**, the **identity
path**, or both — ADR-012 does not say, and stating it is the cheapest decision available.

---

## The three copies have diverged, and merging them naively would reintroduce a bug

**Measured 2026-11-27.** Recorded here because it changes what "move the Appwrite code into one
place" means, and because it is the clearest case this platform has produced of the repository's own
design preference — *duplication is far cheaper than the wrong abstraction* — being right.

**The arithmetic.** Of the ten files in each API repo's Appwrite package: three are byte-identical or
differ only by the repo's own name; four differ only in typing style, import order, or one added
field. **The remaining three — `manager.py`, `file_cache.py`, `metadata.py` — are 2,145 of
views-faoapi's 2,421 lines and 2,042 of views-crafdapi's 2,320, and they carry real behavioural
divergence in both directions. Neither is a superset of the other.**

**Three divergences that are decisions, not drift:**

- **`download_file` holds opposed resolutions of the same incident.** views-crafdapi hard-fails when
  the byte count does not match the recorded size. views-faoapi deliberately **skips** that check for
  SDK-auto-deserialised JSON, after a production incident on 2026-08-24 in which re-serialised
  manifests (26,544 → 22,676 bytes) were wrongly rejected as truncated. **Picking either breaks the
  other.**
- **Replace-on-upload.** views-faoapi stages then swaps — upload the new, delete the old last — which
  closed a data-loss window (C-182). views-crafdapi still deletes first.
- **The timeout patch.** views-faoapi's is thread-safe by construction, lock-guarded and installed
  once per process (#616). views-crafdapi's documents in its own comment that it is *"not
  thread-safe... acceptable while the API runs single-threaded"*.

**What it means.** These are not three copies of one thing. They are three answers to three
incidents, two of which only one repository has suffered. Sandi Metz's rule, which this repository's
design preferences already adopt, is the right instrument: *similar shape is not evidence*. A merge
that picks a winner per file would import one repository's unlearned lesson into the other.

**What survives consolidation cheaply:** the six identical-or-trivial files — roughly 250 lines of
config, results, constants, auth, the provisioning gate and the SDK compatibility shim. That is the
part where every change to one genuinely demands the same change to all.

**What this does not settle.** Whether the diverged behaviours should be reconciled at all, and in
which direction. Each needs the incident behind it read before anyone chooses, and at least one of
them (`download_file`) is a correctness decision rather than a style one.

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

- **Library or service.** Unresolved, but no longer evenly balanced: three of the four sources read
  point at a library and ADR-012 proposes a service. See the synthesis section above.
- **Whether ADR-012's boundary is the data path, the identity path, or both.** It does not say.
  Checked 2026-11-26: the vendor is doing four jobs — file storage, the newest-file index, partner
  authentication and partner revocation — and only the first was ever decided, by
  `views-pipeline-core` ADR-046 in that repository.
  **Stating which one the gateway covers costs nothing and narrows every question below it.** This is
  the cheapest open decision on the list.
- **Three strategies are live and contradict each other, and nothing resolves them.** Consolidate
  (views-appwrite epic #187, activated by the operator 2026-11-17 when trigger T3 fired); evict
  Appwrite from the core (views-pipeline-core #339); or freeze this repository to the registry alone
  (views-appwrite #214, which would park the roadmap that authorises the first). Found 2026-11-27.
- **The surface is shrinking while this is undecided.** views-crafdapi #311 removes roughly 1,530
  lines of Appwrite write and provisioning code that no key can reach; views-faoapi #603 and #585
  rewrite the read and authentication paths. Consolidating now would move code that is being deleted
  or rewritten.
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
- **Corrected 2026-11-27: the `~/brain/9_library/` paths below were wrong and the directory does not
  exist.** The library is at `~/dev/library` — a git repository called *Praxis Library*, flat files
  as authority with SQLite as a derived index.
  - Full books: `~/dev/library/full_books/` — 12 PDFs, including GoF *Design Patterns*, Evans
    *Domain-Driven Design*, Martin *Clean Architecture* and *Clean Code*, Ousterhout, Nygard
    *Release It!*, Kleppmann *DDIA*.
  - Papers and chapter splits: `~/dev/library/papers/` — 1,065 PDFs, including the complete
    *Enterprise Integration Patterns* and per-chapter splits of EIP, Meszaros, Nygard and Beck.
    Extracted text alongside at `papers/_extracted_text/` (1,188 files).
  - Staging: `~/dev/library/incoming/` — 228 PDFs, including the full Freeman & Pryce *GOOS* and
    chapter splits of Fowler's *Refactoring*.
  - Index: `~/dev/library/library_system/index.db` — 1,187 papers, 5,306 claims. Note `chunks` is
    empty and `papers_fts` has no `paper_id` column; query it by `rowid`.
- **Known absent, so do not quote them from memory:** Fowler's *Patterns of Enterprise Application
  Architecture* (cite p. 466 only via *Clean Architecture* ch. 23 fn. 2), Cockburn on Hexagonal
  Architecture (a web page; cite via GOOS ch. 6 p. 48), Fowler's *Service Stub* and *Remote Facade*
  (cross-references inside EIP only), and *Separated Interface* (not present anywhere).
- Platform drawings, as built and target: `~/Desktop/views_blueprints/`
