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

- **Coordinates** — bucket and collection ids and names. Reserve them in the **`[planned]`** table,
  with `status = "planned — …"`, until the operator sets the values in the console; then they move to
  `[target]`. **The table matters more than the marker**: readers scan `[connection]` and `[target]`
  only, and they no longer agree on what a marker means (views-models skips such an entry and emits a
  partial coordinate set; the other two raise — C-51/D-05). A reservation left in `[target]` is
  therefore either a platform-wide outage or a silent partial delivery, depending on who reads it.
  The registry's own header block spells this out; read it before adding anything.
  `views-crafdapi`'s four slots were reserved this way and graduated to `[target]` on 2026-08-02.
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

It exists. Two files, in the directory you are already reading:

| File | What it is |
|---|---|
| `conformance_vector_cache_partition_isolation.py` | 10 tests, `VECTOR_VERSION 1.0.0` |
| `conformance_vector.md` | the spec, and how to adopt it — **start here** |

Copy the vector into your own suite and supply the `adapter` and `other_adapter` fixtures. **A bare
copy errors with 10 errors** — that is documented behaviour, not a defect: it fails loudly rather
than skipping silently. It was validated against two reference implementations before publication.

It asserts one invariant that every independently written client must satisfy:

> Two distinct callers never share a cache partition, and a partition label is neither the key value
> nor derivable from it.

Pass/fail: two distinct keys yield two distinct partitions; the label cannot be derived from the key
value; a request bearing key A never serves content cached for key B.

> **Corrected 2026-11-12 (views-appwrite#169).** This step previously read *"It does not exist
> yet — it is blocked on `views-faoapi#323`, and must be authored from the post-salt
> implementation."* **Both halves had been false since 2026-08-01:** the vector shipped that day in
> `47172af` (views-appwrite#13, closed COMPLETED) and sits two files away in this directory;
> views-faoapi#323 closed 2026-08-18 and its reference run, faoapi#324, on 2026-08-12. The ordering
> the struck sentence protected was honoured, so the sentence has served its purpose.
>
> **Why this mattered more than a stale line.** This file is the checklist a new consumer follows,
> and a step that says its own artifact does not exist is a step that gets skipped — which is the
> one outcome the vector exists to prevent, since its invariant is that two callers never share a
> cache partition. views-crafdapi#22 was open in exactly that position while this sentence stood.
>
> **Why nothing caught it.** `validate_docs.sh` reads no prose claim about whether a sibling file
> exists, and that guard is deliberately not being built — a checker that parses English
> assertions is a bad trade, and views-pipeline-core built one on 2026-11-12 and deleted it the
> same hour after three false positives (negation, qualification, quotation; their C-355). What
> *is* mechanical is the citation: the two issue numbers in the struck sentence were both closed,
> and *"every issue a governed document cites as blocking is still open"* needs no prose parsing
> and would have caught this on the day faoapi#323 closed. Not built here either, and tracked
> rather than assumed — see #169. The sentence survived an edit to its own file on 2026-08-15
> (`1839109` inserted a new §5 and renumbered below it) without anyone reading §4.

## 5. Close your collection and bucket permissions — before the first delivery

Every Appwrite container you create must end up with an **empty permission list**:

```
permissions: []          # on the collection AND the bucket
documentSecurity / fileSecurity — leave alone
```

**An empty list is not "no access".** A server API key bypasses container permissions entirely, so
`[]` means *only key-holders*, which is what you want. `crafd` has served at `[]` throughout while its
delivery read and wrote it under the datastore key — that is the proof, not an exception.

Check it, do not assume it:

```
views-models/tools/credentials/close_resource_permissions.py     # dry-run by default
```

Expected result: an anonymous request carrying only the project id returns **401**; the same request
with the key returns your rows.

**Why this step exists.** On 2026-08-14 two production collections were found granting
`read/create/update/delete("any")` — readable *and writable* by anyone with no credentials, 572 rows
in total. The tooling that created them defaulted to that grant while the sibling bucket call beside
it defaulted to `[]`. See **C-83** in this repo's register, and views-pipeline-core's **ADR-061** for
the target state. **A bring-up that follows every other step here can still produce an open
collection**, which is exactly why this one is not optional.

## 6. Turn on scanning and push protection at creation

Before the first push, not after. Retrofitting is what this platform is doing now, and it is worse.
Include `secret_scanning_non_provider_patterns` and `.ipynb`-cell scanning — those two flags each
catch a class of real finding already present in this platform's history that the defaults miss.

## 7. Then read the full runbook

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
