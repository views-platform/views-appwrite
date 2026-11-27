# ADR-016: Appwrite is the delivery door, not the prediction store

**Status:** Proposed
**Date:** 2026-11-27
**Decider:** Simon Polichinel von der Maase, maintainer of the VIEWS forecasting platform

*This document is a plan under serious consideration, not a commitment. It is written down so that it can be argued with, and so that work started elsewhere can be sequenced against it. A reader new to this platform should read ADR-012 first; its glossary serves this document too.*

---

## In short

Appwrite is doing four jobs on this platform. Only one of them is the reason it was chosen.

It is **the credentialed door that outside partners pull forecasts from**. That is the job. The other three — holding the forecasts themselves, answering *which file is newest*, and being the place a partner's access is switched off — came along with it.

This document proposes that **the forecasts stop living in Appwrite**. A VIEWS-owned prediction store on Hetzner, beside the data factory, replaces both the legacy `views-forecasts` store and the `production_forecasts` bucket. Appwrite keeps the per-audience delivery buckets and the partner keys, because that is what it is for.

The practical consequence is larger than it sounds, and it arrives before any gateway is written: once the prediction store answers *which run is newest*, the metadata table leaves the vendor, and with it the half of the vendor's interface that cost this platform two weeks in October.

---

## Context

### What is true today

**Checked 2026-11-27**, by parsing every tracked `.py` file in each repository and by installing two of them without the vendor's SDK.

- **Three repositories import the Appwrite SDK: 35 files.** views-pipeline-core 18, views-faoapi 11, views-crafdapi 6. views-postprocessing, views-models and views-datafactory import it in **zero** files; they reach the store through views-pipeline-core.
- **Neither partner API can be imported with the SDK absent.** 17 of about 67 modules per repository fail, including the file that builds the HTTP application. The cause in both is four files, one of which re-exports the vendor's own classes at a package root. The business half — forecasting, ingestion, geography, serialization — imports clean.
- **A partner is authenticated by a live call to Appwrite with that partner's own key.** `views-faoapi/src/views_faoapi/managers/api.py:408` builds an Appwrite configuration from the request's `x-api-key` header and lists one file in the delivery bucket. There is no local list of callers anywhere on this platform.
- **Five store operations are live out of eleven**, and each partner API uses three. **Read** — `docs/boundary_tests.md` test 8, measured 2026-11-25.
- **Two prediction stores exist side by side.** The Appwrite `production_forecasts` bucket feeds the two partner APIs; the legacy `views-forecasts` store (Postgres plus SFTP) feeds the public API. Both are written by views-pipeline-core. **Read** — `~/Desktop/views_blueprints/00_review_of_the_sketch.md`, checked 2026-11-21.

### What it costs

In October the vendor renamed its Databases API to TablesDB. The same fix was owed in five repositories, and the work took two weeks. That is not an accident of this vendor: it is what happens when five places hold the vendor's vocabulary — its error strings, its field names, its service classes.

Hohpe & Woolf name the remedy and the arithmetic. A **Canonical Data Model** — one format, independent of any application — needs *N* translators where direct agreement between every pair needs up to *N × (N − 1)*. Today's platform is the second case.

### Why the store is the lever

The vendor's interface splits cleanly in two.

- **Files.** Buckets, uploads, downloads. This is the delivery product.
- **Rows.** A metadata table of thirteen declared fields whose only job is to answer *which file is the newest run, and what is in it*. This is an index.

**The October rename was in the second half.** An index is not something a file-delivery product is uniquely able to provide; a store VIEWS owns answers it directly, without a vendor API, without a scope generation, and without an asynchronous attribute-creation rule that four incidents paid to learn.

---

## The proposal

**1. The forecasts move to a VIEWS-owned prediction store on Hetzner.** It sits with the data factory and the feature factory, and it replaces both existing stores: the legacy `views-forecasts` store and the Appwrite `production_forecasts` bucket.

