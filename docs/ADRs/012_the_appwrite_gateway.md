# ADR-012: The shared Appwrite client is a gateway service, not a library

**Status:** Proposed
**Date:** 2026-11-21
**Decider:** Simon Polichinel von der Maase, maintainer of the VIEWS forecasting platform

*A reader new to this platform will find a short glossary at the end. Nothing before it depends on having read it.*

---

## In short

In August we deliberately made a second copy of a working program rather than invent an abstraction from a single example. That was the right call. In October the vendor renamed half its interface, and the same fix had to be written five times.

The bet has now paid out. We know what the shared piece should look like, because we have watched the same code be maintained in several places and seen exactly where it hurts.

This document decides to build that shared piece as **a small service running on one of our own machines**, rather than as a library that every repository installs. The reason is narrow and specific: the pain we are trying to escape comes from each repository holding its own pinned copy, and a library keeps that, while a service removes it.

---

## How we got here

### The clone

On 2 August 2026 a new repository was created with a single commit: *"seed: faoapi v1.4.0 snapshot (fresh history)."* The next commit renamed the package. `views-crafdapi` is `views-faoapi`, copied.

This was intentional, and it followed a good rule: duplication is cheaper than the wrong abstraction. With one partner-facing service in existence, any shared interface pulled out of it would have been generalised from a single example — and a wrong interface is far more expensive to unpick than a second copy is to maintain. So we took the second copy on purpose.

Four months later, this is what the copy looks like. The two services each carry about 2,300 lines whose only job is talking to Appwrite. The largest file is 1,195 lines in one and 1,123 in the other, and 300 lines now differ between them. The metadata file is 560 and 564 lines, with 80 differing. One file, 51 lines, is still character-for-character identical in both.

That is one program being maintained twice, drifting apart, with every fix owed to both.

The same shape shows up inside `views-postprocessing`, which serves two recipients from one codebase. Two of its files are 111 lines each and byte-identical. Two more are both exactly 435 lines and about 95% the same.

### The rename

In October the Appwrite vendor renamed its database interface. What had been collections and documents became tables and rows, with new endpoint names and a new set of permission names. A credential issued after the change is simply refused by the old endpoints.

The fix had to be applied in five places. One of them was holding up a delivery to CRAF'd.

We had agreed in advance what that would mean. The written position was that a defect requiring the same fix in several copies of the client is the signal to stop copying. On 17 November that signal fired and the maintainer agreed to start building. What nobody had decided was **what to build** — and that is the only question this document answers.

### What the rule in our own contract actually says

Our seam contract tells each partner-facing service to write its own Appwrite client. That rule is not sloppiness and it is not lightly held: it was ratified by every seat of a cross-repository deliberation, and it has an incident behind it. One repository's defect reached a third repository because they shared client code.

But read what the enforcing test says the mechanism was. Its first paragraph: *"That import edge is precisely how a two-repo defect became a three-repo defect."*

**The harm is the import, not the sharing.** When one repository installs another's code, the second repository's bug becomes the first one's bug, on the second one's schedule. A service shares no code with anyone. The repositories exchange messages over a network, exactly as they already do with Appwrite itself.

The contract also declined to settle the bigger question, and said so plainly — whether a shared *implementation* should exist was deferred behind its own trigger. It even admitted its own position was unpriced: the alternative *"has evidence against it and no pricing anywhere in the record,"* and the residual was recorded as *"unresolved, not refuted."*

The measurements above are that missing price. This document does not overrule the rule; it answers the question the rule deferred, by the route the rule laid down.

### The one argument against doing this now, which is the maintainer's own

On 2 August — the same day as the clone — the maintainer set a bar: reconsider extraction once **three** partner-facing services exist. The third, a public API, does not exist. There are two.

That bar was set for the same good reason as the clone. An interface generalised from two examples is still largely a guess, and a wrong interface hurts every consumer at once.

The answer, and it is not a complete answer, is that the signal which fired in November does not depend on counting services. The shape is no longer being inferred from how many partner-facing services there are. It is being read off five copies of one defect that has already been diagnosed and fixed once. That is observation rather than prediction.

**Someone who weighs those differently should reject this document, and this is the honest place to do it.**

