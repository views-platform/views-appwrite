# Joining the Appwrite Seam — a checklist for a new consumer API

> **NON-NORMATIVE.** This document imposes no obligation that the [Appwrite Seam
> Contract](appwrite_seam_contract.md) or the þing-02 verdict does not already impose. Where it says
> *must*, it is reporting an obligation that lives elsewhere, and says where. It exists because the contract is
> what consumers pin, and the clone runbook lives in the þing record, which nobody pins — so a
> developer creating a new API had nowhere to read the steps. Nothing here needs ratification, and
> adding to it triggers no version bump.

**Who this is for:** you are creating a repository that reads from or writes to the shared Appwrite
store — `views-crafdapi`, `views-productionapi`, or whatever comes after them.

---

## 1. Pin the contract. Do this first, before the first push.

Reference the contract **by URL at a tag**, never at `main`:

```
https://github.com/views-platform/views-appwrite/blob/<TAG>/docs/ADRs/platform/appwrite_seam_contract.md
```

The current tag is recorded in the [repository README](../../../README.md). Read it from there —
this document deliberately does not carry a second copy of it, because a second copy goes stale and
then has to be trusted.

**Why this matters more than it looks.** A `/blob/main/` link is not a pin: it resolves to whatever
the contract says today. When the contract moved to v1.2.0, §5.7 was struck entirely — and
`views-datafactory`'s two credential guides, which linked to `main`, silently began describing rules
their authors had never read. Nobody was told. That is
[views-datafactory#393](https://github.com/views-platform/views-datafactory/issues/393).

A published tag is **never moved** (contract §10), so a tag you pin today means the same thing
forever. Moving to a newer version is then a deliberate act: read the diff, accept the changes,
repoint. That deliberate act is the entire point.

**You will be cloning a repo that gets this half right.** `views-faoapi` *does* pin — at
`docs/ADRs/README.md:156`, to a full commit sha — but it pins the **registry**, not the contract, and
that sha is **v1.0.0**: two versions behind, and stale since before either amendment. The contract
itself it cites by name, with no link. Both halves are worth not inheriting: pin the contract too,
and pin something you intend to re-read.

## 2. Declare your slots in the registry — before your repo exists

Your coordinates and your credential slot belong in
[`coordinate_registry.toml`](coordinate_registry.toml), not in your repo.

- **Coordinates** — bucket and collection ids and names. Declared with `status = "planned"` until the
  operator sets the values in the console. Slots for `views-crafdapi` are already there.
- **One credential slot, yours alone.** Contract §5.3's floor: *no key is held by two parties who
  could need revoking separately.* A new external party may not share FAO's key, and two new APIs may
  not share each other's.

This is **free at creation and a coordinated migration afterwards**, which is the whole reason to do
it now. A repo that finds no slot invents one locally, and local invention is the pathology the
registry exists to remove.

**Do not invent placeholder values.** A plausible-looking id that later gets used verbatim is a named
hazard on this platform — see `C-21` and `C-228`, where a wrong bucket coordinate silently provisions
new production storage instead of failing.

## 3. Do not import `views_pipeline_core.modules.{appwrite,datastore}`

Write your own thin client against the SDK, as `views-faoapi` did.

This is not a style preference. `views-postprocessing` imports that client, and that import is how a
two-repo defect became a three-repo defect. Duplication is the deliberate choice here — **WET before
DRY** — until a shared implementation is extracted under its own trigger.

What you consume instead:

| | |
|---|---|
| The **coordinate registry** | read by path as pinned data — that is shared *data*, not a shared *implementation*, and creates no dependency edge |
| The **conformance vector** | a shared *test* you run against your own copy (see §4) |

## 4. Run the conformance vector against your own copy

Once it exists ([#13](https://github.com/views-platform/views-appwrite/issues/13)), it asserts one
invariant that every independently written client must satisfy:

> Two distinct callers never share a cache partition, and a partition label is neither the key value
> nor derivable from it.

Pass/fail: two distinct keys yield two distinct partitions; the label cannot be derived from the key
value; a request bearing key A never serves content cached for key B.

**It does not exist yet** — it is blocked on `views-faoapi#323`, and must be authored from the
post-salt implementation. Written earlier it would encode the current fused behaviour as the
reference, and every clone would conform to the bug.

## 5. Turn on scanning and push protection at creation

Before the first push, not after. Retrofitting is what this platform is doing now, and it is worse.
Include `secret_scanning_non_provider_patterns` and `.ipynb`-cell scanning — those two flags each
catch a class of real finding already present in this platform's history that the defaults miss.

## 6. Then read the full runbook

The remaining preconditions — including the two that **gate the clone itself** — are in the þing-02
verdict, `§III` of:

```
views_platform/þingit/02_credential_identity_key_ownership/orð_dómr.md
```

They are not restated here. A second copy drifts, and this platform has spent two assemblies learning
that. Go there for the reasoning; the steps above are the ones you can act on without it.

**The two that gate the cut**, so you are not surprised by them:

1. The value in `views-faoapi`'s git history must be classified first — `git clone` copies all
   history, so cloning before that resolves replicates the incident rather than moving it.
2. `views-faoapi#322` must ship first. Its client deletes metadata on any `get_file` failure,
   including *"the key lacks read scope"*. That path is dead in faoapi **only because nothing calls
   it** — not because anything guards it — so it comes alive in any clone that adds a write route.
   `views-productionapi` is a write API by definition.

---

*Non-normative companion to the [Appwrite Seam Contract](appwrite_seam_contract.md). Added
2026-07-31 (issue #19). If a step here conflicts with the contract, the contract wins and this
document is wrong.*
