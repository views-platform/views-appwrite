# PLATFORM-001 — Identity, Secrets & Configuration Contract (VIEWS Appwrite seam)

> **SCOPE BANNER: this ADR governs the VIEWS *platform seam*, not the views-appwrite
> repository.** It is the canonical contract for identity, secrets, and shared configuration on
> the Appwrite seam, referenced **by URL at a pinned tag/commit** from every consumer repo. It is
> not this repo's internal architecture, and homing it here does not activate this repo as code
> (þing-01, D7).

| Field | Value |
|---|---|
| Status | **Accepted** — ratified as amended by þing-01, 2026-07-28 |
| Version | **1.1.0** (changes by supersession + version bump; **never silent edit** — consumers pin) |
| Amended | 2026-07-31 — §2 identity table corrected against observed state; §5 gains the credential-identity rules (5.1) and least-privilege-with-teeth (5.5); §9 O2 restated, O3 added. See §11 Amendment Log. |
| Ratified by | all six seats: views-faoapi, views-postprocessing, views-models, views-pipeline-core, views-datafactory, views-appwrite; human sign-off Simon Polichinel von der Maase |
| Operator | **Simon Polichinel von der Maase** — key issuance/rotation, Appwrite console custody, test-project decision |
| Companion | `coordinate_registry.toml` (this directory) — THE canonical coordinate source |
| Record | `views_platform/þingit/01_identity_secrets_config/` (local þing record: orð_00–14, sáttmál, ágreiningr, orð_dómr + dómr_endurmat) |

## 1. Scope

This contract governs **how a component connects** to the shared Appwrite substrate: identities,
credentials, coordinates, their classification, sourcing, validation, and failure semantics.

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

## 2. The identity model

**No repo holds a secret; processes do.** Every library on this seam (pipeline-core's client,
faoapi's client, any future shared client) receives credentials as constructor parameters from
the launching process and must never source, persist, default, or log them. The contract's
identity section therefore describes **callers and processes**:

| Process | Identity on the seam | Key it runs under **today** (observed 2026-07-31) |
|---|---|---|
| model/ensemble runs (views-models launcher) | writer to `production_forecasts` | `VIEWS Pipeline Core` |
| the un_fao delivery (runs *inside* the models launcher) | reader of `production_forecasts`, sole writer of `unfao_bucket` | `VIEWS Pipeline Core` — **same key value**: `views-postprocessing/views_postprocessing/unfao/managers/unfao.py:187` and `views-pipeline-core/views_pipeline_core/configs/prediction_store.py:16` both read `APPWRITE_DATASTORE_API_KEY` |
| views-faoapi serving | validates the **caller's** presented key (`X-API-Key`) and re-uses it read-only | the caller's key |
| preflights/validators | read-only | `VIEWS Pipeline Core` |

**Observed state, recorded so the contract is not read as describing reality.** The Appwrite
console holds **two** keys — `VIEWS Pipeline Core` and `UN FAO` — each carrying 20 scopes, each
expiring ~2026-11-30. Only one of them is a *platform* identity; it serves **three** of the four
rows above. `UN FAO` is a *caller's* key (and is separately compromised — views-faoapi's local
ADR owns that wound and its remediation). The four-identity model in this table is therefore the
**target**, not the present. §5.3 states the rule; §5.5 states why the gap cannot be closed by
console action alone.

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
recover a stable identity without a **key → identity mapping**. That mapping is declared in the
registry as slot metadata (which identity each slot serves) and must satisfy one property:

> **Two live keys may map to one identity simultaneously.**

Without that overlap window, rotation is a coordinated hard cutover with downtime — which is the
friction that has kept keys from being rotated at all. With it, §5.4 is achievable.

### 5.2 Tiers

Tiers: **read** · **write-object** · **provision**. Split keys per tier, named per §3,
independently rotatable. **The provision key is issued to no long-running process, ever** — it is
used by a human, deliberately, through explicit setup entrypoints.

### 5.3 One key per (identity × environment); no key serves two owners

Every key serves exactly one identity in exactly one environment. `un_fao`-production,
`un_fao`-test, `crafd`-production, `views-delivery`-production, `views-ops`-dev are all distinct
keys. A key that serves two identities cannot be revoked for one without revoking it for both,
and its blast radius on leak is the union of both.

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
provisions transitively:

| Call site (`views-pipeline-core/views_pipeline_core/modules/appwrite/file.py`) | Provisioning it reaches |
|---|---|
| `upload_file_with_metadata` → `:2205`, `:2351`, `:2395` | `create_metadata_collection_if_not_exists` |
| `create_metadata_collection_if_not_exists:1228` | `create_database_if_not_exists` |
| `:1238`, `:1264` | `_create_dynamic_attributes` |
| `create_bucket:2811` → `:2882` | bucket **and** database |

Narrowing that key today breaks every upload. The order is therefore forced, and it extends §6's
drill ordering by one step:

> **amend → ship the `create_*` gating → drill the raise path → narrow the key → (test project
> exists) → drill the provisioning path under the provision key.**

**The narrowing is the acceptance test.** A lineage's §6 change is declared done when its
delivery runtime completes an upload under a key that lacks the four provisioning scopes. That is
a substrate-enforced proof and it supersedes code review as the evidence of completion.

### 5.6 Redaction — platform-wide and binding

Credentials in any carrier — env var, config field, request header, netrc entry, tool keychain —
are never logged; endpoints may be.

### 5.7 Safety nets, per repo

Two mechanical checks, in every repo on the seam: a **secret scan** (a real key can never be
committed) and a **registry check** (every identity × environment has its own declared slot; no
slot serves two identities). These are per-repo obligations — one *definition*, stated here;
implementations are not shared code (see §5.8).

### 5.8 One definition, referenced — not one implementation, imported

The rules in this section are stated **once, here**, and referenced by pinned URL. They are
**not** a shared library, and adopting them creates **no dependency edge on views-appwrite** —
which remains parked, per þing-01 `dómr_endurmat` E6 and the constitutional argument that homing
a document is not homing code (orð_14 §4).

Whether a shared *implementation* should exist is a separate, live question: **D8**, deferred
behind its own trigger. That trigger is not this section, and this section must not be read as
firing it. Should D8 activate on its own terms — cloning `views-faoapi` into a second consumer
API is Trigger 1 — the implementation question is answered then, on the ratified route.

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
  slot, fits none of §5.2's three tiers, and is unreachable by the §5.7 registry check. Either
  excise it on the pipeline-core lineage too, or declare it as a slot with an owner.

## 10. Change process

Supersession, never erasure; every change bumps the version; consumers reference a pinned
tag/commit and upgrade deliberately. The registry and this contract version together. Disputes
about this contract return to the þing (or its successor process) — the seam's decisions belong
to the platform, not to any one repo.

## 11. Amendment Log

### v1.1.0 — 2026-07-31 — credential identity, least privilege with teeth, observed state

**Status of this version: PROPOSED.** v1.0.0 remains the ratified text until the seats bound by
these clauses accept. Consumers pinned to v1.0.0 are unaffected until they move their pin.

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