### What our one real experiment actually showed

`views-datafactory` is the only place on this platform where a shared capability was put behind a server, so it is the natural evidence. It does not say what it first appears to say.

It is both things at once. It serves a 37 GB data grid over the network, *and* it publishes a client package that every model environment installs at a pinned version. So it pays for both arrangements.

The serving half worked. Nobody edits a dependency file when the grid is rebuilt.

The installed half did not. A version constraint inside that client package held another shared library frozen for ten weeks while three new major versions were published upstream. Nothing failed. Nothing was reported. During those ten weeks the forecasting path quietly used an older function for combining results — one that loses between 2.9% and 7.3% of fatality totals. The skew is still live: model environments ask for version 1.9.0 or newer of that client, while the credential-handling fixes landed in 1.13.0.

That is the whole lesson, and it is worth stating as plainly as possible: **the recurring cost is in what consumers are made to install, not in where the code runs.**

### Four facts that decide whether a service is affordable

**Our services already live on separate machines.** `views-crafdapi` runs alone on its own server; counting the data server, three Hetzner hosts are in use. So a shared library would mean a separate deployment to each host for every fix — the fan-out we are trying to escape, three times over.

**Rented machines can reach those hosts.** Setting up credentials for the data server is already a documented step when provisioning a rented GPU machine.

**Credentials that write to partner-facing stores are not allowed on rented hardware.** That is our own written ground rule. A gateway holding the Appwrite credential means no rented machine ever needs one.

**Watching a service is a solved problem here, and it was cheap.** An outside check has polled the data server every three minutes, with alerting, since 3 August. That work can be copied in an afternoon, and it closes the objection that would otherwise be decisive.

One more thing, easy to miss and important: **every call to Appwrite is already a network call** to Frankfurt that can already fail, and every caller already handles that. The usual warning about turning function calls into network calls does not apply here. The hard part is already paid for.

---

## The decision

**1. One program does all the talking to Appwrite.** A single service — the gateway — performs every contact with Appwrite on the delivery path. It runs on a Hetzner host under systemd, as our partner-facing services already do.

**2. Nobody installs it.** Consumers reach the gateway over HTTP. No repository installs it, pins a version of it, or links against it. Each repository keeps a small automated test that fails if such an import ever appears, following a pattern already in use in `views-crafdapi`.

**3. It is a published package with exactly one installer.** The code is an ordinary Python package, published to PyPI, so every release is a fixed, named, retrievable thing and a replacement host can be built without repository access. The gateway's own deployment is the only thing permitted to install it. Publishing is how we version and deploy; point 2 governs who may consume.

**4. It covers the Appwrite delivery boundary and nothing else.** In scope: the partner delivery buckets and their metadata records — listing, reading, writing, and the metadata contract. Out of scope and deliberately so: the internal prediction store and the wider data platform, whose technology and access method nobody has chosen yet; issuing and rotating credentials, which stay with the maintainer; and creating buckets, tables and indexes, which needs the highest privileges and is excluded from the first release.

**5. One consumer moves at a time, least consequential first.** `views-postprocessing`'s write path, then `views-crafdapi`, then `views-faoapi`. Each step deletes one copy of the duplicated client. No step starts until the one before it has carried a real delivery.

**6. Monitoring and a backup exist before anyone depends on it.** A check from outside the host that the gateway is answering, on the pattern already running for the data server, and a written recovery position. Without both, the gateway does not carry a partner delivery.

**7. Every step is proven with a real request, never with a code trace.** This is an existing rule of the seam contract and it matters more here, because one wrong assumption inside shared code reaches every consumer at once.

---

## Why a service rather than a library

**Because the coupling is in the store, not in the code.** Put the calling code in one package and you have moved the typing, not the agreement. Every repository would still know that a particular bucket holds a particular kind of file with particular fields. A database is built so any authorised client can read anything — that is its virtue and it is why it cannot hide anything. A program in front of it can refuse.

**Because both shapes concentrate failure, and only one of them concentrates the repair.** The best argument for the existing no-sharing rule is that shared code turns independent bugs into common ones. True of a library and a service alike. The difference is what it takes to fix: a library means a release and three separate deployments, with the copies disagreeing in the meantime; the gateway means one deployment. If correlated failure is the worry, the service is the safer of the two ways to share.

