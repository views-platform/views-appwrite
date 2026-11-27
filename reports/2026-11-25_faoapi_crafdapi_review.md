# Multi-Expert Review — views-faoapi and views-crafdapi

**Date:** 2026-11-25
**Scope:** `views-faoapi` and `views-crafdapi`, source and tests. GitHub issues read only after the
findings were complete, as instructed.
**Reviewer:** reading session, Claude Opus 5.
**Literature:** quoted only from the chapter extracts at `~/Desktop/views_blueprints/reading/`,
converted to text and read during this review. Nothing is quoted from memory.

**Claim labels.** **Checked** = verified in the code during this review. **Read** = taken from a
document. **Estimated** = cannot be checked.

---

## The two answers first

### 1. What will it take to make them work correctly?

**One live defect can put a wrong forecast in FAO's hands, and it is already filed.** Issue #660
(label `bug`, opened 2026-11-25): `/pg/data/forecast/bulk` and `/data/forecast/bulk` serve the cached
artefact without checking which run it belongs to. **Read** from the issue body, which reports it as
reproduced against the real writer and the real route: a download after run B landed returned run A's
bytes, 74,301 bytes both times. That is the whole of "not working correctly" in the sense that matters
to a paying partner — everything else on this list is a cost, not a wrong number.

**The structural reason it happens, and the reason it will happen again.** The service caches a
*derived artefact* keyed on a cache slot, and the slot's validity is decided by three gates — file
exists, schema version matches, TTL not expired. **Checked:** none of those gates is the run
identity. The design permits a stale slot to be indistinguishable from a fresh one. A guard on those
three gates fixes this instance. It does not remove the class.

**views-crafdapi has already removed the class.** **Checked:** crafdapi exposes five routes
(`/ping`, `/version`, `/bulk/{level}/{outcome}`, `/slice/{level}/{outcome}`, `/health`); faoapi
exposes fifteen. #660's own body says crafdapi "has already solved it by a method that makes it
impossible rather than guarded." The two repositories are described as deliberate clones; **on the
serving surface they are no longer clones, and crafdapi is the simpler one.**

**So the minimum change to make faoapi work correctly is a convergence, not a repair:**

1. **Name the artefact by the run that produced it.** If the file on disk is addressed by run
   identity rather than by a cache slot with a TTL, serving the wrong month stops being reachable.
   This closes #660 structurally and makes #643 (a permanently null run-fitness field) moot.
2. **Stop reading the store under the caller's credential.** **Checked:**
   `managers/api.py:378-405`, `_create_appwrite_config`, passes `credentials=x_api_key` — the
   partner's own Appwrite key — into the store client, and `_validate_api_key` says it "validates the
   API key on every call." Every partner request therefore depends on Appwrite being reachable *and*
   on the partner's vendor key being valid. This is epic #581 S3/S4 (#584, #585) and is in flight.
   Until it lands, a key expiry at Appwrite is a partner outage, and the vendor cannot be replaced
   without re-issuing partner credentials.
3. **Settle the key-vocabulary blocker.** **Read** from epic #600: Appwrite 1.8 renamed Databases to
   TablesDB non-additively; this service's one partner-facing metadata read is
   `databases.list_documents` at `managers/appwrite/metadata.py:464`, and a key minted today is
   offered only `tables.*`/`rows.*`. It works only because both current keys predate the rename. The
   next rotation breaks delivery. This is the single highest-risk item on the board and it is
   calendar-driven, not effort-driven.
4. **Stop serving the vendor's identifiers.** **Checked:** `managers/api.py:686` and `:694` put
   `file_id` into the partner response payload, and `:990`, `:1026`, `:1052` republish it as
   `artifact_id`. **Checked:** four routes carry Appwrite's nouns in the public URL path —
   `/files/{bucket_id}`, `/files/{bucket_id}/{file_id}/info`, `/files/{bucket_id}/{file_id}/download`,
   `/files/{bucket_id}/{file_id}/cached`. A partner who has stored one of those URLs holds a
   reference that only Appwrite can redeem. Issue #650 asks whether `/files/*` is a declared partner
   contract at all; it should be answered "no" and the routes removed.

