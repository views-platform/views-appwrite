# The Appwrite keys — what exists, who holds it, and how to rotate one

**Status: ACTIVE.** Non-normative companion to the [Appwrite Seam Contract](appwrite_seam_contract.md).
Added 2026-11-12.

> **NON-NORMATIVE.** This document imposes no obligation the [seam
> contract](appwrite_seam_contract.md) does not already impose. Where it says *must*, it is reporting
> an obligation that lives elsewhere, and says where. It exists because the key inventory lived in
> three places that disagreed — and the one place that is supposed to be canonical was the one that
> was wrong. Nothing here needs ratification, and adding to it triggers no version bump.

**Who this is for:** you are about to rotate a key, issue a new one, or work out why a request is
returning 401.

---

## 1. Why this document exists — read this before trusting anything else here

On **2026-11-12** a session in this repository read `coordinate_registry.toml`, found *"both
platform keys expire 2026-11-17, no stagger and no fallback"*, and reported a five-day emergency to
the operator.

**There was no emergency.** The keys had been rotated three weeks earlier, and the operator had
confirmed it from the console twice in the preceding two days. Everything in use expires in 2027.

Every other repository on the seam had been updated. **The canonical registry — the one artefact
whose entire purpose is to be the inventory — was the last to know, and nothing anywhere compared
the two.** þing-04's `aðgát §1` had named the exact contradiction a day earlier: *"different names,
eleven months apart, successors or a stale registry, nobody knows which."* The operator answered it
at **G2-1**. The answer reached the þing record and never reached this repo.

That is register cluster **I**'s thesis — *"no inventory stays true"* — and the fourth instance in
the four it lists. It is also why §2 below carries a read-date on every row: **a key fact without a
date and a reader is a soft fact, and this platform plans against those.**

## 2. What exists today

**Five keys are in use.** Two more exist and are retired.

| Console key | Who holds it | Scopes | Expires | Last established |
|---|---|---|---|---|
| `pipeline-core-writer` | the producer: `views-models`, `views-pipeline-core`, `views-postprocessing` | 6, "load-bearing" | **2027-10-29** | console, 2026-11-11 (þing-04 G2-1) |
| `faoapi-server` | the `views-faoapi` box **and** its daily monitor | 4, all reads | **2027-10-29** | console, 2026-11-11 (þing-04 G2-1) |
| `faoapi-caller-fao` | **UN FAO** — they present it as `X-API-Key` | 3 | **2027-10-20** | console, 2026-11-12 — *in use* |
| `crafdapi-probe` | `views-crafdapi` smoke, notebooks, integration tests, daily monitor | per views-crafdapi ADR-038 | **never** | console, 2026-10-20 |
| `crafd-caller-read` | **CRAF'd** — external partner | **14**, all `.read` | **never** | console, 2026-11-11 (þing-04 G2) |

| Retired key | Was | Scopes | Dies | State |
|---|---|---|---|---|
| `VIEWS Pipeline Core` | the producer key | 20 as read 2026-08-05 | **2026-11-17 12:35** | nothing authenticates with it; kept as fallback |
| `faoapi-legacy-shared-RETIRING` | the `UN FAO` key — FAO *and* server *and* dev/ops at once | 20 as read 2026-08-02 | **2026-11-17 16:10** | renamed 2026-10-20; nothing authenticates with it |

**Sources, so the next reader can re-verify rather than re-trust:**

- Successor names, 11-month terms, and *"the two expiring keys are the old ones"* —
  `þingit/04_audience_isolation/baton.md:116`, the operator's own G2-1 answer, console read
  2026-11-11.
- Successor dates and roles — `views-postprocessing/tests/test_credential_expiry.py:40-79`, which is
  also the platform's only executing expiry tripwire.
- FAO confirmed on their own key — `views-faoapi/reports/technical_risk_register.md:4156-4169`,
  **C-259 resolved 2026-11-12**: *"FAO are on `faoapi-caller-fao` and the console shows it in use."*
- `crafdapi-probe` / `crafd-caller-read` never expire —
  `views-crafdapi/deployment/RELEASE_RUNBOOK.md:367-369`, console read 2026-10-20.
- The split that produced the FAO pair — `views-faoapi/deployment/KEY_SPLIT_AND_ROTATION_RUNBOOK.md`
  and `views-faoapi/reports/post_mortems/2026-10-20_the_night_the_key_was_proven.md`.

### Three figures in this table are not as solid as they look