**Because the standard test picks it.** Newman, *Building Microservices*, second edition, page 42: *"If you really do need to update that code for all users at exactly the same time, then you'll actually want to look at reusing code via a dedicated microservice instead."* Three consumers of one store cannot migrate to a different storage provider gradually. The data moves once.

**Because this boundary is one we have actually seen.** Both standard treatments warn against drawing a boundary before you have observed it. We have observed this one: one writer, three readers, an agreement already at its seventeenth version. We have not observed the internal prediction store at all, which is why point 4 leaves it alone.

**Because publishing and importing are different decisions.** What has hurt us is many consumers pinning versions, not the existence of a release. A published version is a fixed artifact, which is exactly what a deployment should install. The risk that somebody later sees a package and imports it is handled by the tests in point 2, not by refusing to publish.

**Because we can afford one more service.** The expensive step is going from zero operated services to one, and we operate three.

---

## What was considered instead

**Keep writing a client per service.** This is the status quo, and it was right in August. It is rejected now on the price: roughly 2,300 lines maintained twice, already 300 lines apart in the main file after four months, with a third copy wanted. It has already produced a defect needing the same fix in five places. Worth revisiting if running the gateway turns out to be unaffordable in practice.

**A published library that everyone installs.** This is what our existing roadmap plans. Rejected: it buys the dependency-version problem that silently changed our delivered figures for ten weeks, it does so across three separate hosts, and it creates precisely the import relationship our own rule's evidence indicts. Its *design* is sound and the gateway inherits it internally.

**A gateway for writing only, with the partner-facing services still reading Appwrite directly.** Rejected: the duplication is on the reading side, so this builds a service and keeps the problem. Recorded because it is the obvious halfway house and was raised as an open question when the architecture was drawn.

**Draw the boundary at the internal prediction store instead.** Rejected for now. That store has no decided technology and no decided access method. A boundary around it today would be a guess, which is the thing August's clone correctly avoided.

---

## What this costs, and what it does not fix

**It costs an operated service.** One more program must stay running, and the maintainer is responsible for it. After the last adoption step, a broken gateway means the UN FAO is served nothing, where today that service would keep going on its own. That is the real price and it should not be minimised.

**It costs one network hop** — about a millisecond on our own network, in front of a call of tens of milliseconds to Frankfurt.

**It costs a release process** for a package with a single installer.

**And it does not fix the underlying arrangement.** Several programs still exchange work through one shared store. They remain coupled through its structure, schema changes still reach everyone, and the agreement still has to be negotiated and versioned. The gateway narrows who may touch the store and puts the agreement in one enforceable place. It does not turn this into a different kind of system.

---

## Still open

**Which host it starts on.** Proposed: the `views-faoapi` host, as the heaviest reader. Easy to move later.

**What operations it offers.** To be drafted from the existing call sites and checked against two interfaces that already exist in the right shape — `views-postprocessing`'s five-method store port, and `views-pipeline-core`'s `DatastoreModule`, 771 lines and twelve methods, every one of them expressed in terms of forecasts rather than in terms of Appwrite. **Amended 2026-11-24:** that sentence was verified and holds for the method *names*, but three of the twelve signatures pass an Appwrite-issued file id across the boundary. Deciding the operations therefore means deciding who issues identifiers, not only what the routes are called. See the challenge entry of the same date.

**How it knows who is calling.** Whether a caller presents its own credential through the gateway, or the gateway holds one on the caller's behalf. This touches the seam contract's identity model and how narrowly a partner's access can be scoped.

---

## Challenges and questions

Raised during review and kept here on purpose. **These are not decisions.** They change nothing above
them. Each entry records when it was raised, what prompted it, and what would settle it. An entry may
end in an amendment to this ADR, or in a recorded "looked at it, it is fine" — both are useful
outcomes and the second should be written down rather than left implicit.

No code exists in this repository yet. Until it does, the decisions above are cheap to change, which
makes this the right moment to collect objections rather than defend positions.

### 2026-11-24 — "What operations it offers" is the load-bearing decision, not a loose end