**What it will take, in one sentence:** close #660 by naming artefacts after runs, finish #581 so the
service holds its own key, resolve #600 before the next key rotation, and delete the four `/files/*`
routes. Nothing on that list requires a new abstraction.

### 2. How much source code can be deleted before the core task suffers?

Core task taken as: *read a finished forecast for a level and outcome, and serve it to a partner.*

**views-faoapi is 14,855 source lines in 68 files. Roughly 8,000 to 9,000 of them can go.** The
estimate is tiered by what has to be decided first; only Tier A is a measurement rather than a
projection.

**Tier A — deletable now, no decision required. 1,656 lines, 11%. Checked** by walking the import
graph from the real entry point (`views_faoapi.managers.api:create_app`, per
`deployment/views-faoapi.service:38`). These modules are not reachable from the running application:

| lines | module | note |
|---|---|---|
| 566 | `smoke.py` | test scaffolding living in `src/` |
| 451 | `client.py` | a consumer-side client shipped inside the server |
| 325 | `plotting.py` | a serving API that draws maps with matplotlib |
| 93 | `managers/forecast_loader.py` | |
| 74 | `evict_cache.py` | |
| 49 | `forecast/geography/level_mapping.py` | |
| 45 | `wandb/utils.py` | plus the `wandb==0.18.7` dependency on a serving box |
| 29 | `forecast/conformance.py` | |
| 24 | `time.py` | |

The remainder of the 1,656 is empty or near-empty `__init__` files. **Caveat:** "unreachable from the
app" is not "unused" — `plotting.py` has 40 references in notebooks and docs, `smoke.py` is
presumably run by hand. The correct action for those two is *move*, not delete; for the rest,
delete. Also note this is the honest number: a first attempt at this measurement mis-resolved
relative imports inside package `__init__` files and reported 7,761 unreachable lines. That figure
was wrong and is recorded here so it is not quoted later.

**Tier B — deletable when ADR-012's gateway exists. 2,270 source lines and 2,046 test lines.
Estimated.** `managers/appwrite/` is **2,421 lines** (**Checked**). **Read** from
`views-appwrite/docs/boundary_tests.md` test 8: faoapi performs **three** store operations
(`get_predictions_by_metadata`, `download_prediction`, `get_latest_file_id`) while defining eleven.
An HTTP client for three routes is on the order of 150 lines. The two test files that exist only to
mock the vendor — `tests/test_appwrite_manager.py` (1,447 lines) and `tests/test_sdk_compat.py` (599)
— go with it. **Checked:** 261 `patch`/`Mock` calls in the test suite, 33 of them naming Appwrite.

**Tier C — deletable if the service reads a finished file instead of building one. 3,000 to 4,000
lines. Estimated.** `data/handlers/` is 2,476 lines (`grid_dataset.py` 1,488, `forecast_dataset.py`
936) and `forecast/` is 2,221 — ingestion, densification, summarisation, cross-level aggregation,
serialisation. **Read**: `views-publicapi/SPECS.md` §8 assigns densification and summarisation to a
postprocessor upstream of the serving layer. If that holds, most of these two trees are in the wrong
repository rather than wrong.

**Tier D — deletable if monthly data is served as named static files. ~900 lines plus a class of
bug. Estimated.** `managers/disk_cache.py` 588, `managers/locked_cache.py` 165, and the three
in-process caches at `managers/api.py:361-363`. **Checked** from the `locked_cache.py` module
docstring: driving those three caches from 14 worker threads produced **28,236**, **4,340** and
**37,544** `KeyError`s respectively, and two of the three ended with their eviction bound broken. A
mutex was added to stop the corruption; the docstring states plainly that it does not protect a
cached value's contents, which is C-371 and issue #637. **All of this machinery exists to cache data
that changes once a month.**

**views-crafdapi: 13,039 lines, same arithmetic, same tiers**, with two differences. **Checked:** it
has no `wandb`, no `evict_cache.py` and no `locked_cache.py`, its `api.py` is 1,099 lines against
faoapi's 1,860, and it carries a `preflight.py` of 521 lines that faoapi does not. Its five-route
surface is the target shape.

