# The Appwrite Seam Contract — Identity, Secrets & Configuration

> **SCOPE BANNER: this ADR governs the VIEWS *platform seam*, not the views-appwrite
> repository.** It is the canonical contract for identity, secrets, and shared configuration on
> the Appwrite seam, referenced **by URL at a pinned tag/commit** from every consumer repo. It is
> not this repo's internal architecture, and homing it here does not activate this repo as code
> (þing-01, D7).

| Field | Value |
|---|---|
| **Former name** | **`PLATFORM-001`** — retired 2026-07-31 by [ADR-011](../011_naming_of_cross_repo_contracts.md). Historical text, amendment-log entries and þing records keep the old name deliberately; renaming history is erasure. Citations reaching this document as `PLATFORM-001` are correct and resolve here. |
| Status | **Accepted** — ratified as amended by þing-02, 2026-07-31; v1.4.0 is an observation-driven bump carrying **no clause change** |
| Version | **1.4.1** (changes by supersession + version bump; **never silent edit** — consumers pin) |
| Amended | 2026-08-02 — **v1.4.0**: no clause changed. Companion registry records four CRAFD coordinates as issued and the CRAFD caller key as created; §10 requires the two to version together. **v1.3.0**: renamed from `PLATFORM-001` (ADR-011); §1 points at the onboarding checklist. **v1.2.0**: §1 cites the admission test, §2's four corrections, §5.1 split, §5.3 defined, §5.5 amended twice, §5.7 struck, §10 gains tag immutability. See §11 Amendment Log. |
| Ratified by | **þing-02**, all six seats + the unstaked doubter and lawspeaker; operator sign-off Simon Polichinel von der Maase. (v1.0.0 was ratified by þing-01; **v1.1.0 was proposed and never ratified** — it is superseded here, not by a decision of its author.) |
| Operator | **Simon Polichinel von der Maase** — key issuance/rotation, Appwrite console custody, test-project decision |
| Companion | `coordinate_registry.toml` (this directory) — THE canonical coordinate source, versioned in lockstep (§10) |
| Record | þing-01: `views_platform/þingit/01_identity_secrets_config/` · **þing-02: `views_platform/þingit/02_credential_identity_key_ownership/`** (orð_00–13, sáttmál, ágreiningr, aðgát, orð_dómr, rýni_00, dómr_endurmat) |

## 1. Scope

This contract governs **how a component connects** to the shared Appwrite substrate: identities,
credentials, coordinates, their classification, sourcing, validation, and failure semantics.

> **Building a new consumer API?** [`joining_the_seam.md`](joining_the_seam.md) is a non-normative
> checklist of what to do, in order, starting with pinning this contract at a tag. It imposes
> nothing this document does not; it exists because the steps were previously readable only in the
> þing record, which consumers do not pin.

**Explicitly out of scope, by cross-reference (never by omission):**
- **Eligibility** — *which* run/artifact may be served — is views-models' ADR-017 contract. The
  `APPWRITE_UNFAO_{APPROVED,QUARANTINED}_FILE_IDS` lists are eligibility *data* wearing this
  seam's prefix; they are listed in the registry as exclusions, governed there.
- **The datafactory seam** (HTTP + `~/.netrc`) — governed by views-datafactory ADR-026 +
  `credential_setup.md` (reciprocally cross-linked). A full delivery runtime needs both seams'
  credentials in one environment; the netrc entry is the sole co-resident secret. The harvest
  tokens (`UCDP_API_TOKEN`, `ACLED_USERNAME`/`ACLED_PASSWORD`, `GDL_API_TOKEN`) are needed **only
  where harvests run** — the datafactory production server, or a developer machine deliberately
  running harvest scripts; **no model, postprocessing, or serving runtime ever needs them**
  (orð_10 §1, contributed per ledger DF3).
- The legacy views-forecasts store credentials (retire with the store) and W&B keys.
- **The wire format** crossing the seam (views-postprocessing ADR-013) and **payload
  eligibility** (ADR-017) — the data half, already contracted elsewhere.

**How to tell whether a rule belongs here at all.** Admission is decided by a three-question test —
*(Q1) does the thing it governs cross the Appwrite seam · (Q2) is it true, unchanged, for a seat
that does not exist yet · (Q3) does honouring it require importing a shared implementation* — and a
rule is platform surface only if it passes all three. **The test is stated at `orð_dómr §I` D7 in
the þing-02 record and is deliberately not reproduced here**: it governs contract admission, which
does not cross the Appwrite seam, so by its own Q1 it is not contract text. Citing it rather than
importing it is §5.8 applied to this contract itself.

## 2. The identity model