**Raised by:** a reading session working through Ousterhout, *A Philosophy of Software Design*, ch. 4
against this document.

**The concern.** *What operations it offers* currently sits under **Still open**, alongside which
host the service starts on. Those two are not comparable in weight.

Ousterhout §4.4 defines a module's worth as a ratio: *"The benefit provided by a module is its
functionality. The cost of a module (in terms of system complexity) is its interface."* A module that
hides a great deal behind a narrow interface is **deep** and earns its place. One whose interface is
nearly as complicated as what it hides is **shallow**: *"Shallow modules don't help much in the battle
against complexity, because the benefit they provide ... is negated by the cost of learning and using
their interfaces."*

Applied here: if the gateway's routes end up mirroring the Appwrite SDK one for one, it is shallow. It
would add a network hop, a host that can fail and a release process, while hiding nothing — and the
duplication this document exists to remove would reappear, with every caller still knowing the
vendor's shape, through a different door. Martin, *Clean Architecture*, ch. 27 says the same of
services specifically: services that merely separate application behaviours are *"little more than
expensive function calls, and are not necessarily architecturally significant."*

Every benefit this document claims therefore rests on an answer it does not give.

**What is already right, and should be promoted rather than invented.** The *Still open* entry points
at `views-postprocessing`'s five-method store port and `views-pipeline-core`'s `DatastoreModule`, and
observes that both are *"expressed in terms of forecasts rather than in terms of Appwrite."* That is
the correct criterion, stated in passing. Ousterhout §4.3 gives the reason: an abstraction *"is a
simplified view of an entity, which omits unimportant details"*, and the vendor's vocabulary is
precisely what is unimportant to a caller who wants a forecast.

**What would settle it.** Move the question out of *Still open* and into *The decision*, as a
principle even if the route list is not yet drafted: the gateway's interface is expressed in forecasts
and deliveries, never in buckets, files, collections or rows. The depth claim then becomes testable —
count the operations the gateway offers against the number of distinct Appwrite calls they subsume.

### 2026-11-24 — The network-hop sentence overstates its case

**Raised by:** the same session.

**The concern.** Under *Four facts that decide whether a service is affordable*, this document says:
*"every call to Appwrite is already a network call to Frankfurt that can already fail, and every
caller already handles that. The usual warning about turning function calls into network calls does
not apply here."*

Half of that holds. The *category* of failure does already exist, and callers already handle it. But
the *count* changes: a read becomes API → gateway → Appwrite, two hops where there was one, plus one
additional machine whose failure stops the delivery. The usual warning is weakened here, not removed.

This document is honest about the same fact elsewhere — *"a broken gateway means the UN FAO is served
nothing"* — so the overstatement is local to that one sentence.

**What would settle it.** Narrow the sentence to the claim that actually holds, and let the cost
section carry the remainder.

### 2026-11-24 — Measured: the vendor's vocabulary and the record's shape are known in three repositories

**Raised by:** the same reading session, after Ousterhout ch. 5 ("Information Hiding (and
Leakage)"). This entry is evidence for point 4 of the decision rather than an objection to it.

**The test applied.** §5.2 defines information leakage as the same design decision being reflected
in several modules, and gives as its example one class that writes a file format and another that
reads it: *"Even if neither class exposes that information in its interface, they both depend on the
file format: if the format changes, both classes will need to be modified. Back-door leakage like
this is more pernicious than leakage through an interface, because it isn't obvious."*

That is the shape of this platform's delivery path, so it was measured. Every identifier-like string
literal in the Appwrite-facing and delivery code of the writing side (`views-pipeline-core`,
`views-postprocessing`) was compared with the same on the reading side (`views-faoapi`,
`views-crafdapi`). 73 appear on both sides. Most are coincidence — `data`, `name`, `type`. Two
clusters are not.

**Cluster 1 — Appwrite's error vocabulary, hard-coded in three repositories.** Verified by reading
the lines on 2026-11-24:

- `views-pipeline-core/views_pipeline_core/modules/appwrite/file.py:134-135` —
  `APPWRITE_FILE_NOT_FOUND = "storage_file_not_found"`,
  `APPWRITE_BUCKET_NOT_FOUND = "storage_bucket_not_found"`
