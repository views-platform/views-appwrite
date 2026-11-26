# The forecast store, as five operations — a proposal

**Status: a proposal, not a decision.** Nothing here is ratified and nothing depends on it. It exists
so there is something concrete to disagree with. Written 2026-11-26.

**Who it is for.** Someone who wants to know what "the middle program" actually is, in enough detail
to point at a line and say *that is wrong* or *I don't understand that one*.

---

## The one idea

Today five programs each know how to talk to Appwrite. This replaces that with **one list of five
things a forecast store can do**, written in forecast words, and **one piece of code that knows
Appwrite**.

Everything else asks for a forecast. Nothing else knows where forecasts live.

---

## The value that travels: what a forecast is called

Everything below depends on this one definition, so it comes first.

```
ForecastRef
    run       "chrome_box_forecasting_20261112_210150"
    level     "pgm" | "cm"
    outcome   "sb_fatalities"
    kind      "manifest" | "shard" | "sidecar" | "table"
```

**Four facts VIEWS already knows and already issues.** The run name above is real — it is the CRAF'd
run now waiting to be delivered. VIEWS made that name. Appwrite had no part in it.

**This is the whole proposal in one line:** a forecast is identified by what it *is*, not by where it
was put. Nothing below ever takes or returns a storage identifier.

---

## The five operations

```
publish(ref, body, description)    -> ForecastRef
latest(level, outcome, kind)       -> ForecastRef | None
fetch(ref)                         -> bytes
describe(ref)                      -> Description
find(level=None, outcome=None, kind=None) -> list[ForecastRef]
```

**Why five and not twelve.** This is measured, not chosen. Of the eleven operations the current
shared client offers, **five are called from production code anywhere in the platform** (checked
2026-11-25 across fifteen repositories). The other six are called only by tests and one audit tool.
Separately, `views-postprocessing` already declares a five-method port, and it is the same five.

Taken one at a time:

**`publish(ref, body, description) -> ForecastRef`**
The producer writes a forecast. `body` is bytes or a path. `description` carries the things a human
or a service needs later: the targets, the category, the level of analysis, a human name, free text.
Returns the ref it stored under — the same one it was given, so a caller never learns a new
identifier. Used by `views-postprocessing` and `views-pipeline-core`.

**`latest(level, outcome, kind) -> ForecastRef | None`**
*Which is the newest published forecast of this description?* Returns a ref or nothing. **This is the
operation that decides whether the whole design works**, because today's equivalent returns an
Appwrite file id. Used by both partner APIs and by `views-postprocessing`.

**`fetch(ref) -> bytes`**
Give me that forecast's contents. The adapter resolves the ref to wherever the bytes actually are;
the caller never sees how. Used by both partner APIs.

**`describe(ref) -> Description`**
The metadata record for that forecast — same shape `publish` accepted.

**Corrected 2026-11-26, and this changes the proposal.** The first draft said this is used by
`views-postprocessing` only. **Wrong.** Counting what the two partner APIs actually read out of a
metadata record — **Fact, measured 2026-11-26** — gives `fileId` (10 reads), `source_kind` (7),
`file_id` (7), `provenance` (5), `sla_days` (4), `filename` (3), `created_at` (3), `age_days` (3),
`targets` (1). So the APIs do not use the record merely to find the newest file: they read
provenance, freshness and naming out of it **and serve some of it to partners**. `latest` returning
a bare ref is therefore not sufficient for them, and either `latest` returns a ref plus its
description, or every caller follows `latest` with `describe`. **Unresolved. It is the first thing
to settle, because it decides the shape of the two most-used operations.**

**`find(...) -> list[ForecastRef]`**
Everything matching, newest first. `latest` is `find(...)[0]` and exists separately because it is the
common case and should be the simplest call. Used by both partner APIs and `views-postprocessing`.

---

## The errors, in our words

```
ForecastNotFound     nothing matches that ref or that description
StoreUnavailable     the store could not be asked — network, credentials, outage
ForecastRejected     publish refused it: a field missing, a container absent
```

**Three, and no more.** Today `storage_file_not_found`, `storage_bucket_not_found` and
`collection_not_found` — Appwrite's own words — are written as literals in three repositories. Under
this proposal the adapter catches Appwrite's exceptions and raises one of the three above. No other
program ever contains an Appwrite word.