**The single most useful sentence in this section:** faoapi has ten routes crafdapi does not, and
crafdapi delivers the same product. The deletion question has a worked example inside the platform.

---

## System summary

Two FastAPI services, deployed under systemd on one shared 22 GiB host (faoapi on :8000, crafdapi on
:8001), each serving monthly conflict-forecast data to one partner — the UN FAO and CRAFD
respectively. Each reads forecast files and metadata from an Appwrite bucket and collection, converts
them to dense grids and summary statistics, caches derived artefacts on disk and in process, and
exposes them over HTTP. They were forked from one codebase on 2026-08-02 and kept separate
deliberately to observe divergence. faoapi is 14,855 source lines over 68 files with 29,171 lines of
tests; crafdapi is 13,039 and 21,962. **Checked.**

---

## Expert reviews

### Robert C. Martin

**Strengths.** The deployment boundary is real: `deployment/views-faoapi.service` names a uvicorn
factory, a checked-out deploy tag and an `EnvironmentFile`, so the runtime contract is explicit rather
than assumed. `managers/appwrite/__init__.py` documents an intentional split of the write/provision
surface from the read surface, which is an architectural decision recorded at the place it binds.
Dependency pinning is reasoned in `pyproject.toml` with CVE identifiers against each floor — unusual
discipline.

**Weaknesses.** *The dependency arrow points the wrong way, and it is visible in the URL space.* Four
routes name `{bucket_id}` and `{file_id}` in the path. His criterion in the boundary chapter is that
high-level policy must not depend on low-level detail; here the lowest-level detail — the vendor's
object identifiers — is in the outermost public contract. **Checked.**

*`managers/api.py` is a 1,860-line class that is simultaneously the controller, the authenticator,
the cache owner, the health reporter and the payload serialiser.* **Read** from #620: 34 route
handlers, authentication, three caches, `/health`, payload assembly, artefact preparation and the
FastAPI dependencies, in one file. There is no boundary inside it to point an arrow across.

*The business rule is expressed in the vendor's terms.* `metadata.py:464` calls
`databases.list_documents` directly for the one partner-facing metadata read. On his ch. 30 argument
— *"The organizational structure of data, the data model, is architecturally significant. The
technologies and systems that move data on and off a rotating magnetic surface are not"* — the data
model here is a forecast for a level, an outcome and a month. Nothing above the store should know the
word `documents`, and the word is load-bearing enough that epic #600 exists because Appwrite renamed
it.

**Improvements.** (1) Delete `/files/*` and remove `file_id`/`artifact_id` from every response body;
the partner-visible identity becomes run, level and outcome. (2) Extract one `ForecastStore`
interface owned by the service, with the three operations faoapi actually performs, and let the
Appwrite code implement it from below. (3) Split `api.py` along the seam #620 asks about — routes and
payload assembly do not share state with the caches.

### Gang of Four

**Strengths.** `managers/appwrite/auth.py` carries an `AuthFactory`/`AuthManager`/`ApiKeyAuth`
hierarchy — a Strategy with a Factory, correctly applied where more than one auth method was
anticipated. `managers/appwrite/sdk_compat.py` is a small Adapter (`_as_dict`, `_get`) isolating SDK
response-shape differences. `LockedCache` is a clean Decorator over a `MutableMapping`.

**Weaknesses.** *The Strategy has one strategy.* **Checked:** `config.py` declares an `AuthMethod`
and `api.py` passes `auth_method="api_key"` as a literal. Three classes and a factory stand where one
function would do, and the generality was never exercised.

*The Adapter is adapting a dependency the service pins exactly.* `sdk_compat.py` is 51 source lines
with 599 lines of test, against `appwrite==19.2.0` — a pinned version. An adapter earns its place
when the thing behind it varies; this one guards a constant.

*`AppWriteFileManager` is a 1,273-line God Object* rather than a pattern. **Checked** it is the single
largest non-route file in the Appwrite package, and **Read** from boundary test 8 that three of its
eleven operations are used.

**Improvements.** (1) Collapse the auth hierarchy to one function until a second auth method is
required by a named caller. (2) Delete `sdk_compat.py` and its 599 test lines, or move the two
helpers into the one call site that needs them, since the SDK version is pinned. (3) If the gateway
lands, none of these patterns survives — do not refactor them first.