- `views-faoapi/src/views_faoapi/managers/appwrite/manager.py:407,415` — the same two strings, as
  inline literals
- `views-faoapi/src/views_faoapi/managers/prediction/manager.py:74` and
  `views-pipeline-core/views_pipeline_core/modules/datastore/datastore.py:413` — both compare
  `code == "storage_bucket_not_found"`
- `collection_not_found` appears in the retry logic of both repositories

These are the vendor's words. A rename reaches every repository holding them — which is the October
TablesDB rename, the event this ADR was written about, in miniature and waiting to recur. Note that
`views-pipeline-core` already does this correctly in one place, naming the codes as constants in a
single module; the two APIs re-encode them as literals.

**Cluster 2 — the metadata record's field names, known by writer and reader alike.** *Corrected
2026-11-24 after the views-pipeline-core session answered, and after reading the lines it named.*
This cluster is smaller than first reported, and the correction matters because it changes what is
missing.

`views-pipeline-core` **does** declare its half, in code and under a governing contract:
`views_pipeline_core/modules/appwrite/provisioning.py:108` declares `FIXED_METADATA_ATTRIBUTES`
(`fileId`, `bucketId`, `filename`, `file_size`, `mime_type`, `uploaded_at`, `file_hash`, with types
and sizes) and `:135` declares `DELIVERY_METADATA_ATTRIBUTES` (`loa`, `name`, `type`, `targets`,
`category`, `description`). Together, 13 fields. The governing document is
`views-pipeline-core/documentation/CICs/AppwriteProvisioner.md:46`: *"The declared schema covers the
whole delivery document."*

Two corrections to the first version of this entry: the stored names are `fileId` and `bucketId` in
camel case, not `file_id`; and `file_bytes` is a function parameter, not a stored field.

**Corrected again, 2026-11-24, after reading `views-postprocessing` directly.** `run_id`,
`sidecar`, `expected_cell_count` and `pgm` do **not** reach the metadata document. They belong to the
wire contract and the run manifest — `contract/wire/run_manifest.py:51-56`,
`contract/track_a_source.py:58,140`. The fields `views-postprocessing` actually sends to the store
are `name`, `loa`, `category`, `targets`, `type` and `description`, all six declared in
`provisioning.py:135`. The worry recorded in the first version of this entry was unfounded and is
withdrawn.

`views-postprocessing` also turns out to handle this better than either API: `contract/store_metadata.py`
is explicitly designed as the single place that knows the document's shape, and its docstring says so
— *"This is the only place that knows that shape."* That is precisely §5.2's prescribed remedy,
applied deliberately and before anyone read the book.

**What is actually left.** Two things, both smaller than first claimed. The store document's field
names are known in three places inside `views-postprocessing`, not one — `store_metadata.py:29`,
`store_port.py:76` in both partner packages, and `delivery/findability.py:254` — so the docstring's
promise is wider than what holds. That is filed as `views-postprocessing#341`. And no single document
covers the whole record: pipeline-core's declaration covers the 13 fields it writes, and the seam
contract points at none of it.

So the accurate statement is narrower than "the record's shape is leaked": **the record is declared,
in code, in the repository that writes it; what is missing is the contract's cross-reference to that
declaration.** Cluster 1 — the vendor's error vocabulary — remains the real leak.

**The gap this exposes in our own instrument.** The Appwrite Seam Contract was searched for any of
these field names or error codes on 2026-11-24: **zero matches.** The contract and the coordinate
registry centralise the *coordinates* — which bucket, which collection, which environment variable
carries which value. They say nothing about the shape of the record stored at those coordinates, nor
about the vendor's error taxonomy. The instrument exists and its scope stops one level short of the
leakage.

**Why this supports point 4 rather than challenging it.** Point 4 puts "the partner delivery buckets
and their metadata records — listing, reading, writing, and the metadata contract" inside the
gateway's scope. The measurement says what that sentence is worth: these are the two pieces of
knowledge currently duplicated, and they are what a gateway would actually remove from its consumers.
It also sharpens the depth test in the entry above — a gateway that passes Appwrite's error codes
through unchanged would leave cluster 1 exactly where it is.