**2. Its technology and access method are not decided here.** That is deliberate and it is the largest open item in this document. What is decided is its *role*: it is the one place a finished run is read from, by one writer (views-pipeline-core) and a small number of readers inside the platform.

**3. Appwrite keeps the delivery buckets, one curated file set per audience, and nothing else.** No forecasts at rest, no metadata table, no index. Partners keep their Appwrite keys and keep pulling from Appwrite; that is the job it was chosen for and this document does not touch it.

**4. The delivery job remains the only writer of those buckets.** views-postprocessing cuts one product per audience and hands it over; it imports the SDK in zero files today and will continue to.

**5. One program does the handing over.** This is ADR-012's gateway, unchanged in form: a service on a Hetzner host, reached over HTTP, that nobody installs. This document narrows what it has to carry — see below.

**6. Nothing moves before it is proven with a live call.** Seam contract §8's standing rule. It applies to the new store exactly as it applies to the vendor.

---

## What this changes about ADR-012

ADR-012 point 4 puts the internal prediction store out of scope, *"whose technology and access method nobody has chosen yet"*. This document is the choice that paragraph was waiting for, and it makes ADR-012 cheaper rather than wrong:

- **The gateway's metadata contract shrinks or disappears.** ADR-012 scopes the gateway to *"the partner delivery buckets and their metadata records — listing, reading, writing, and the metadata contract."* If the prediction store answers *which run is newest*, the delivery buckets need no queryable metadata table, and the gateway's surface reduces to: write a curated file, list and read it, and check a caller's key.
- **The load-bearing open question in ADR-012 — what operations the gateway offers — gets smaller and easier.** It was recorded there on 2026-11-24 as the decision the whole ADR rests on.
- **The argument for the service form survives this change, but on different grounds.** ADR-012 argues a service because a library leaves every consumer holding its own pinned copy. After this move there is one writer, so that argument weakens — and a new one replaces it: the gateway is then the only holder of a bucket-**write** credential, which keeps write authority off the partner-facing API servers. That is a credential argument, not a duplication argument, and it is the stronger one.

---

## Rationale

**Because the vendor is being used for a job it was not chosen for.** The forecasts could live anywhere. The credentialed door could not — partners hold keys to it, and revoking a partner means deleting a key. Keeping the files in the same product as the door buys nothing and couples five repositories to the door's vendor.

**Because it removes the duplication at its source rather than wrapping it.** Freeman & Pryce's adapter layer and Hohpe & Woolf's Messaging Gateway both hide a vendor behind an interface in your own terms. Neither claims to remove a dependency that need not exist. Half of this one need not exist.

**Because it is the cheaper half to move.** The index has no outside party in it. Moving the forecasts changes no partner's credentials, no partner's URL and no partner's file format. The door — the half with outside parties attached — is exactly the half this proposal does **not** move.

**Because the measurement supports it.** The business code in both partner APIs already imports clean without the vendor. What binds them to it is four files each, and three of the five live operations. Remove the index and that falls further.

**Because it ends a second, older duplication at the same time.** Two prediction stores exist today, and the public API is fed by the legacy one. One store replaces both.

---

## What was considered instead

**Leave the forecasts in Appwrite and consolidate the client.** This is the activated epic. It is strictly less effective: it reduces five copies of the calling code to one, and leaves the vendor's vocabulary in the platform permanently, including the half that broke in October.

**Move everything, including the partner door, off Appwrite.** Rejected here, and the reason is not technical: partners hold Appwrite credentials, so leaving the vendor entirely is a re-credentialing of outside organisations on their timetable, not a data migration. The door is the one piece where the vendor is genuinely earning its place.

**Do nothing until the gateway exists.** Rejected because sequencing runs the other way: the gateway's surface depends on whether the delivery buckets still need a metadata table, so deciding the store first makes the gateway smaller and later work cheaper.

---

## What this costs, and what it does not fix