**No repo holds a secret; processes do.** Every library on this seam (pipeline-core's client,
faoapi's client, any future shared client) receives credentials as constructor parameters from
the launching process and must never source, persist, default, or log them. The contract's
identity section therefore describes **callers and processes**:

| Process | Identity on the seam | Key it runs under **today** (observed 2026-07-31) |
|---|---|---|
| model/ensemble runs (views-models launcher) | writer to `production_forecasts` | `VIEWS Pipeline Core` |
| the un_fao delivery (runs *inside* the models launcher) | reader of `production_forecasts`, sole writer of `unfao_bucket` | `VIEWS Pipeline Core` — **same key value, and the same client**: see correction (i) |
| views-faoapi serving | validates the **caller's** presented key (`X-API-Key`) and re-uses it read-only. **Provisions nothing** — correction (ii) | the caller's key |
| preflights/validators | read-only | `VIEWS Pipeline Core` |

**Observed state, recorded so the contract is not read as describing reality.** The Appwrite
console holds **two** keys — `VIEWS Pipeline Core` and `UN FAO` — each carrying 20 scopes, each
expiring ~2026-11-30. Only one of them is a *platform* identity; it serves **three** of the four
rows above. `UN FAO` is a *caller's* key, and it serves **two holders** — FAO **and** this
platform's developers/operators (§5.3's floor requires that split). The four-identity model in this
table is the **target**, not the present. §5.3 states the rule; §5.5 states why the gap cannot be
closed by console action alone.

> **Nothing in this section has been read from a console by any repository.** The scope counts, the
> `~` on the expiry, and the key names are **operator testimony relayed by a seat** (þing-02 S2,
> S36). No seat can grep a console, and the record must keep saying so rather than letting relay
> harden into fact. Enumerating the 20 scopes and the exact expiry is an operator gate.

**Four corrections, adopted 2026-07-31 (þing-02 D1).** Each was supplied by the seat it cost:

- **(i) views-postprocessing imports pipeline-core's *client*, not merely its key value.**
  `views-postprocessing:views_postprocessing/unfao/managers/unfao.py:9-10` imports `AppwriteConfig`
  **and** `DatastoreModule` from `views_pipeline_core` (þing-02 S3, read at `688e19c`, corroborated
  at `e0433b4`). Every defect in that storage module is therefore live on FAO's outbound bucket
  under another repo's name. The coupling is one level deeper than "a shared secret."
- **(ii) views-faoapi provisions never.** Every `create_*` leaf is guarded by `_require_provisioning`
  (`views-faoapi@2415991:src/views_faoapi/managers/appwrite.py:482, :635, :713, :1905`) and is dead
  on the serving path (S4). The transitive-provisioning finding in §5.5 is true of
  **views-pipeline-core alone**.
- **(iii) `views-models/.env` is canonical as a *document*, not as the *mechanism*.** No
  `load_dotenv` exists in that repo (S5); `views-faoapi@2415991:deployment/bootstrap.sh:69-70` greps
  the file and is reading it correctly as a document. Separately, that repo's liveness tool reads
  **faoapi's** `.env` by a hardcoded foreign path (S6) — two `.env` files, two formats, already
  diverged.
- **(iv) A fourth provisioning site exists one level up**, at
  `views-pipeline-core@43362f7:views_pipeline_core/modules/datastore/datastore.py:350-370`, which
  catches `storage_bucket_not_found` and creates the bucket (S15). It is the site an operator hits
  first. Carried into §5.5's table.