**What would settle it.** Three steps, filed as issues in the repositories that own the code, since
this repository cannot edit them:

1. Point the seam contract at `views-pipeline-core`'s declaration for the 13 fields it covers, and
   establish what happens to `views-postprocessing`'s fields — whether they are declared anywhere,
   and if not, whether they are written by inference. The first is a cross-reference; the second is
   an open question that must be answered before it can be written down.
2. Translate the vendor's error codes once, at the boundary, into our own vocabulary — the
   anticorruption layer of Evans, the adapter layer of Freeman & Pryce ch. 8. `pipeline-core`'s
   `file.py` constants are the pattern; the APIs should copy it rather than re-encode.
3. Guard it with a test that fails if a vendor error string appears outside the one module permitted
   to know it, on the pattern of the import-contract tests this platform already uses and which
   point 2 of this decision proposes for the gateway.

**Sequencing, added 2026-11-24.** Steps 2 and 3 are filed as `views-faoapi#596`/`#597` and
`views-crafdapi#259`/`#260`, and all four are **on hold**. The views-pipeline-core session reports
that story #603 of its TablesDB epic adds a single classifier for Appwrite database errors, keyed on
HTTP status first and the vendor's type string second, replacing the message-text match at
`provisioning.py:568` and closing register entry C-235. The APIs should copy that shape after it
exists rather than invent one first. #603 has not started and waits on a priority call from the
maintainer, so the four issues have no scheduled unblock date. (Relayed from that session; this
session did not verify the issue numbers in GitHub.)

Step 1 is this repository's to perform and has not been done.

### 2026-11-24 — Measured: the abstraction hides the vendor's nouns and hands out the vendor's identifiers

**Raised by:** the same reading session, working through Martin, *Clean Architecture*, ch. 17 — Figure
17.2, "The boundary line" — against this platform's code on 2026-11-24.

**The first measurement was wrong, and the correction is the finding.** The session counted the word
"bucket" outside each repository's Appwrite module: 92 lines in views-faoapi, 40 in views-crafdapi,
32 in views-pipeline-core, and 38 in views-postprocessing, which has no Appwrite module at all — 202
lines across 24 files in four repositories. On that count
`views-pipeline-core/views_pipeline_core/modules/datastore/datastore.py` looked like the worst case
at 26 hits, and the session concluded the abstraction was written in the vendor's language.

Reading the file disproved it. `DatastoreModule` is 771 lines with twelve public methods —
`upload_predictions`, `upload_data`, `get_predictions_by_metadata`, `download_prediction`,
`get_latest_file_id`, `download_latest_file`, `get_file_metadata`, `update_prediction_metadata`,
`delete_prediction`, `list_all_predictions`, `list_all_predictions_unfiltered`, `to_dict`. The verbs
are forecast nouns. **No public signature takes a bucket**; every bucket reference in the file is a
docstring, a comment, or `self.__appwrite_file_manager_config.bucket_id`, which is private.
**This ADR's existing claim under "Still open" — that the twelve methods are expressed in terms of
forecasts rather than in terms of Appwrite — is correct, and counting words was the wrong
instrument.** Recorded here because a measurement that nearly produced a false entry in this document
is worth more than one that merely confirmed something.

**What is true instead is narrower and worse.** Three of the twelve signatures pass a vendor-issued
identifier across the boundary:

```
def get_latest_file_id(self, filters) -> Optional[str]
def get_file_metadata(self, file_id: str) -> OperationResult
def delete_prediction(self, file_id: str) -> OperationResult
```

and `views_pipeline_core/modules/appwrite/file.py:308` documents what that string is, in our own
words: *"fileId: Appwrite storage file ID."* The abstraction hides where the file sits. It does not
hide the vendor's name for the file. And the identifier does not stay inside the caller — `fileId`
is a **required** attribute of `FIXED_METADATA_ATTRIBUTES` in
`views_pipeline_core/modules/appwrite/provisioning.py`, so it is written into the metadata record
that travels between repositories.