- **A new store has to be built, run, backed up and monitored.** None of that exists today, and the platform already operates three Hetzner servers.
- **A migration with two readers that cannot be interrupted.** Both partner APIs serve live partners from the current bucket. There is no scheduled downtime on this platform because there is no schedule.
- **It does not remove the vendor.** It removes the vendor from the forecast path. The identity path stays, deliberately.
- **It does not by itself end the per-repository duplication.** That depends on the open question below.
- **The legacy store's retirement drags the public API with it**, which has its own undecided questions about which runs it shows and whether it keeps its address.

---

## Sequence, and what blocks what

1. **Decide the prediction store's technology and access method.** Everything else waits on it.
2. **Stand it up beside the data factory and write to it in parallel** with the current store, so that the two can be compared on real runs before anything is cut over.
3. **Move the readers one at a time**, least consequential first, each proven by a real delivery before the next starts — ADR-012's point 5 discipline.
4. **Only then narrow the delivery buckets**, removing the metadata table once nothing reads it.
5. **Retire the legacy store and settle the public API's questions** separately; it is not on the partner path.

**Not blocked by this document, and should not wait for it:** the TablesDB migration in views-pipeline-core, which unblocks a partner delivery now and whose code this proposal eventually deletes. Finishing it costs little and removes a live failure; see `views-pipeline-core` issue #599.

---

## Still open

- **Do the partner APIs read through the gateway, or read the buckets directly?** The maintainer's own open point 10 on the target drawing of 2026-11-21. If they go through the gateway, the vendor's vocabulary exists in exactly one program and the duplication ends. If they read directly, two copies survive permanently, and a third arrives with the public API. **This is the question that decides whether the whole effort succeeds or merely shrinks.**
- **The prediction store's technology and access method.** Not decided. See point 2.
- **Who issues the identifier that crosses the boundary**, filed as placeholders in four repositories. A store VIEWS owns can issue its own run identifier, which may make this easier; it does not make it automatic.
- **Whether the delivery buckets need any metadata at all** once the store answers freshness, or whether a filename convention suffices.
- **What happens to the six store operations that only tests call.** Found by `docs/boundary_tests.md` test 8; never resolved.
- **Whether partner authentication stays a live probe against Appwrite**, or becomes one call to the gateway. The probe is currently inside both partner APIs.

---

## How we would know it worked

- **Test 4 passes in both partner APIs.** Install each without the Appwrite SDK and import it. Both fail today, 2026-11-27; a pass is the measurement that the vendor has left the application. `docs/boundary_tests.md` test 4.
- **Test 6 finds no shared vendor literals.** No error string or field name of the vendor's appears on both sides of the boundary. 73 shared literals were found on 2026-11-24.
- **A vendor change costs one repository.** The honest test, and the only one that measures the thing this platform actually wants. It cannot be run on demand; it is observed the next time the vendor moves.

---

## References

- `docs/ADRs/012_the_appwrite_gateway.md` — the gateway's form, Proposed, with five challenge entries
- `docs/boundary_tests.md` — tests 3, 4, 6 and 8, and what each cannot tell you
- `docs/what_we_learned.md` — the literature, one source at a time, and the synthesis
- `docs/ADRs/platform/appwrite_seam_contract.md` §8 — the substrate facts four incidents paid for
- `~/Desktop/views_blueprints/01_views_platform_today` and `02_views_platform_future` — the as-built and target drawings, 2026-11-21
- `reports/c4_appwrite_boundary.html` — the same two states in the C4 model's vocabulary, 2026-11-27
- Hohpe & Woolf, *Enterprise Integration Patterns*, ch. 8 pp. 322-329 (Canonical Data Model) and ch. 10 pp. 418-427 (Messaging Gateway)
- Freeman & Pryce, *Growing Object-Oriented Software, Guided by Tests*, ch. 8 (adapter layer; do not mock types you cannot change)
- `views-pipeline-core` issue #599 — the TablesDB migration, half complete, not blocked by this document