**One live credential kind** operates on the seam (the Appwrite API key); the session-auth
strategies in the client libraries are vestigial on the serving path (þing-01 S4) and are being
excised/quarantined (faoapi #274). **The external caller's key (FAO parties) is an OPEN design
item — O2** (§9): its issuance, scope, rotation, and the confused-deputy question are unmodeled
and assigned, not silently assumed.

## 3. Classification — declared, never inferred

Every variable on the seam's environment carries a **declared class in the registry**. The
governing rule (þing-01, D3):

> **Class is declared, never inferred — not from the prefix, and not from the carrier.**

Classes: **connection** (endpoint, project id, credentials, auth method — mixed: the credential
is secret, the rest coordinates) · **target** (bucket/collection/database ids and names —
non-secret, correctness-critical, must agree across repos) · **behavioral** (TTLs, timeouts,
cache dirs — local; **never a cross-repo agreement**) · **policy pointers** (listed as exclusions,
owned elsewhere).

**The naming rule** (adopted from views-datafactory ADR-026, all four clauses):
1. The suffix `_API_KEY` / `_PASSWORD` / `_TOKEN` marks a secret — **as a lint convention and
   signal; the declared class in the registry overrides it** (dómr_endurmat E1).
2. Resolution order: explicit argument → environment variable → **fail loud naming the exact
   variable**. No other sources.
3. **No `.env`/dotenv loading in importable/library code.** A service entry point reading its own
   process environment at startup is the legitimate boundary; a library reading whatever `.env`
   the working directory holds is the disease this contract exists to cure (þing-01 S7).
4. No silent fallback to anonymous access, defaults, or hidden sources.

**Secrets span carriers**: env var, `~/.netrc`, tool keychains, and the **`X-API-Key` request
header**. The redaction clause (§5) covers all carriers.

## 4. Coordinates — the registry is the source

`coordinate_registry.toml` (this directory) is **the** canonical source of the seam's shared
coordinates. Consumers read/validate against it and pass values in explicitly. Binding rules:

- Referenced **by pinned URL/commit**; never copied into repo-local `.env` files as a source of
  truth, never baked into code, examples, or dataclass defaults ("production coordinates
  reachable without a deliberate choice" is a named hazard class — þing-01 register work).
- The registry is **readable without holding a secret** (bootstrap invariant).
- The registry is exhaustive over the seam's environment **including what it does not govern** —
  explicit exclusions with owning contracts, so nothing reads as unaccounted-for.
- The registry stays minimal: a file, owned and versioned. No tooling (dómr_endurmat E3).

## 5. Credentials — identity, tiers, one operator

### 5.1 Three things kept separate — the identity rule

Never fuse these three:

- **The identity** — a stable name for the party or process (`un_fao`, `crafd`, `views-delivery`,
  `views-ops`). It does **not** change when a key is replaced.
- **The key** — the swappable secret presented. Revocable at any time without renaming anything.
- **Any label derived from the credential** — cache partitions, log correlation ids, per-caller
  quotas. Derived from the **identity**, never from key material.

Fusing them is what makes a key un-rotatable: once the key *is* the identity, replacing it
re-identifies the holder, and every label downstream moves with it. Both live instances of this
fusion on the seam (the shared platform key of §2; the caller key faoapi re-uses as an identity)
trace to exactly this.

**The mapping is contract surface.** A component whose only input is a presented key cannot
recover a stable identity without a **key → identity mapping**, declared in the registry as slot
metadata (which identity each slot serves).

**The fix that lands now, and needs no substrate feature.** The one live instance of the fusion is
views-faoapi's cache, which partitions on `sha256(x_api_key)[:16]`
(`views-faoapi@2415991:src/views_faoapi/managers/api.py:246` →
`.../managers/disk_cache.py:71-81`), so rotating a caller's key orphans that caller's cache. A
**server-side random salt per first-seen key**, stored beside the cache, decouples the label from
the key value — no identity store, no dual-key support (þing-02 S20, D2). Four other seats grepped
and found **zero** derived labels; this is the only one.

> **UNRATIFIED — the overlap property.** *"Two live keys may map to one identity simultaneously"*
> was asserted by a seat that has never called the substrate, and is **not** ratified. Whether
> Appwrite can express it is an **operator gate**. Without an overlap window, rotation is a
> coordinated hard cutover with downtime — the friction that has kept keys from being rotated at
> all.
>
> **Pre-commitment, accepted at þing-02 by the clause's own author:** if the substrate cannot
> express two live keys for one identity, **§5.4's "rotation is a routine chore" is struck** to
> *"rotation is a coordinated cutover until an overlap mechanism exists"* — rather than left
> standing as an aspiration the contract cannot cash.
>
> The salt (above) does **not** depend on this and does **not** wait for it. It also does not make
> rotation survivable on its own: a rotated key still gets a cold partition.

### 5.2 Tiers

Tiers: **read** · **write-object** · **provision**. Split keys per tier, named per §3,
independently rotatable. **The provision key is issued to no long-running process, ever** — it is
used by a human, deliberately, through explicit setup entrypoints.

### 5.3 The floor — no key serves two parties who could need revoking separately

**"Environment" is defined**, because on this platform it is not obvious:

> An **environment** is a **credential-holding location under one party's control** — one deployed
> host, one CI runner, one person's machine.

On this platform "production" is therefore **two** locations, not one: the deployed host and the
laptop. Undefined, the rule reads as *one key per developer*, which is not what it means.

**The binding form is a floor, not a matrix** (þing-02 D3). The (identity × environment)
cross-product **generates** candidate keys; what *binds* is:

> **No key is held by two parties who could need revoking separately.**

A key serving two parties cannot be revoked for one without revoking it for both, and its blast
radius on leak is the union of both.

**Applied to today's holders**, the floor yields exactly two obligations, and no more:

1. **FAO gets its own key, separate from dev/ops.** The `UN FAO` key currently serves both (§2).
2. By correction (i) in §2, the un_fao delivery and the model writer are **one holder today, not
   two** — they run the same client under the same value — so the floor does not split them yet.

**The floor gains two new holders at the clones, not one** (þing-02 S35): `un-crafdapi` brings a
second external party and `views-productionapi` a third holder. §5.3 is **free at creation and a
migration afterwards** — which is why the clone runbook places it at t=0.

> **Assumption not verified: that issuance is cheap and unlimited.** Nobody has asked the operator
> whether there is a cap, a cost, or a lead time on issuing N keys. Both this clause and §5.5 assume
> there is not. It is an **operator gate**, and it is the same class of unverified substrate
> assertion as §5.1's overlap property.

### 5.4 Rotation touches exactly one identity

Because no key is shared, replacing or revoking a key affects only its one identity. Every key
has a named owner and a refresh schedule. **Replacing a key is a routine chore, not an
emergency** — and a rotation mechanism that has never been exercised should not be assumed to
work. Until **O1** (§9) is designed, rotation is manual and operator-coordinated.

### 5.5 Least privilege — with teeth, and with a sequencing gate

> **No key held by a long-running process carries `buckets.write`, `databases.write`,
> `collections.write`, or `attributes.write`.**

This is the **substrate-level enforcement of §6**. §6 binds *code* not to auto-provision — a
discipline enforceable only by review. This clause makes the phantom-bucket failure
*impossible*: a process whose key cannot create a bucket cannot create one at a typo'd
coordinate, whatever the code does. Belt and braces, and the braces do not depend on anyone
remembering.

**Sequencing — binding, and derived from observed evidence, not from principle.** This clause
cannot be satisfied by console action alone, because the incumbent client's *ordinary* write path
provisions transitively, at **four** sites (þing-02 S15, all verified by the owning seat):

| Call site, `views-pipeline-core@43362f7:views_pipeline_core/…` | Provisioning it reaches |
|---|---|
| `…/modules/datastore/datastore.py:350-370` | catches `storage_bucket_not_found` → **creates the bucket and retries** — the site an operator hits first |
| `…/modules/appwrite/file.py` `upload_file_with_metadata` → `:2205`, `:2351`, `:2395` | `create_metadata_collection_if_not_exists` |
| `…/modules/appwrite/file.py:1228` | `create_database_if_not_exists` |
| `…/modules/appwrite/file.py:1238`, `:1264` | `_create_dynamic_attributes` — attributes **inferred from the payload**, so the collection's shape is whatever the last caller sent |
| `…/modules/appwrite/file.py:2811` → `:2882` | bucket **and** database |

Narrowing that key today breaks every upload. **The order is therefore forced:**

> **fix C-231/C-227 → probe a scoped key → issue tier keys → declare schema → relocate `create_*`
> → narrow scopes.**

**Amendment 1 — the gate binds before *issuance*, not only before narrowing.** A tier key could
otherwise be cut with wrong scopes and fail only in production. Added by the seat that pays for it.

**Amendment 2 — the probe's key shape is normative.** The two reads are in different scope
families: the de-dup lookup is a **database** read and the verify step a **storage** read, and the
destructive branch is entered only when the lookup *succeeded*. A **wholly** read-restricted key
never reaches it and **passes benignly, certifying nothing**. The probe key must therefore have:

> **database read, and no bucket file read** — plus a wrong bucket id.

Without that shape the gate is theatre, and þing-02 struck one clause for being exactly that.

**Why the fix comes first, and it is not a priority ranking.** `get_file` collapses every
`AppwriteException` into one `success=False`; the de-dup path reads that as "orphan" and **deletes
the metadata document**. *File genuinely absent*, *wrong bucket id* and ***key lacks read scope***
are indistinguishable — so **a key that is correct under this contract could begin deleting valid
metadata the day it is issued.** That branch ran **108 times in production** on FAO's outbound
delivery on 2026-07-27, harmlessly, because the files were readable. This is a **precondition of
issuing scoped writer keys**, not a line in a priority list.

**Narrowing is the acceptance test.** A lineage's §6 change is declared done when its delivery
runtime completes an upload under a key lacking the four provisioning scopes — a substrate-enforced
proof that supersedes code review as evidence of completion. **Narrowing does not begin until the
20 scopes have been enumerated** (operator gate): nothing can be narrowed against a privilege set
nobody has listed.

### 5.6 Redaction — platform-wide and binding

Credentials in any carrier — env var, config field, request header, netrc entry, tool keychain —
are never logged; endpoints may be.

### 5.7 ~~Safety nets, per repo~~ — **STRUCK 2026-07-31 (þing-02 D5)**

> ~~Two mechanical checks, in every repo on the seam: a **secret scan** and a **registry check**.~~
>
> **Struck by its own author, under this contract's own admission test (§1), after both seats
> defending the clause withdrew on their own reasoning.** Secret scanning does not cross the
> Appwrite seam, so it is not this contract's to impose. The arithmetic is decisive: an
> organisation-level setting reaches **all 16 public repos**; a seam contract reaches **6**, and
> **10 of the exposed repos have no seat at this þing**. A clause covering a third of the problem
> while reading as coverage is worse than no clause.

**What survives, as a statement of fact rather than an obligation:**

> **A clean scanner run is a floor, not a proof.** Three limits are on the record and each was
> reported by the seat whose own clean result it undercut: (i) **prose** — a working password sat in
> an English sentence across three commits and no scanner flagged it; (ii) **merge-only content** —
> content existing solely as a merge resolution goes unscanned; (iii) **unreconciled coverage** — a
> seat reported 165 commits scanned against 226 reachable and declined to claim the gap.
> Scanning must additionally read **`.ipynb` cell contents**, which is exactly where the one real
> finding on this platform hid.

The replacement is an **organisation-level default**, not a clause, and it is an operator action.
Where a repo wants a mechanical check of its own, that is its own business and needs no
authorisation from this contract.

### 5.8 One definition, referenced — not one implementation, imported

The rules in this section are stated **once, here**, and referenced by pinned URL. They are
**not** a shared library, and adopting them creates **no dependency edge on views-appwrite** —
which remains parked, per þing-01 `dómr_endurmat` E6 and the constitutional argument that homing
a document is not homing code (orð_14 §4).

Whether a shared *implementation* should exist is a separate, live question: **D8**, deferred
behind its own trigger. That trigger is not this section, and this section must not be read as
firing it. Should D8 activate on its own terms — cloning `views-faoapi` into a second consumer
API is Trigger 1 — the implementation question is answered then, on the ratified route.

**What this clause buys, and what it costs — both recorded** (þing-02 Ó-7). It buys the absence of
a dependency edge on a repo that ships nothing, and it has live evidence behind it: correction (i)
in §2 is a two-repo defect that reached a third repo *because* a client was shared. It costs
**three independently written clients** once the clones exist — faoapi, `un-crafdapi`,
`views-productionapi`. The **conformance vector** (below) guards one invariant across them and
guards nothing else. The alternative — one shared implementation — has evidence against it and **no
pricing anywhere in the record**. That residual is **unresolved, not refuted**, and it is the right
question for D8's trigger rather than for first contact.

**The conformance vector.** A shared *test*, hosted beside this contract and run by each client
against its **own** copy — no import, no edge. It asserts one invariant:

> Two distinct callers never share a cache partition, and a partition label is neither the key
> value nor derivable from it.

Pass/fail: (i) two distinct keys yield two distinct partitions; (ii) the label cannot be derived
from the key value; (iii) a request bearing key A never serves content cached for key B. It is
authored from the **post-salt** implementation (§5.1) — written before that, it would encode the
fused behaviour as the reference and every clone would conform to the bug.

## 6. Failure semantics — raise, never provision

- **A wrong or missing coordinate raises, naming the offending coordinate.** On any path, read or
  write. Auto-provisioning of buckets/databases/collections/attributes is **opt-in, default off**,
  reachable only from deliberate setup entrypoints — never from ordinary operations. (The
  pre-contract behavior — silently creating a phantom bucket at a typo'd address — is the
  single most dangerous property this contract removes; þing-01 S8.)
- **A half-succeeded write raises.** A file landed whose metadata write failed is a failure, not
  a logged warning (the run-0 orphan; views-appwrite C-12, observed).
- Each client lineage flips to these semantics **independently** (no synchronized window), each
  preceded by a characterization test enumerating its `create_*` call sites, each declared done
  only after **real-exception-type tests and a live drill run in this order: amend → ship the
  raise change → drill the raise path → (test project exists) → drill the provisioning path.**
  Drilling before shipping would itself provision a phantom bucket in production.

## 7. Validation — the contract is executable

Every consumer runs an **in-process preflight at startup**: the resolved environment is validated
against the registry (names resolve; values match; on the write path, before expensive work),
failing loud with the exact variable name. Donor patterns: pipeline-core's
`PredictionStoreConfig.from_environment()`, faoapi's `_validate_appwrite_env()`,
views-datafactory's preflight/recurring-verification patterns.

A central **reference validator** (runnable, never importable; read-only; recurring) is
**deferred** behind the named trigger *operator ∧ test project* (views-appwrite #8). Until a test
project exists, **integration tests against the production project are forbidden**; read-only
preflight validation is the only permitted live check (þing-01 S23).

## 8. The substrate annex — schema, behavior, versions

The shared substrate's own properties are contract surface. Authoritative sources:
- **SDK behavior:** views-faoapi **ADR-018** (response normalization; the Pydantic/`model_dump`
  hazards) and pipeline-core's **C-217/C-219** record + real-SDK CI pins (`Client.call()` returns
  a parsed dict for `application/json` despite bytes annotations — broke the first FAO delivery).
- **SDK version:** views-faoapi **ADR-019** — `appwrite==19.2.0`, pinned below the
  `list_documents` removal; a declared pin silently diverging from the deployed runtime is this
  contract's pathology in dependency clothes.
- **Schema limits:** the metadata collection's filterable attributes (`name`/`category`/`type`)
  and constraints — notably `description ≤ 255` (learned from a production ERROR, run-0).

## 9. Open items — named, owned, not pretended solved

- **O1 — secret-value rotation/propagation** (owner: operator + a small design task): the
  registry moves coordinates; no mechanism yet distributes a rotated key *value* to process
  environments. Tier-2 on the seam-home register. Until closed: rotation is manual and
  operator-coordinated.
- **O2 — the FAO external-caller credential** (owner: views-faoapi + operator; views-faoapi
  #279). **Partially addressed at v1.1.0, and explicitly NOT closed.** §5.1–5.4 answer the
  *key-hygiene* half: issuance per identity, scope, rotation, and the separation that makes
  revocation survivable. The **confused-deputy** half remains open — whether faoapi should
  authenticate the caller and then act under its **own** read credential instead of re-using the
  caller's key to reach storage. That question is untouched by this amendment; keeping
  caller-brings-own-key is a *deferral*, not a decision, and it is the open half of O2.
- **O3 — credential carriers outside the tier model** (owner: views-pipeline-core + operator).
  §2 records session auth as vestigial and "being excised" — that excision is views-faoapi #274
  and covers faoapi only. `views-pipeline-core/.../modules/appwrite/file.py:359–412` still ships
  `SessionAuth`, which takes **email + password**: a credential kind that appears in no registry
  slot and fits none of §5.2's three tiers. Either
  excise it on the pipeline-core lineage too, or declare it as a slot with an owner.

## 10. Change process

Supersession, never erasure; every change bumps the version; consumers reference a pinned
tag/commit and upgrade deliberately. The registry and this contract version together. Disputes
about this contract return to the þing (or its successor process) — the seam's decisions belong
to the platform, not to any one repo.

**A published version tag is never moved.** A git tag is a *movable* reference: `git tag -f` plus a
force-push repoints a name that consumers believe is frozen, which reintroduces exactly the
mutability the pinning rule exists to remove. A commit id cannot lie about its content; a tag can.
The tag is therefore the readable handle **and** this sentence is what makes it trustworthy. To
correct a published version, cut a new one — `platform-001-v1.2.1` — and supersede.

**The pin is a rule, and rules on this platform decay unobserved unless something checks them.**
As of 2026-07-31, of five consumer repositories: one pins to a commit and that pin is **stale**
(it points at v1.0.0); one links to `/blob/main/`, which is not a pin at all and silently changed
meaning when this version landed; three cite this contract by name with no reference. **Pinning is
the consumer's obligation, and an unpinned reference is a defect in the consuming repo**, not a
licence to edit this file freely.

**Versioning is versioning of the rules.** Where this contract records observed state (§2) rather
than obligation, that state is marked as such. A version bump driven only by an observation carries
no new obligation, and a consumer diffing two versions is entitled to that distinction.

## 11. Amendment Log

### v1.4.1 — 2026-08-03 — companion registry only; no clause changed

**Status: ACCEPTED** — observation-driven, per §10. Byte-identical to v1.4.0 in every clause.

The CRAFD caller key's recorded scopes gain `buckets.read` and `tables.read`, ticked by the operator
in the console. As first issued the key held four read scopes and **could not authenticate a single
request** — views-crafdapi proves a key is real by listing buckets, so `buckets.read` is an
*authentication* requirement rather than a data-access one, and nothing about the key's purpose
suggests ticking it (C-56).

**Remediated at source; not yet verified end-to-end.** The console is authoritative for what a key
carries, and the operator confirms both boxes. Whether CRAFD's requests actually succeed is a
different question, answered by S11's smoke test (views-crafdapi#12) once the API is deployed — which
it is not yet.

**A probe was drafted and discarded**, recorded here because the reasoning generalises. It would have
had the operator paste a live secret into a shell to re-read something the console already displays.
The platform has spent real effort removing credential-handling steps; adding a ceremonial one back
for a test that answers nothing new is a bad trade, even when it is technically harmless. The console
shows the scopes — that is the check.

### v1.4.0 — 2026-08-02 — companion registry only; no clause changed

**Status: ACCEPTED** — an **observation-driven** bump in the sense §10 defines. Every clause is
byte-identical to v1.3.0. No consumer acquires an obligation by upgrading, and a consumer diffing
v1.3.0 against v1.4.0 is entitled to see exactly that.

**What changed** — all of it in `coordinate_registry.toml`:

| | |
|---|---|
| **CRAFD coordinates** | The four `APPWRITE_CRAFD_*` slots graduate `[planned]` → `[target]` with values. The operator created the bucket and metadata collection on 2026-08-02 — the shape the reservation inferred |
| **CRAFD caller key** | Recorded as issued (`crafd-caller-read`), with its console scopes enumerated — **and with the two missing scopes that stop it authenticating recorded alongside them** (C-56) |
| **Standing reservation rule** | Rewritten as a rule about the file rather than a note about four particular entries, after it inverted against its own data (C-54) |
| **Fourth identity** | `APPWRITE_DATASTORE_API_KEY.serves_identities` gains the CRAFD delivery — the graduation is what made that writer reachable (C-57) |

**Why this needed a version at all, given nothing normative moved.** §10 says *"every change bumps
the version"* and the registry's own header says changes come *"by PR to this file + a seam-contract
version bump."* Four coordinates became canonical under v1.3.0's number. Three consumers
(`views-pipeline-core`, `views-postprocessing`, `views-datafactory`) resolve this contract through
`/blob/main/` rather than a pin, and `views-postprocessing` runs a drift test that compares the
registry's `meta.version` against its own pinned `"1.3.0"` — so the merge would have changed what
they read while every check stayed green. **A version that can stand still through a content change
carries no information**, which is the whole property consumers pin for.

`docs/validate_docs.sh` gains a check for this: the previous one compared the two version numbers to
each other and to nothing else, so *bumping neither* satisfied it.

**Nothing downstream breaks.** `platform-001-v1.2.0` and the v1.3.0 tag are not moved, per §10.

### v1.3.0 — 2026-07-31 — renamed; no clause changed

**Status: RATIFIED** — this version changes the document's *identity*, not its obligations. Every
clause is byte-identical to v1.2.0 apart from §1's pointer to the onboarding checklist.

**What changed**

| | |
|---|---|
| **Name** | `PLATFORM-001` → **The Appwrite Seam Contract**. File moves to `appwrite_seam_contract.md`. Recorded by [ADR-011](../011_naming_of_cross_repo_contracts.md) |
| **Alias** | `PLATFORM-001` retained as a `Former name` header row. Historical text, this log, and þing records keep the old name deliberately |
| **§1** | Gains a five-line pointer to [`joining_the_seam.md`](joining_the_seam.md), a **non-normative** onboarding checklist. Imposes nothing new |

**Why.** The identifier carried no information at the point of use, and on this platform that has a
measured cost: unreadable identifiers **hide staleness**. Two consumer repos are pinned at commit
`60674b2` — v1.0.0 — and neither noticed through two subsequent versions, because nothing about that
string can be compared by eye. `PLATFORM-001` fails the same way. The number also indexed a set of
size one. The maintainer reported being unable to remember what it referred to on three separate
occasions.

**Nothing downstream breaks.** Correctly-pinned URLs resolve against commits where the old filename
still exists. The alias catches readers arriving with the old identifier. The 76 prose citations in
the five consumer repos are tracked per-repo (views-faoapi#340, views-models#304,
views-pipeline-core#335, views-postprocessing#158, views-datafactory#395) and are explicitly
**cosmetic and non-blocking** — no consumer is asked to repoint a pin as part of a rename.

**`platform-001-v1.2.0` is not moved**, per §10. Anyone pinned to it continues to resolve to the
pre-rename file, correctly, indefinitely. That is the pinning rule working as designed, and it is
what makes a rename safe to perform at all.

---

### v1.2.0 — 2026-07-31 — ratified by þing-02; §5.7 struck

**Status: RATIFIED.** This is the first ratified version since v1.0.0 — **v1.1.0 was proposed and
never ratified**, and is superseded here by the assembly rather than by its author.

**Cause.** þing-02, *"Credential identity, key ownership and least privilege on the Appwrite
seam"* (`views_platform/þingit/02_credential_identity_key_ownership/`). Six seats plus an unstaked
doubter and lawspeaker; `orð_dómr.md` as amended by `dómr_endurmat.md` (E1–E11); operator sign-off.
v1.1.0's clauses were disposed of individually rather than accepted as a block.

| § | Disposition |
|---|---|
| 1 | **New**: cites the admission test by reference (A2′). The test is *not* contract text — it fails its own Q1, and a meta-rule exemption would have reopened §5.7's strike, which rested on that same question. Found by the reviewer against its own ledger row |
| 2 | **Ratified**, with four corrections owed to it — each supplied by the seat it cost (D1) |
| 5.1 | **Split** (D2): the cache salt lands now; the two-live-keys property is unratified and goes to the operator |
| 5.3 | **Ratified as amended** (D3): "environment" defined; the binding form is the floor, not the matrix |
| 5.5 | **Ratified**, amended twice (D4): the gate binds before *issuance*; the probe's key shape is normative |
| 5.7 | **STRUCK** (D5) — see below |
| 5.8 | **Ratified** (D6), the most attacked clause in the matter; plus the conformance vector, and its residual recorded |
| 10 | tag immutability, the pin-decay finding, and the observation-vs-obligation distinction |

**§5.7's strike is the finding of this version, and the clause count goes *down*.** Struck by its
own author under this contract's own admission test, after **both** seats defending it withdrew on
their own reasoning. Secret scanning does not cross the Appwrite seam. The replacement is an
organisation-level setting reaching 16 repositories where a clause reaches 6 — and ten of the
exposed repositories have no seat at any þing, so no clause here could ever have reached them.

**What this version deliberately does not do.** No identity store. No shared client library. No
platform-wide branch-retirement programme. No new secret-scanning clause. views-appwrite remains
**parked**: no repository imports it, and þing-01 D8's trigger is untouched.

**Corrections this version makes to its own predecessor.** v1.1.0's §2 was wrong in two ways that
mattered: it claimed `views-models/.env` was the credential *mechanism* (it is a document — there is
no `load_dotenv` in that repo), and its transitive-provisioning finding was written as though it
applied to views-faoapi (it does not — faoapi provisions never). Both were corrected by the seats
whose testimony they had made load-bearing.

**Known and unresolved, carried rather than papered over.** Three independently written clients
will exist once the clones are cut; the conformance vector guards one invariant and nothing else;
the alternative has no pricing in the record (§5.8). Whether the substrate can express two live
keys for one identity is unverified (§5.1). Whether key issuance is cheap and unlimited is
unverified (§5.3). Nobody has read the 20 scopes on either key (§2).

---

### v1.1.0 — 2026-07-31 — credential identity, least privilege with teeth, observed state

**Status: SUPERSEDED by v1.2.0, never ratified.** Proposed by views-appwrite and put to þing-02,
which disposed of its clauses individually — five ratified (three with amendments), one struck.
Consumers pinned to v1.0.0 were unaffected throughout.

**Cause.** Two inputs. (1) A draft platform ADR from the views-faoapi seat
(*"How VIEWS APIs Handle Keys and Who Owns Them"*, 2026-07-31) proposing general key-ownership
rules and nominating this contract's home as their host. (2) First direct observation of the
Appwrite console by the operator, plus a trace of the incumbent client's provisioning call sites
— evidence no seat held at þing-01, when key scopes were recorded as *"unknowable from evidence"*
(S22).

**What changed.**

| § | Change |
|---|---|
| 2 | Identity table gains an observed-state column and a correction note: one platform key serves three of four identities; two keys exist, 20 scopes each, expiring ~2026-11-30 |
| 5.1 | **New** — identity / key / derived-label separation, and the key→identity mapping with its two-live-keys overlap property |
| 5.3–5.4 | **New** — one key per (identity × environment); rotation touches one identity |
| 5.5 | **New** — least privilege made enforceable (`no long-running process holds provisioning scopes`), plus the sequencing gate and the narrowing-as-acceptance-test rule |
| 5.7 | **New** — per-repo secret scan + registry check |
| 5.8 | **New** — one definition referenced, not one implementation imported; D8 explicitly not fired |
| 9 | O2 restated as half-addressed; **O3 added** (SessionAuth email+password carrier) |

**What was rejected from the source draft, and why.**

- *"`views-appwrite` has to be a real, working dependency before we clone anything"* and *"use
  views-appwrite for the key model, the private-box rule, and the no-cross-serve check — don't
  copy them."* **Rejected.** These make this repo an importable runtime dependency, reversing
  `dómr_endurmat` E6 (scaffold deferred; repo parked) and pre-empting **D8**, which is
  trigger-gated. §5.8 states the distinction that preserves both: the *rule* is shared, the
  *implementation* is not. Nothing here prevents D8 activating on its own trigger.
- *"Decide the rules first, then fix the key."* **Rejected as a platform clause** — a live
  compromised credential is an incident, not an input to a design process, and the two are not
  coupled: a like-for-like reissuance requires no rules. Recorded here because the reasoning
  would otherwise propagate to the next incident. The operator has decided to sequence
  remediation behind governance; that is the operator's call to make and it is noted, not
  contested. The clause does not enter this contract.
- *Caller-authentication policy* (the draft's Rule 6 and §5 adoption runbook). **Not adopted
  here** — this contract governs how a process authenticates **to Appwrite**, not how a web API
  authenticates its own HTTP callers. That is views-faoapi ADR-027's subject. Generality alone
  does not make a rule this contract's: the test is *general* **and** *about the Appwrite seam*.

**Factual corrections to the source draft, from evidence.**

- The draft states the leaked key's replacement would cut off *"FAO, the developers, and
  operations."* Operations runs under a separate key (`VIEWS Pipeline Core`), so the blast radius
  is FAO plus developers. The wound is real; its stated extent was not.
- The draft locates key-sharing only in the `UN FAO` key. A **second** three-identity sharing
  exists and is arguably more consequential — the platform key that writes into FAO's outbound
  bucket (§2).
- Least privilege is not achievable by console action for the platform key: the incumbent
  client's ordinary upload path provisions transitively (§5.5 table). The draft's Rule 3 assumes
  otherwise.

**Register effect (views-appwrite, the seam-home register).** C-27 (O1 rotation) gains a date:
both live keys expire ~2026-11-30, so an unexercised rotation mechanism meets a forced deadline.
C-28 (O2) narrows to the confused-deputy half. New material for C-21's hazard class: a key whose
scopes exceed its process's need is "production power reachable without a deliberate choice."

**Companion registry.** `coordinate_registry.toml` moves to 1.1.0 with this amendment: the
*"Legacy single key"* entry is replaced by the two observed keys with their console names, served
identities, and scope/expiry observations; `FAO_CALLER_API_KEY` is listed as a caller slot with
its owning contract; the planned tier slots gain §5.1 identity metadata; and an `[unmodelled]`
section records the O3 carrier. The registry and this contract version together (§10).

---
*Ratified 2026-07-28 (þing-01, as amended by dómr_endurmat E1–E9). Implementation lands via the
27-issue ledger recorded in the þing's `issues.gh`; this repo's rows: #2–#9. Amended 2026-07-31
to v1.1.0 (§11) — **proposed, pending seat acceptance**.*