**Why this is load-bearing for this ADR.** The decision above moves the client behind an HTTP
boundary. That move does nothing about this. A gateway route called `GET /predictions/latest` that
returns an Appwrite file id has the same defect as a method called `get_latest_file_id` that returns
one — the day the vendor is replaced, there is nothing for it to return, and every stored, logged or
recorded identifier is a dead reference. **The duplication this ADR was written to remove is the
symptom; the identity scheme is the thing that makes the vendor expensive to leave.**

**The literature.** Ousterhout §4.3 names this a **false abstraction** — one that omits a detail the
caller genuinely needs, so that it "might appear simple, but in reality it isn't." `download_prediction`
reads as vendor-neutral and is not, because of what the caller must hold to call it. Martin's Figure
17.2 puts `DatabaseInterface` above the boundary and `Database Access` below it; the arrangement only
works if what crosses the line is expressed in the business's terms. A vendor-issued identifier
crossing the line defeats the figure regardless of how the methods are named.

**Amended 2026-11-25 — the leak cannot be found by any structural check.** The line `file_id: str`
names no vendor. Nothing imports Appwrite in order to read it, a search of the four repositories for
the vendor's name does not return it, and a type checker accepts any string that is handed to it. The
dependency is nevertheless real: only Appwrite can produce a value that call will accept. It travels
as a primitive type, so it is invisible to the import graph, to a text search, and to the type system
alike. The knowledge that makes it a dependency lives in a parameter name and in one docstring,
`views_pipeline_core/modules/appwrite/file.py:308`, in a different repository from most of its
callers.

Ousterhout §4.2 describes exactly this, and the sentence that matters is the one about enforcement:
the informal parts of an interface *"are not specified in a way that can be understood or enforced by
the programming language"*, and *"if a developer needs to know a particular piece of information in
order to use a module, then that information is part of the module's interface."* Read together with
§4.3, a vendor identifier passed as `str` is a false abstraction whose falseness no tool can report.

**The practical consequence for this ADR.** Whether the gateway has actually moved this dependency
cannot be demonstrated by a test, a linter, an import-contract check or a grep. It can be
demonstrated only by asking, of every identifier that crosses the boundary, who issued it and whether
anything other than the vendor could have issued it. Any acceptance criterion written for this ADR
has to be a question put to a reader, not a check run in CI. The question, and the other tests this
boundary can be put to, are catalogued in `docs/boundary_tests.md`.

**What would settle it.** Decide who issues the identifier that callers hold. If VIEWS issues it — a
run name, a level, an outcome, a content hash — then the vendor's id stays inside the adapter and
replacement is a rewrite of one component. If the vendor issues it, replacement reaches every holder
of a stored id, and the gateway's value is reduced to removing duplicated lines.

**What this does not settle.** Whether the existing `fileId` values must be migrated, what a
VIEWS-issued identifier would look like, or whether this changes the seam contract. None of that is
decided here, and this entry is not a proposal.

**Filed as investigative placeholders on 2026-11-24**, so the question survives this session without
constraining the design: views-pipeline-core#619 (where the scheme is defined),
views-faoapi#615, views-crafdapi#261, views-postprocessing#343. All four are explicitly not work
items and nothing is blocked on them.

### 2026-11-24 — This review has read ch. 4 only

**Raised by:** the same session, about itself.

The entries above come from chapters 4 and 5 of one book, read on 2026-11-23 and 2026-11-24. The same reading list
holds Hohpe & Woolf ch. 2 and 10, Newman ch. 1 and 4, Freeman & Pryce ch. 8, and Martin ch. 17, 24,
27 and 30. **Updated 2026-11-24:** Martin ch. 17 and Hohpe & Woolf ch. 10 have since been read
against this document and produced the two entries above them; the remainder have not. Expect further entries, and do not
read the current list as the complete set of objections.

---

## Consequences for existing documents

This supersedes the plan in `docs/roadmap_shared_client.md` for a published library adopted by four repositories in sequence. The first step of that plan — migrating `views-pipeline-core` to the renamed Appwrite interface, in its own repository — is untouched and is still the correct first action.

It answers the deferred cross-repository question of whether a shared implementation should exist: yes, in the form that creates no import relationship.

It requires a later amendment to the seam contract so that section 5.8 matches points 1 to 3. **That is a separate act with its own version number and its own decision about whether it obliges anyone to do anything, and this document does not perform it.** Until it lands, section 5.8 stands exactly as written and no other repository is obliged to anything.