**The 2027 expiry *times* are not a console reading.** Each successor was created on 2026-10-29 with
a one-year term, so the *date* is arithmetic and the time is creation-order guesswork.
`test_credential_expiry.py` says so in its own comment and declines to invent precision; this
document declines with it. **Do not quote a time.**

**`faoapi-caller-fao`'s three scopes are not established anywhere this repo can read.** The runbook
that nominally defines them grants `files.read, documents.read, databases.read` — and
**views-faoapi#543 / C-282 record that a key built to exactly that table returned
`401 … missing scopes (["buckets.read"])` on every request.** So the table is wrong, the key works
(verified 28/28 on 2026-10-20), and therefore the key does not carry what the table says. The actual
three need a console read. Recorded as unknown rather than copied.

**The scope *counts* disagree across records.** This repo read 20 scopes on each old key
(2026-07-31 / 2026-08-02); views-postprocessing calls the same pair "36-scope keys" in October. Both
may be right — Appwrite has since split the vocabulary into further generations — but nobody has
reconciled them, and a count without a date is worth nothing.

## 3. One variable name holds four different keys

This is the single most dangerous fact about rotating anything here.

```
APPWRITE_DATASTORE_API_KEY
```

That one name carries **`pipeline-core-writer`** in `views-models/.env`, **`faoapi-server`** on the
faoapi box and in views-faoapi's Actions secrets, **`crafdapi-probe`** in views-crafdapi's, and
FAO's own **`faoapi-caller-fao`** in the `.env` they create from our delivery bundle.

**A rotation that updates "everywhere `APPWRITE_DATASTORE_API_KEY` appears" with one new value
cross-wires three identities.** views-crafdapi's register **C-256** records this having cost real
time twice.

**Therefore the inventory below is keyed by console key, never by variable name.** If you are
holding a checklist organised by variable name, throw it away.

## 4. Every surface that holds a key value

Measured across all 19 repositories on 2026-11-12. **Tier A is authoritative: missing one causes an
outage or a silent blind spot.**

### `pipeline-core-writer` — the producer

| Surface | Where | Note |
|---|---|---|
| `views-models/.env` | line 17 | **the sole carrier.** `tools/credentials/platform_env.sh:157` says so explicitly; appended by `bootstrap.sh:107-132`; exported at `platform_env.sh:225`; sourced by `monthly_run.sh:147-148` and `tools/launcher/postprocessor.sh:50,230` |
| `/root/.secrets` on the GPU pod | — | **no file in any repo points at it.** `tools/podrun/pod_run_fao_delivery.sh:158-160` requires the values be exported, e.g. `set -a; . /root/.secrets; set +a`. A grep-driven checklist misses this |
| password manager | — | declared source of truth: `views-crafdapi/deployment/RELEASE_RUNBOOK.md:350-354` |

`views-pipeline-core` and `views-postprocessing` **read** this key and supply it nowhere — they
inherit the process environment. That is by design, and it means they need no rotation step.

### `faoapi-server` — the faoapi box and its monitor

| Surface | Where | Note |
|---|---|---|
| `/home/views-faoapi-deploy/.env.faoapi` | declared at `views-faoapi/deployment/views-faoapi.service:23`; written by `deployment/bootstrap.sh:88` | not in any repo — lives only on the box |
| views-faoapi **Actions secret** | `.github/workflows/data-freshness.yml:75,90` | **the holder its own runbook forgot** (register **C-345**). A dead key here leaves the job **green**, not red — it stops reporting, which looks like nothing being wrong |

### `crafdapi-probe` — crafdapi

| Surface | Where |
|---|---|
| `/home/views-crafdapi-deploy/.env.crafdapi` | `views-crafdapi/deployment/views-crafdapi.service:38`, written by `deployment/bootstrap.sh:117`; also read by `deployment/partner_key_check.py` |
| views-crafdapi **Actions secret** | `.github/workflows/data-freshness.yml:86,101,256` — opens an issue when its key is rejected (#173) |
| `views-crafdapi/.env` | line 7, local dev |

### `faoapi-caller-fao` — FAO's own

Held by FAO, on their machines. **Nothing in this platform installs it.** The only artefact here is
the placeholder in the delivery bundle (`fao_delivery_*/.env.example`), with instructions at
`views-faoapi/notebooks/README.md:116,131`. Changing it means a message to FAO and their clock, not
ours.

### `crafd-caller-read` — CRAF'd's own

Same shape: held by the partner. It appears in **no code anywhere in the workspace** — only in the
registry and the þing record.

### Not in any repository, and therefore missed by every grep

- **the Better Stack monitor** — `views-faoapi/reports/ops/betterstack_deployment.md:59`: the
  `faoapi — forecast health` monitor sends a valid key in an `X-API-Key` header. This surface exists
  only in prose; nothing in any repo fails if it is missed.
- **`/root/.secrets` on the GPU pod**, above.

### Stale copies that still hold a live value

`views-models/.env.bak` and `views-models/.env.bak-2026-08-02-134410` both contain a key value.
`bootstrap.sh:126` creates a new timestamped backup on every run, so this set grows with each
rotation. They break nothing; they are leak surface, and they should be purged in the same change as
any rotation.

## 5. How to rotate a key

### The two substrate facts the procedure rests on

From Appwrite's own documentation, read 2026-11-12 (`appwrite.io/docs/partners/project/key-rotation`,
`appwrite.io/docs/advanced/platform/api-keys`):