### Michael Feathers

**Strengths.** The seams that exist are real ones: `create_app` as a factory is a genuine test seam,
and `AppwriteConfig` being constructed in one method (`_create_appwrite_config`) means the credential
path has a single point of interception. Test coverage is enormous — 29,171 lines — so changes are
not being made blind.

**Weaknesses.** *The test suite is pinned to the implementation it should be freeing.* 261
`patch`/`Mock` calls, 1,447 lines mocking the vendor manager, 599 mocking an SDK shim. This is the
situation Freeman & Pryce describe directly: *"tests that mock external libraries often need to be
complex to get the code into the right state for the functionality we need to exercise. The mess in
such tests is telling us that the design isn't right but, instead of fixing the problem by improving
the code, we have to carry the extra complexity in both code and test."* **The 2:1 test-to-source
ratio is not safety here; it is the cost of the missing seam**, and it is why every attempt to simplify
makes the repository grow.

*There is no seam at the store.* To test "serve the right month" you must mock Appwrite. If a
`ForecastStore` interface existed, the test would hand over a fake with two runs in it, and #660
would have been caught by a unit test rather than by a falsification audit.

*`api.py` cannot be tested in parts* because the caches, the auth probe and the route handlers are
one object.

**Improvements.** (1) Introduce the store interface and write one fake; retire the vendor mocks
against it. Freeman & Pryce's prescription is explicit — *"We keep this layer as thin as possible, to
minimize the amount of potentially brittle and hard-to-test code"* — and 2,421 lines is not thin.
(2) Characterise the four routes FAO actually calls before touching anything else; **Read** from #660
that the FAO notebook calls only the two bulk download routes. (3) Treat the test suite as a
deletion target of the same size as the source.

### Michael T. Nygard

