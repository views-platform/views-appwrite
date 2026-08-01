# Conformance vector — cache-partition isolation

**Version 1.0.0** · authored 2026-08-01 against `views-faoapi` v1.4.0 (post-salt)
**Artifact:** [`conformance_vector_cache_partition_isolation.py`](conformance_vector_cache_partition_isolation.py)
**Governed by:** [the Appwrite Seam Contract](appwrite_seam_contract.md) §5.8 · þing-02 **A4**, as amended by `dómr_endurmat` **E3**

---

## Why this exists

The platform runs **several independently written Appwrite clients** rather than one shared
implementation. That is deliberate — WET before DRY, and there is live evidence behind it:
`views-postprocessing` imports `views-pipeline-core`'s client, and that import is how a two-repo
defect reached a third repo.

Copying the code is accepted. **Letting the isolation guarantee drift silently across the copies is
not.** This vector is the difference between those two things.

## The invariant

> **Two distinct callers never share a cache partition, and a partition label is neither the key
> value nor derivable from it.**

Three ratified criteria, and the file tests all three:

| | Criterion | Tests |
|---|---|---|
| **(i)** | two distinct keys yield two distinct partitions | 4 |
| **(ii)** | the label cannot be derived from the key value | 3 |
| **(iii)** | a request bearing key A never serves content cached for key B | 3 |

Criteria (i) and (iii) each gained a **survives-a-restart** test beyond the ratified minimum.
Isolation that holds only in memory is not isolation, and a partition label that changes on restart
means the server-side secret was never persisted — which reads as a cache-miss problem while
actually being an isolation defect.

## The defect it was written against

`views-faoapi` labelled its on-disk cache partitions `sha256(x_api_key)[:16]` — a one-way
fingerprint of the caller's key. One-way is not enough: **anyone holding the key can compute the
label**, so anyone who can list the cache directory learns which partition belongs to whom, and
rotating a caller's key silently orphans that caller's entire cache.

The fix (`views-faoapi#323`, shipped in v1.4.0) introduces one **server-side salt** —
`.partition_salt`, 32 random bytes, write-once, file-locked — and labels partitions
`hmac_sha256(salt, api_key_hash)[:16]`.

**The ordering mattered and was ratified.** This vector had to be authored *after* that fix. Written
before it, criterion (ii) would have been written against the fused behaviour, and every clone
would have conformed to the bug.

## How to adopt it — copy, do not import

1. **Copy** the `.py` file into your repo's test suite. Rename it to `test_*.py`.
2. **Implement `CachePartitionAdapter`** — four methods, roughly twenty lines. A reference binding
   for views-faoapi is in the class docstring.
3. **Override the two fixtures**: `adapter`, and `other_adapter` over a *different* cache directory
   so it holds a different secret.
4. **Record the `VECTOR_VERSION`** you ran against.

**Do not add `views-appwrite` as a dependency.** Copying a test creates no dependency edge; importing
one does. That distinction is what keeps this compatible with §5.8 and keeps this repo parked — and
it is the same rule the contract applies to itself.

## It was run before it was published

A conformance vector nobody has executed is the thing þing-02's own review called *"the token that
lets a parked seat stay parked."* So it was validated against two reference implementations before
shipping — the post-salt scheme, and the pre-fix scheme it replaced.

| Run against | Result |
|---|---|
| **Fixed** — `hmac(server_salt, key_hash)[:16]`, faoapi v1.4.0 | **10 / 10 pass** |
| **Broken** — `sha256(key)[:16]`, the pre-#323 defect | **2 fail**, and exactly the two criterion-(ii) tests |
| **Bare copy, fixtures not supplied** | **10 errors** — loud, never a silent skip |

The discrimination is precise and worth stating: under the broken scheme, criteria **(i)** and
**(iii)** still pass — `sha256` *is* deterministic and distinct per key, so the unsalted scheme
genuinely isolates callers. What it fails is only **(ii)**: the label leaks *which partition belongs
to whom* to anyone holding the key. The vector catches the real defect without over-claiming that
everything was broken.

**Running it also found a defect in the vector itself.** The two fixtures were originally stubbed
inside the file. A fixture defined in a test module shadows one from `conftest.py`, so a consumer
could not have overridden them without editing the vector — and the stubs called `pytest.skip`, so
an unadapted copy would have reported a **green run for a client that was never tested**. They are
now required from `conftest.py`, and their absence errors loudly. That failure mode was invisible on
inspection and took thirty seconds to find by execution.

## The test that actually decides it

`test_ii_label_depends_on_a_server_side_secret` is the load-bearing one. It computes the label for
the same key under **two different deployments** and requires them to differ.

If they match, the derivation contains no secret and criterion (ii) fails — regardless of how clever
the label looks. Every other (ii) test enumerates *known* bad derivations; this one catches the ones
nobody thought of.

## What this does not guard

**This invariant, and nothing else.** It does not stop three independently written clients diverging
in any other respect — pagination, error taxonomy, retry behaviour, provisioning semantics.

That residual is real, unpriced, and recorded as **þing-02 Ó-7**: *three thin clients are a cost that
nobody has costed; the alternative has live evidence against it and no pricing in the record at all.*
It is the standing question for þing-01 **D8**'s trigger, not something this file resolves. Read as
coverage of the isolation guarantee only.

## Known gap: nothing forces a re-run

The vector and the clients that run it are **reused together but released separately**. Change this
file and three copies drift, with nothing triggering a re-run.

Recording the `VECTOR_VERSION` per repo is what makes that visible rather than silent. It is a
mitigation, not a fix — the underlying REP violation is registered as **C-38** and left open rather
than papered over.

## Consumers

| Repo | Status |
|---|---|
| `views-faoapi` | `#324` — the reference implementation runs it against its own copy |
| `views-crafdapi` | at birth, per [`joining_the_seam.md`](joining_the_seam.md) §4 |
| `views-productionapi` | at birth |

## Changing this vector

It is **not contract text** and carries no version of the contract — it may change without a
contract version bump. But a change that tightens a criterion invalidates every recorded
`VECTOR_VERSION`, so bump this file's version and say what changed, or the recording mechanism
above is worthless.