> **"Updating a key changes its name, scopes, and expiry while keeping the same secret."**
>
> **"The secret is returned once, on creation, and never again."** There is no call that reads it
> back.

Two consequences that decide which job you are doing:

1. **Extending an expiry propagates nothing.** The secret does not change, so no `.env`, no Actions
   secret, no box and no partner is touched. It is a console edit and it is finished.
2. **A new secret must be caught at creation** and then reaches every surface in §4 by hand. Miss
   one and §4 tells you which failure you get.

Also: creating long-lived keys through the Project API was **deprecated 2026-08-17**, and Appwrite
Cloud now blocks an API key from creating another key. **Long-lived keys are created in the console**
— which is to say, by the operator (seam contract §9; þing-01 **D4**: *"a console action no repo can
own"*). No agent can do this step.

### The order, and it is the order that was actually used

> **create the new key → repoint each holder → confirm each holder works → only then delete the old
> key.**

The old and new keys coexist through the middle steps, which is what makes stopping safe at any
point before the last one. **The delete is immediate and is the only irreversible step.**

**This is not a procedure invented for this document.** It is what was executed on 2026-10-20 (the
FAO split) and 2026-10-29 (the producer and server keys), across the surfaces in §4, successfully.
That is the strongest evidence this platform has about rotation, and it is why the step-by-step
detail is **not** restated here:

| For | Follow | Which is |
|---|---|---|
| the faoapi keys and anything shaped like them | `views-faoapi/deployment/KEY_SPLIT_AND_ROTATION_RUNBOOK.md` | 252 lines, executed 2026-10-20, with an undo for every step and the monitor-is-silently-broken trap called out |
| a partner key | `views-crafdapi/deployment/PARTNER_KEYS.md` | þing-04 **D7** / views-crafdapi#183 — issue, fence-check, warm, send, revoke |

A second copy drifts. Go to those; this document's job is §2, §3 and §4 — **which keys exist, who
holds each, and every place a value lives** — because that is the part no per-repo runbook can see.

### Two traps that have each cost a real outage

**A `200` does not mean the key works.** views-models **C-114** measured it against live Appwrite on
2026-08-02: a real key returned `200, total=461`; **a garbage key and an empty key both returned
`200, total=0`.** Listing files was the only call either surface made, so a dead credential was
indistinguishable from an empty bucket — and the verdict a human read was *"nothing landed lately"*,
which is unremarkable on a monthly cadence. The fix was to GET the bucket itself: **401 if the key is
rejected, 404 if the coordinate is wrong.** The generalisation is worth more than the incident: *an
empty result and a refused request are the same bytes unless something distinguishes them.*

**A `/health` 200 proves one scope, not three.** `views-crafdapi/deployment/RELEASE_RUNBOOK.md:358-362`:
`/health` exercises `buckets.read` only, so a key missing `documents.read` or `files.read` still
answers 200 there. The smoke tests (`views-faoapi/src/views_faoapi/smoke.py`,
`views-crafdapi/src/views_crafdapi/smoke.py`) are what exercise all three.

**And a corollary about scopes, measured the hard way.** During the 2026-10-29 rotation, a full
source trace of every SDK call site *and* an independent second analysis both predicted Appwrite's
modern namespaced scopes (`documentsdb.*`). **Both were wrong** — the server answered
`401 … missing scopes (["collections.read"])` and `(["documents.read"])`, because `appwrite==19.2.0`
still calls the legacy endpoints, so the **deprecated** scope names are the authorising ones and the
modern-looking ones are inert (views-faoapi#543). Seam contract §5.5 was corrected on the same
grounds a day later, independently. **Reading the code does not tell you which scope the substrate
will demand. Only the substrate does.**

## 6. What is still owed

| Item | Owner | By when | Tracked |
|---|---|---|---|
| **The faoapi box's env file.** þing-04 G2-1 closed every part of the key question but one: *"whether the FAO server box's env file holds one [of the retired keys]. The operator has a read-only check."* Blast radius is the smoke and warm-up path, not serving — views-faoapi is a pure proxy and its `_REQUIRED_APPWRITE_ENV_VARS` (`managers/api.py:146-155`) holds no key at all — but it is unresolved | operator | **before 2026-11-17 16:10**, after which the answer stops being recoverable from the box | [views-faoapi#568](https://github.com/views-platform/views-faoapi/issues/568) — carries the mtime screen and the value-free fingerprint comparison |
| **`pipeline-core-writer`'s `files.write` and `documents.write` are unproven.** Proving them needs a real producer write to the production store. The retained old key that could cover a missing scope **dies 2026-11-17**. After that, a missing write scope is fixed by a console scope edit, not a revert — `test_credential_expiry.py` says so, and says the fallback *"is a convenience with a deadline, not a dependency"* | operator | prove before **2026-11-17**, or accept knowingly | [views-postprocessing#332](https://github.com/views-platform/views-postprocessing/issues/332) |
| **`crafd-caller-read` has no expiry**, so nothing will ever force it to be reviewed (**C-66**). Both an expiry-with-renewal and a deliberate no-expiry are defensible; *only the absence of a decision is not*. Decide before `PRODUCTIONAPI_API_KEY` is issued, or the default propagates to a third external party by inheritance | operator | before the next external key | [views-appwrite#12](https://github.com/views-platform/views-appwrite/issues/12), **C-66** |
| **Scope counts and `faoapi-caller-fao`'s actual three scopes** — §2's caveats. One console sitting closes all of it | operator | opportunistic | [views-appwrite#12](https://github.com/views-platform/views-appwrite/issues/12); `faoapi-caller-fao`'s three at [views-faoapi#543](https://github.com/views-platform/views-faoapi/issues/543) |

> **Each row above is tracked somewhere a date can fire, added 2026-11-12.** Written in a
> table here, "still owed" is prose in a document nobody is obliged to re-read — the failure
> mode **C-85** exists to name. The two dated rows now have issues in the repositories that
> would feel them, filed because an unknown that is not tracked does not survive the session
> that found it. Neither issue asks for a code change: both are operator actions with a
> deadline, and the deadline is the point.

## 7. What this document is not

**It is not a rotation mechanism, and it does not close C-27.** Register **C-27** — *rotating a
secret value has no propagation mechanism* — stays open. There is no secret store, no
injection-at-launch and no per-process slots; §4 is a hand-maintained list, and the contract's §5.4
promise that *"replacing a key is a routine chore"* is still unearned. Seam contract §9 **O1** owns
the design task, views-appwrite#9 owns the issue.

What changed is the evidence: the 2026-10-20 and 2026-10-29 rotations were manual multi-surface
surgery and they **worked**, with one holder forgotten and caught (C-345). That is worth recording
and it is not a mechanism.

**It is not a second expiry tripwire.** `views-postprocessing/tests/test_credential_expiry.py`
already fires 30 days before the earliest expiry, has an acknowledgement escape so it cannot hold a
merge queue hostage, and is correctly maintained. Its own docstring names the alternative — *"a date
to act on, not a mechanism to build, and inventing a mechanism would be building the wrong thing to
feel busy."* A second one here would be exactly that.

**It does not touch þing-02 D4's sequence.** Probe a scoped key → issue tier keys → declare schema →
relocate `create_*` → narrow scopes is ratified and unchanged; none of it has happened, and
`APPWRITE_READ_API_KEY` / `APPWRITE_WRITE_API_KEY` / `APPWRITE_PROVISION_API_KEY` are still
`status = "planned"` in the registry. What happened in October is permitted by þing-02 **E5** —
*"FAO's key is reissued **like-for-like** (scopes unchanged); any dev/ops key produced by the split
is a scoped key and falls under D9's gate"* — and a like-for-like reissue is not a scoped key. The
split bought **revocability**, not least privilege. Narrowing is still owed, and
views-pipeline-core#489 records that it never happened.

---

*Non-normative companion to the [Appwrite Seam Contract](appwrite_seam_contract.md). If a statement
here conflicts with the contract, the contract wins and this document is wrong. If it conflicts with
the **console**, the console wins and both are wrong — that is the failure in §1.*