**Strengths.** `/health` assembles freshness, serving state and store reachability rather than
returning 200 unconditionally. The systemd unit sets `Restart=always` with `RestartSec=5` and a
cgroup memory cap sized against a measured co-tenancy budget. There is an external daily monitor
(#496 refers to it).

**Weaknesses.** *The partner's credential is a coupling to a third party in the request path.*
**Checked:** `_validate_api_key` validates against Appwrite on every call. That is a synchronous
dependency on an external service, per request, with no circuit breaker in evidence. An Appwrite
slowdown becomes a partner-visible stall, and a key expiry becomes a partner outage.

*The caches were a stability hazard, and the fix is partial by its own account.* The `locked_cache.py`
docstring is unusually honest: two of three caches ended in "structural corruption — the eviction
policy has stopped holding, so the cache can grow past the bound it exists to enforce," and for the
DataFrame cache on a 22 GiB host "that is an unbounded-growth path." The mutex closes the corruption
and explicitly does not close C-371.

*Stale-serving is a silent failure.* #660 returns 200 with last month's bytes. There is no louder
failure mode available: the partner cannot tell.

**Improvements.** (1) Serve named static files and the cache tier disappears, along with the
eviction, the TTL, the mutex and C-371. (2) Make freshness a property of the artefact's name, so
staleness cannot be silent. (3) Separate the partner's authorisation from the store's credential
(#581) so an upstream outage cannot be caused by a partner's key.

### Martin Kleppmann

**Strengths.** The data is immutable once a month, which is the easiest possible consistency regime,
and the design acknowledges it (`disk_cache` TTL is 24.5 days). Metadata is declared in one place
upstream (**Read:** `views-pipeline-core/.../provisioning.py`). Schema versioning exists in the cache
gate.

**Weaknesses.** *The identity of a forecast run is not a first-class value anywhere.* It is implied by
a cache slot, a TTL and an Appwrite `fileId`. #660 is the direct consequence: with no run identity in
the read path, "is this the current forecast?" is not a question the code can ask.

*Derived state is cached in four places with four different invalidation rules* — three in-process
caches, a disk cache, the Appwrite file cache, and 463 MB of `appwrite_cache/` on disk (**Checked**;
it is gitignored at `.gitignore:211`). Each has its own notion of when it is wrong.

*A cached value is mutated in place after publication.* **Read** from the `locked_cache.py` docstring:
`DatasetService` writes six fields into each per-category dict after it is stored, outside the lock,
so "a reader can see a half-updated value."

**Improvements.** (1) Make the run identifier — a name VIEWS issues, not Appwrite's `fileId` — part
of every artefact name and every response. (2) One cache, or none. Given monthly immutability, none
is defensible. (3) Build values whole and store them in one assignment (#637).

### John Ousterhout

**Strengths.** `views-postprocessing`'s sibling pattern aside, this codebase does contain genuine
information hiding in places: `sdk_compat.py` concentrates SDK shape knowledge, and
`managers/appwrite/__init__.py` states which half a read-only clone drops.

**Weaknesses.** *`forecast/` is textbook temporal decomposition, and he names the exact shape.*
**Checked:** the package is `ingestion/` → `summarize/` + `aggregate/` → `serialize/`. His §5.3 reads:
*"Consider an application that reads a file in a particular format, modifies the contents of the file,
and then writes the file out again. With temporal decomposition, this application might be broken into
three classes: one to read the file, another to perform the modifications, and a third to write out the
new version. Both the file reading and file writing steps have knowledge about the file format, which
results in information leakage."* That is `ingestion/parquet_reader.py` and `serialize/bulk_parquet.py`,
both knowing the forecast file's shape. His red flag states the test: *"If the same knowledge is used
at different points in execution, it gets encoded in multiple places, resulting in information
leakage."* The prescription is to combine the read and write mechanisms into one module, and his
closing instruction is the one to act on: *"focus on the knowledge that's needed to perform each task,
not the order in which tasks occur."*

*Special-general mixture at the store client.* `AppWriteFileManager` holds a general-purpose Appwrite
file mechanism *and* forecast-specific specialisations, plus provisioning DDL. His red flag: *"This
red flag occurs when a general-purpose mechanism also contains code specialized for a particular use
of that mechanism... future modifications to the use case are likely to require changes to the
underlying mechanism as well."* §9.4's remedy is to pull special-purpose code upwards and leave the
lower layer general — the opposite of what a read-only partner API needs from a 2,421-line vendor
package.

*The interface of the Appwrite package is its entire contents.* **Checked:**
`managers/appwrite/__init__.py` re-exports 22 names, including four raw SDK classes (`Client`,
`Storage`, `Databases`, `Users`). Any importer of the package gets the vendor's own types in scope.
This is why module-level reachability found almost nothing dead: the package has no narrow face.

**Improvements.** (1) Replace `ingestion/`+`serialize/` with one module that owns the forecast file
format, per §5.3. (2) Stop re-exporting SDK classes from `__init__`; the vendor's types should not be
reachable through a first-party package root. (3) Judge the gateway by the interface it removes, not
the lines it saves.

### Rich Hickey

**Strengths.** The forecast datum is genuinely a value — immutable, monthly, reproducible — and
Parquet is an appropriate place-free representation of it.

**Weaknesses.** *Place-oriented programming at the centre.* The service's model of a forecast is a
*slot*: a cache path whose contents change. `artefact_path` returning non-`None` means "something is
here", not "this is run B". #660 is the defect that identity-by-place always produces.

*Incidental complexity dominates.* Of 14,855 lines, the essential task — read a file for a level and
outcome, project columns, serialise — is a small fraction. Caches, mocks, auth strategies,
provisioning, plotting and smoke scaffolding are all incidental to it.

*Complecting authorisation with storage access.* One string, `x_api_key`, answers both "may this
caller in?" and "what may be read from the vendor?" Those are two decisions braided into one value;
#588 is the attempt to unbraid them.

**Improvements.** (1) Name artefacts by their content or their run, so identity travels with the
value. (2) Separate the two meanings of the caller's key. (3) Prefer deleting incidental machinery
over abstracting it.

### Kent Beck

**Strengths.** Tests exist in quantity and the repository has clearly been driven by them;
`tests/test_concurrency_model.py` (732 lines) is a real response to a real measured defect. Issues are
written with measurements in them, which is a healthy feedback loop.

**Weaknesses.** *The simplest thing that could possibly work was never attempted.* The product is one
file per level and outcome per month. A static file server would deliver it. Instead the first version
shipped a slice route, a grid builder, four cache tiers and a per-caller Appwrite manager cache.

*The feedback loop has inverted.* **Checked:** 122 open issues on faoapi, 72 on crafdapi; of the
faoapi set, 50 are `story`, 12 are `epic`, 31 are `planning`. The recent commit stream — threads,
caches, keys, registers, ADRs — contains no commit about delivering a forecast. Each pass adds a
guard; none removes a capability. That is the mechanism behind "every time I work through the issues,
the codebase grows."

*YAGNI breached in specific, nameable places:* `provisioning.py` (DDL in a read-only partner API),
`wandb` (experiment tracking on a serving box), `plotting.py` (map rendering in an HTTP service),
`client.py` (a consumer library inside the server), the `AuthFactory` with one strategy,
and six of eleven store operations that no production code calls.

**Improvements.** (1) Pick the four routes FAO actually uses and declare the other eleven out of
contract. (2) Adopt a rule that no issue may be closed by adding a file; a closing commit must have a
negative line delta or state why not. (3) Make deletion the default response to a finding.

### The Maintainer (sufficiency verdict)

**Verdict: the architecture is not the thing that is broken. The scope is.**

The engineering standard in these repositories is high — measured issue bodies, CVE-reasoned pins, a
cache docstring that reports its own residual defect by number. This is not a careless codebase. It
is a careful codebase doing far more than its job, and the care is what makes it expensive: every
capability is held to the same high standard, including the ones nobody asked for.

**Findings I judge not worth acting on now:**

- *The `AuthFactory`/`AuthManager` hierarchy.* Three classes too many, 45 lines. If the gateway lands
  it is deleted anyway. Fixing it now is motion.
- *`sdk_compat.py` as an adapter over a pinned dependency.* Correct criticism, wrong moment — its 599
  test lines are the cost, and they are paid already. Delete both with the Appwrite package, not
  before.
- *Splitting `api.py` into modules.* #620 is right that it is too big, and it is explicitly scoped as
  an investigation rather than a refactor. Splitting a 1,860-line file whose route count is about to
  drop from fifteen to five is work done twice. **Do the deletion first; the split may not be needed.**
- *The `forecast/` temporal decomposition.* Diagnostically the sharpest finding in this review, and
  the cheapest to ignore for now, because Tier C moves most of that tree to another repository. Act on
  it if and only if the densification stays here.
- *The 463 MB `appwrite_cache/`.* Gitignored, on a box with a measured memory cap, not a correctness
  issue. Housekeeping.

**What is worth acting on, in this order:** #660 (a wrong forecast can reach FAO), #600 (the next key
rotation stops delivery), #581/#584/#585 (the service holds its own key), then Tier A deletion and the
`/files/*` removal (#650). Everything else waits.

---

## Key disagreements between experts

**D-01 — Feathers against Beck, on the test suite.** Feathers reads 29,171 test lines as the asset
that makes change safe; Beck reads them as the receipt for complexity that should not exist. Both are
right about different halves: the tests covering the four routes FAO calls are the asset; the 2,046
lines mocking a pinned vendor SDK are the receipt. The disagreement resolves by splitting the suite
along that line, not by choosing a side.

**D-02 — Martin against the Maintainer, on `api.py`.** Martin wants the boundary drawn inside the
1,860-line class now. The Maintainer says the route count is about to fall by two thirds, so drawing
it now is work done twice. Unresolved, and the tiebreak is whether `/files/*` is a partner contract —
which is exactly what #650 asks.

**D-03 — Ousterhout against Tier C.** Ousterhout's §5.3 prescription is to *combine* the reading and
writing of the forecast format into one module. Tier C proposes *moving* most of that code to the
postprocessor instead. These conflict: one says fix the decomposition here, the other says it is not
this repository's work. Resolution depends on SPECS.md §8 holding, which is **Read**, not settled.

**D-04 — Kleppmann against Nygard, on caching.** Kleppmann says one cache or none. Nygard's
availability instinct wants a local copy so an Appwrite outage is not a partner outage. Reconcilable:
a named static file on disk *is* the local copy, and it has no invalidation rule to get wrong.

---

## Failure mode analysis

Register-compatible concern entries. Not appended to any register; invoke `register-risk` to file.

**C-A1 · Tier 1 · Wrong data to a paying partner.**
*Trigger:* a new run lands upstream while a cache slot is inside its 24.5-day TTL; the next partner
download returns the previous month.
*Source:* this review, corroborating #660. *Location:* `managers/api.py` bulk routes →
`FAODiskCacheManager.artefact_path`.
*Narrative:* artefact validity is gated on existence, schema version and TTL, never on run identity.
Returns 200 with stale bytes; undetectable by the partner.

**C-A2 · Tier 1 · The next key rotation stops delivery.**
*Trigger:* either faoapi key is rotated or recreated in the Appwrite console.
*Source:* **Read** from epic #600. *Location:* `managers/appwrite/metadata.py:464`.
*Narrative:* the partner-facing metadata read uses `databases.list_documents`; post-1.8 keys are
offered only `tables.*`/`rows.*`. Delivery currently works only because both keys predate the rename.
Calendar-driven.

**C-A3 · Tier 2 · A partner's vendor key is in the request path.**
*Trigger:* Appwrite latency, outage, or partner key expiry. *Source:* this review, **Checked** at
`managers/api.py:378-405`. *Narrative:* the store is read under `credentials=x_api_key` and the key is
validated against Appwrite per call, so a third party's availability and a partner's credential
hygiene both gate the product. Mitigation in flight as #581 S3/S4.

**C-A4 · Tier 2 · Vendor identifiers are in the public contract.**
*Trigger:* replacing or renaming the store. *Source:* this review, **Checked** at `managers/api.py`
`:686`, `:694`, `:990`, `:1026`, `:1052` and the four `/files/{bucket_id}/{file_id}/*` routes.
*Narrative:* any partner-held URL or recorded `file_id`/`artifact_id` becomes a dead reference. Makes
the gateway's benefit conditional. Related: #650.

**C-A5 · Tier 2 · Unbounded memory growth in the DataFrame cache.**
*Trigger:* concurrent requests under eviction pressure. *Source:* **Read** from
`managers/locked_cache.py` docstring. *Narrative:* measured eviction-bound breakage before the mutex;
the mutex does not protect value contents (C-371, #637), and the box is shared with crafdapi under a
cgroup cap.

**C-A6 · Tier 3 · The backlog grows faster than the product.**
*Trigger:* working the issue list. *Source:* this review, **Checked**: 122 open issues on faoapi, 50
`story`, 12 `epic`; no recent commit concerns delivering a forecast.
*Narrative:* every finding is converted into a guard, a proof or a runbook, and none into a deletion.
The backlog is a faithful record of a system too large to finish.

---

## Long-term regret test

**What will be regretted in twelve months if nothing changes.**

*Most likely regret:* that the two repositories diverged in capability rather than converging on the
smaller one. crafdapi already has five routes and has already made #660 impossible. The experiment in
deliberate cloning has produced a result — one fork got simpler and better — and the result is not
being harvested.

*Second:* that the vendor's identifiers were published. Every month that `file_id` appears in a
response or a URL, more of it exists in partner-side notebooks, scripts and citations. This is the
cheapest thing on the list to stop and the most expensive to undo.

*Third:* that 2,046 lines of test were written against a pinned vendor SDK. They will be deleted
unread when the gateway lands, and the effort is unrecoverable.

**What will be regretted if the review's advice is followed too enthusiastically.** Deleting
`plotting.py` and `smoke.py` outright rather than moving them — they have 40 and several references in
notebooks and docs respectively, and the notebooks are a delivered artefact. And deleting the tests
covering the four live routes along with the vendor mocks.

---

## Engineering recommendation

**Do not refactor. Converge faoapi on crafdapi, and delete.**

1. **Close #660 by naming artefacts after runs, not slots.** One wrong forecast reaching FAO costs
   more than everything else here. Structural, not a guard.
2. **Resolve #600 before any key rotation.** Calendar-driven and currently load-bearing on two keys
   created on 2026-10-29.
3. **Finish #581 S3/S4** so the service reads under its own key and the partner's key only decides
   entry.
4. **Answer #650 "no" and delete the four `/files/*` routes**, plus `file_id` and `artifact_id` from
   every response body. Fifteen routes becomes eleven; crafdapi shows five is enough.
5. **Take Tier A: delete 1,656 unreachable lines**, moving `plotting.py` and `smoke.py` rather than
   deleting them. No decision required, nothing depends on them.
6. **Then, and only then,** decide ADR-012 (Tier B), SPECS §8 ownership (Tier C) and the static-file
   serving model (Tier D). Each is a large deletion gated on one decision.
7. **Adopt one rule with teeth:** a commit that closes an issue must reduce the line count, or say in
   the message why it cannot. This is the only item on the list that addresses C-A6, which is the
   reason the other six have not happened yet.

**What not to do now:** split `api.py` (#620), fix the auth hierarchy, repair the `forecast/`
decomposition, or touch `sdk_compat.py`. All four are real findings whose code is scheduled for
deletion by the steps above.

---

## Issue reconciliation (read after the findings, as instructed)

**The issue tracker is not the problem. It is better than the code.** #660, #600 and #620 are
measured, specific and honest. Most of what this review found was already filed.

**Findings already filed, no new issue needed:**

| finding | existing issue |
|---|---|
| Stale run served from cache | **#660** (`bug`) — matches exactly, including the reproduction |
| `databases.list_documents` vs post-1.8 keys | **#600** (epic) |
| Service reads under the caller's key | **#584**, **#585** (epic #581 S3/S4) |
| Caller key conflates entry with store access | **#588** |
| `api.py` is too large and holds seven concerns | **#620** — and correctly scoped as investigation |
| Cached value mutated after publication (C-371) | **#637** |
| `/files/*` may not be a partner contract | **#650** |
| `AppwriteConfig` defaults name the producer's bucket | **#593** — the dead-default finding, already filed |
| Permanently null run-fitness field | **#643** |
| Cache security fixes present in crafdapi, absent here | **#576**, **#579** |

**Issues that should be re-scoped in light of this review:**

- **#620** should be told that the route count is likely to fall from fifteen to five, because that
  changes the answer to its own question. Splitting `api.py` may be unnecessary rather than deferred.
- **#650** should be promoted. It is currently one story inside an epic, and answering it "no" is
  prerequisite to four of the seven recommendations above. It is also the cheapest Tier-1 mitigation
  of C-A4.
- **#576** ("did crafdapi's four cache security fixes need applying here?") should be reframed. The
  more useful question is not whether to port fixes from crafdapi to faoapi, but **why faoapi has a
  cache surface crafdapi does not** — the answer is ten extra routes.

**What is genuinely missing from the tracker — three gaps, not thirty:**

1. **No issue proposes deleting anything.** Of 122 open faoapi issues, none asks for a capability to
   be removed. `plotting.py`, `smoke.py`, `client.py`, `wandb`, `provisioning.py` and the six unused
   store operations are unrepresented. This is the gap that explains the growth.
2. **No issue records that crafdapi is the simpler fork and should be the target shape.** The cloning
   was deliberate and has produced a measurable result; nothing captures it.
3. **No issue covers the publication of vendor identifiers in response bodies.** #650 covers the
   `/files/*` routes; `file_id` and `artifact_id` inside the bulk and provenance payloads are
   separate and unfiled. (This is the same finding as `views-pipeline-core#619`,
   `views-faoapi#615`, `views-crafdapi#261` and `views-postprocessing#343`, filed 2026-11-24 as
   investigative placeholders — but those ask who issues identifiers, not whether this service
   publishes them.)

**On the 122 open issues as an artefact.** 50 stories, 12 epics, 31 planning items. Every one appears
to be true. Collectively they describe a system larger than one maintainer can finish, and working
them in order is what has produced four weeks of slippage: each is a correct response to a real
finding, and each adds code. The only intervention that changes the trajectory is recommendation 7 —
make deletion the default outcome of a finding — and that is a policy change, not an engineering task.