---

## Glossary, for a reader new to this platform

**VIEWS** produces monthly forecasts of armed conflict. The work is split across separate repositories, each a Python project with its own release cycle: `views-models` holds every model's settings and starts each run; `views-pipeline-core` is the shared machinery that fetches data, trains, forecasts and writes results; `views-postprocessing` turns a finished run into the product each recipient gets; `views-faoapi` and `views-crafdapi` are web services that hand data to the UN Food and Agriculture Organization and to the CRAF'd partner consortium; `views-datafactory` builds and serves the input data; and `views-appwrite` — this repository — holds the written agreements about the shared store and ships no code today.

**Appwrite** is a commercial hosted backend running in Frankfurt, rented by this project. It provides file storage, in folders it calls *buckets*, and a database of records. We use it as the place finished forecasts are put so the partner-facing services can fetch them. Appwrite publishes a Python client library, the SDK.

**Three kinds of document live in this repository**, and the difference matters because two of them are cited above:

- *Architecture decision records*, numbered ADR-000 upward, in `docs/ADRs/`. Decisions about this repository itself. This document is one.
- *The Appwrite Seam Contract*, at `docs/ADRs/platform/appwrite_seam_contract.md`. A cross-repository agreement stating the rules any program must follow to connect to the shared store. Six repositories reference it, each pinned to a released version.
- *The coordinate registry*, at `docs/ADRs/platform/coordinate_registry.toml`. Not prose — a data file listing the agreed names: which bucket holds what, which table holds which metadata, which environment variable carries which value. Secrets appear as named empty slots, never as values.

The contract states the rules, the registry lists the values, and the two are released together under one version number. **A known defect:** both cross-repository documents sit inside the `docs/ADRs/` folder, which is for a different kind of document with a different audience. ADR-011 drew that distinction and fixed the naming; the location was never corrected, and it is the likeliest reason a reader will not realise these are not ADRs.

**Some rules cited above were agreed through a formal written procedure** for decisions spanning several repositories. It produces a dated record: the case for and against from each affected repository's point of view, the disagreements left unresolved, an adversarial review written against the draft, and the final decision. Those records are cited only as pointers for maintainers; everything needed to understand or challenge this document is restated in it.

---

## Sources

**Measurements** in this document were taken from the code or from a repository's own records on 21 November 2026 and can be re-checked at: `views-crafdapi` first commit and `deployment/RELEASE_RUNBOOK.md:3`; `views-faoapi/src/views_faoapi/managers/appwrite/` against `views-crafdapi/src/views_crafdapi/managers/appwrite/`; `views-postprocessing/views_postprocessing/{unfao,crafd}/`; `views-models/docs/runpod_run_guide.md:58-76` and `:211`; `views-datafactory/reports/technical_risk_register.md:173` and `docs/ADRs/051_external_monitoring_split.md:100`; `views-pipeline-core/views_pipeline_core/modules/datastore/datastore.py`.

**In this repository:** `docs/roadmap_shared_client.md`, decision log entries 10 to 12 and the superseded plan in section 7; `docs/ADRs/platform/appwrite_seam_contract.md`, sections 5.5, 5.8, 8 and 10; `docs/ADRs/011_naming_of_cross_repo_contracts.md`.

**Published work:** Hohpe, G. and Woolf, B. (2003), *Enterprise Integration Patterns*, Addison-Wesley, chapters 2, 8 and 11. Newman, S. (2021), *Building Microservices*, second edition, O'Reilly, chapters 4, 5 and 12. Ousterhout, J. (2018), *A Philosophy of Software Design*, first edition, Yaknyam Press, ch. 4. Martin, R. C. (2017), *Clean Architecture: A Craftsman's Guide to Software Structure and Design*, Pearson, chapters 17, 24, 27 and 30. Helland, P. (2005), "Data on the Outside versus Data on the Inside", CIDR. Helland, P. (2016), "Immutability Changes Everything", *Communications of the ACM* 59(1).

**Related work in other repositories:** `views-datafactory` issues 601 and 619 to 622 record the decisions this evidence raises for that repository.