**`ForecastNotFound` and `StoreUnavailable` must stay distinguishable.** "There is nothing" and "I
could not ask" are different facts and a caller acts differently on each. `views-crafdapi` already
learned this the hard way and fixed it (its C-233); the fix must survive into whatever replaces it.

---

## What this does **not** include, deliberately

- **Creating buckets, tables or columns.** Provisioning is a separate, higher-privilege act. Keeping
  it out is what lets the serving credential stay read-only.
- **Deleting.** No production code path calls delete today. If something needs it, it arrives with a
  named caller.
- **Anything about quarantine, approval allowlists or cache policy.** Those are decisions about
  *which* forecast to serve. They belong above this line, in the service that serves.
- **Any mention of buckets, collections, tables, rows, documents, projects or file ids.** If one of
  those words appears in this interface, the proposal has failed.

---

## What this is, in the vocabulary of the books

Stated once, so the terms are anchored to something concrete rather than floating.

- **The five operations are the interface. VIEWS owns them.** The Appwrite code is the
  implementation and sits underneath. That is Martin's Figure 17.2 and it is the whole of
  "dependency inversion": the caller writes the contract, the vendor's code conforms to it.
- **It is deep, if it stays at five.** A small opening hiding roughly 2,400 lines of vendor handling,
  times the five repositories that no longer need their own copy.
