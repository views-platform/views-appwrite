# PLATFORM-001 — Identity, Secrets & Configuration Contract (VIEWS Appwrite seam)

> **SCOPE BANNER: this ADR governs the VIEWS *platform seam*, not the views-appwrite
> repository.** It is the canonical contract for identity, secrets, and shared configuration on
> the Appwrite seam, referenced **by URL at a pinned tag/commit** from every consumer repo. It is
> not this repo's internal architecture, and homing it here does not activate this repo as code
> (þing-01, D7).

| Field | Value |
|---|---|
| Status | **Accepted** — ratified as amended by þing-01, 2026-07-28 |
| Version | 1.0.0 (changes by supersession + version bump; **never silent edit** — consumers pin) |
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
  credentials in one environment; the netrc entry is the sole co-resident secret.
- The legacy views-forecasts store credentials (retire with the store) and W&B keys.
- **The wire format** crossing the seam (views-postprocessing ADR-013) and **payload
  eligibility** (ADR-017) — the data half, already contracted elsewhere.

## 2. The identity model

**No repo holds a secret; processes do.** Every library on this seam (pipeline-core's client,
faoapi's client, any future shared client) receives credentials as constructor parameters from
the launching process and must never source, persist, default, or log them. The contract's
identity section therefore describes **callers and processes**:

| Process | Identity on the seam |
|---|---|
| model/ensemble runs (views-models launcher) | writer to `production_forecasts` under the write key |
| the un_fao delivery (runs *inside* the models launcher) | reader of `production_forecasts`, sole writer of `unfao_bucket` |
| views-faoapi serving | validates the **caller's** presented key (`X-API-Key`) and re-uses it read-only |
| preflights/validators | read-only, under the read key |

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

## 5. Credentials — three tiers, one operator

- Tiers: **read** · **write-object** · **provision**. Split keys per tier, named per §3,
  independently rotatable. **The provision key is issued to no long-running process, ever** — it
  is used by a human, deliberately, through explicit setup entrypoints.
- The legacy single fanned-out key (whose scopes no seat could state from evidence — þing-01
  S22) is retired by reissuance under this model.
- **The operator** (Simon Polichinel von der Maase) issues keys, holds console custody, decides
  the test project, and owns rotation. Until **O1** (§9) is designed, rotation is a manual,
  operator-coordinated platform event.
- **Redaction, platform-wide and binding:** credentials in any carrier — env var, config field,
  request header, netrc entry, tool keychain — are never logged; endpoints may be.

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
  #279): issuance to external parties, scope, rotation, and whether faoapi should authenticate
  the caller then act under its own read credential instead of re-using the caller's key.

## 10. Change process

Supersession, never erasure; every change bumps the version; consumers reference a pinned
tag/commit and upgrade deliberately. The registry and this contract version together. Disputes
about this contract return to the þing (or its successor process) — the seam's decisions belong
to the platform, not to any one repo.

---
*Ratified 2026-07-28 (þing-01, as amended by dómr_endurmat E1–E9). Implementation lands via the
27-issue ledger recorded in the þing's `issues.gh`; this repo's rows: #2–#9.*