- **It is Hohpe & Woolf's Messaging Gateway**, which is explicitly *"a class that wraps
  messaging-specific method calls and exposes domain-specific methods."* `latest(level, outcome,
  kind)` is their `GetCreditScore`. `get_latest_file_id()` is the thing they contrast it against.
- **It is Freeman & Pryce's adapter layer**, and `ForecastRef` is their instruction about third-party
  *value* types: translate at the boundary rather than adopting the vendor's.
- **It does not change the integration style.** Underneath it is still a file plus an index. This
  hides that; it does not transform it. Worth being clear-eyed about.

---

## Why this defers the library-versus-service question instead of answering it

**The five operations are identical either way.** As a library, a caller imports them. As a service,
a caller makes five HTTP requests that carry the same arguments and return the same things.

So that decision — which ADR-012 currently answers "service", at status Proposed, against an
objection raised 2026-11-25 and not yet answered — **can be made later, and made cheaply, provided
the interface is settled first.**

**Two arguments against the service shape that are not recorded anywhere, from Newman ch. 4.**
ADR-012 cites Newman p. 42 in favour of a service; ch. 4 supplies the other side and nobody has
weighed it.

*First, `fetch` is what makes a service expensive.* Newman notes that across a network *"the data
actually has to be serialized... we may need to be more mindful about the size of payloads"*, and
suggests the opposite of what a `fetch` route does — *"offload data to a filesystem and pass around a
reference to that file location instead."* A forecast file is hundreds of megabytes. As a library,
`fetch` is cheap. As a service, it is the whole payload crossing the network twice.

*Second, a service makes this interface harder to change, not easier.* *"With communication between
microservices... when making a backward-incompatible change to a microservice interface, we either
need to do a lockstep deployment with consumers... or else find some way to phase the rollout."* In a
library, the five operations change atomically. In a service they cannot. Since nobody is yet
confident these five operations are the right five, **choosing the shape that is hardest to change
is the wrong order of decisions.** Settling the interface first is the thing that makes the deployment
question small. Doing it the other way round is what produced the current situation.

---

## The four questions this proposal cannot answer, and what would answer them

**1. Is `run` enough to identify a forecast, or is something missing from `ForecastRef`?**
*What would answer it:* list what each of the five call sites passes today, and check that a run,
level, outcome and kind distinguish every case. Half a day of reading.

**2. Is the metadata table needed at all once a ref carries identity?**
Only `describe` touches it, and only `views-postprocessing` calls `describe`. If the partner APIs read
nothing from it beyond "which is newest", `latest` replaces it entirely.
*What would answer it:* read what the two APIs actually use from the record. Half a day.

**3. Does `publish` belong in the same interface as the four read operations?**
One writer, three readers. A read-only consumer that cannot publish is a safer thing to deploy and a
smaller thing to credential.
*What would answer it:* a decision, not a measurement. The split costs nothing now and is awkward
later.

**4. Would this actually work?**
*What would answer it:* the two tests already written up in `boundary_tests.md` and never run —
install a consumer with the Appwrite SDK absent and import it; put a fake store behind these five
operations and run the existing suite. About a day for both, and they convert every claim in this
document from argument into measurement.

---

## The half-day check, run 2026-11-26 — and it found a flaw in this proposal

**The proposal above analysed the store as two things. It is being used as four.** All four facts
below were checked in the code on 2026-11-26.

**Job 1 — file storage.** Analysed. **Job 2 — the index.** Analysed.

**Job 3 — the identity provider, which this proposal missed.** `views-faoapi/src/views_faoapi/managers/api.py:408`
`_validate_api_key` answers *"is this caller allowed?"* by making a live call to the store with the
caller's own credential: `manager.list_files(bucket_id, limit=1)`. `views-crafdapi` does the same at
`managers/api.py:486` with `list_buckets(limit=1)`. **There is no local list of callers and no other
authentication anywhere.** A caller is someone whose store credential works.

**Job 4 — the revocation mechanism, also missed.** views-faoapi#588 keeps that probe deliberately
and states why: *"If the service reads under its own credential and never re-checks the caller's
key, a revoked key keeps being served indefinitely. The caller key must still be probed."*
views-crafdapi's ADR-044 §2 (that repo) is quoted there as the pattern: *"keys only decide who gets in: checked with
the store and remembered for one minute, so a deleted key stops working within a minute."*

**What this does to the proposal.** "Make it unnecessary" addressed the data path and silently
assumed the rest. Removing the store from the read path would leave the platform with no way to
authenticate a caller and no way to cut one off. That is two capabilities that would have to be
built from nothing. **The recommendation to collapse to File Transfer is not supportable as stated,
and the five operations above do not cover authentication at all.**

**What survives.** Taking the vendor out of the *data* path is still worth doing and still removes
most of the code. It is a narrower claim than "make it unnecessary": the vendor would be retained as
the identity provider while ceasing to be the delivery mechanism.

**The cost nobody has written down.** External callers hold **the vendor's own** credentials, issued
from its console. So leaving the vendor is not a migration of data — it is a re-credentialing of
outside organisations, on their clock, coordinated. That is the most expensive form of lock-in this
platform has, and it appears in no cost list, including ADR-012's.

**One finding that cuts the other way.** `views-faoapi/docs/ADRs/active/027_authentication_and_per_key_isolation.md:138-141`
carries a correction dated 2026-11-11 to two sentences that *"were false when written and stayed
false for 138 days"*: **"Appwrite API-key scopes are granted per resource type and are project-wide;
a key carrying `files.read` reads *every bucket in the project*, and keys bypass per-bucket
permissions entirely. There is no such thing as a single-bucket key."** So a caller credential
authenticates and does not isolate. þing-04 D1 answers this by making the *project* the unit of
isolation, which is why the second partner was given one of its own.

---

## What would make this proposal wrong

Recorded now, so it can be checked rather than defended.

- **One such caller already exists, and it is the operator.** **Fact, checked 2026-11-26.** Both
  partner APIs read an environment variable — `APPWRITE_UNFAO_QUARANTINED_FILE_IDS` and its CRAF'd
  twin — described in the code as *"the quarantine blocklist (comma-separated bucket file IDs)...
  Read at selection time so an operator can roll back a bad upload without a redeploy."* This is a
  deliberate, human-operated control surface built directly on the vendor's identifiers, and it is
  the rollback mechanism for a bad forecast.

  **This is simultaneously the strongest argument for this proposal and a requirement it must
  meet.** For it: rolling back today means the operator finding and pasting opaque Appwrite ids
  under time pressure. A `ForecastRef` carrying a run name is something a person can read, check and
  type correctly. As a requirement: the quarantine list must become a list of refs in the same
  change, or the one escape hatch that exists stops working. **This was not in the first draft and
  is the most consequential thing the review of past failure modes turned up.**
- If `latest` cannot be answered without reading the metadata table, then the table is load-bearing
  and question 2 resolves against the simple version.
- If five operations turn out to need twenty parameters between them, the interface is shallow
  wearing a deep interface's clothes, and the count was the wrong thing to optimise.
