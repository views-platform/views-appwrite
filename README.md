# views-appwrite

**Home of the VIEWS platform's cross-repo contracts** — the Appwrite seam (identity, secrets and
shared coordinates) and the consumer-API strategy that governs how those repos are built and
deployed. **Six repositories reference these documents** — views-models, views-pipeline-core,
views-faoapi, views-crafdapi, views-postprocessing and views-datafactory (counted 2026-08-13).

> **The name is narrower than the charter, deliberately for now.** Operator decision, 2026-08-05:
> this repo owns platform contracts *and* consumer-API strategy, not the Appwrite seam alone — *"maybe
> we'll shuffle around responsibilities in the future, but for now this seam is the lesser of a bunch
> of evils."* Recorded as provisional so it does not harden into permanence by repetition.

> **Public since 2026-08-08.** History was scanned before the flip, not after —
> `.github/workflows/secret_scan.yml` walks every non-merge commit and the exit code is the
> verdict. What "green" guarantees is written in [`.gitleaks.toml`](.gitleaks.toml), including
> what it does **not** cover. `main` and `development` are protected by a ruleset requiring a PR
> and a passing scan; branch protection was impossible while the repo was private, so going
> public is what made it enforceable.
>
> **Three workflows run on every pull request, and three checks are required to merge.**
>
> | Workflow | Job | Required? |
> |---|---|---|
> | `secret_scan.yml` | `gitleaks (full history)` | **yes** |
> | `guards.yml` | `guards (self-contained)` — registry-shape invariants + `validate_docs.sh` | **yes** |
> | `guards.yml` | `guards (cross-repo)` — the canonical readers still agree | **yes** |
> | `falsification.yml` | `falsification (reporting only)` | **no, deliberately** |
>
> The guards protect the registry's live invariants: that a value-less `[target]` entry kills every
> reader (C-29), that no secret carries a value, and that the contract and registry cannot change
> without their versions moving (C-53). **Each was made required only after being watched fail for
> the reason it exists** — mutated, observed red in CI, reverted, recorded (#71, epic #66).
> A guard nobody has watched fail is decoration.
>
> The falsification job is **excluded from the required set on purpose**: its stubs are red by
> design, so blocking on them would make deleting one the fastest way to ship. It reports instead,
> and shouts when a stub turns green.

> **This repository ships no code today — and that changed status on 2026-11-17.**
>
> There is no `src/`, no `pyproject.toml`, no package to install or import. Until 2026-11-17 that
> was a recorded decision to **stay parked**; it is now a recorded decision to **start**, with the
> code not yet written. The shared Appwrite client's trigger **T3 fired** — see
> [Current posture](#current-posture).

**What is live now:**

| | |
|---|---|
| [The seam contract](docs/ADRs/platform/appwrite_seam_contract.md) | Identity, secrets and configuration on the Appwrite seam. Formerly `PLATFORM-001`, renamed by [ADR-011](docs/ADRs/011_naming_of_cross_repo_contracts.md) |
| [The deployment pattern](docs/ADRs/platform/consumer_api_deployment_pattern.md) | How a consumer API reaches production: registry-sourced coordinates, operator-slot secret, **a box that records which registry version built it**, tag-gated deploys, fail-visible serving. Repo-agnostic; each consumer's concrete ADR references it by pinned tag |
| [The key inventory](docs/ADRs/platform/key_inventory_and_rotation.md) | Which Appwrite keys exist, who holds each, when each expires and **every surface that holds a key value** — keyed by console key, because one variable name holds four different keys. Non-normative; added after this repo's own inventory went three weeks stale (C-85) |
| **How to pin** | Pin an `appwrite-seam-v*` tag — **[the newest is on the releases page](https://github.com/views-platform/views-appwrite/tags)**, and this README deliberately does not name one (see below). The deployment pattern is versioned **separately** at **v1.0.2**; pin it independently, because the two change for different reasons. `platform-001-v1.2.0` is retained and still resolves — §10 forbids moving a published tag |
| [The coordinate registry](docs/ADRs/platform/coordinate_registry.toml) | The canonical source for every bucket, collection and database id on the seam, plus named secret slots — **never secret values** |

> **Are you still conformant? Compare against the floor, not the newest tag.**
>
> The registry carries `[meta] obliges_consumers_since`. Most editions ask nothing of you — of the
> **seventeen** published so far, **three oblige a consumer and fourteen do not** (counted from the
> registry's `[edition.*]` table, 2026-11-17; this page said *"eleven… three and eight"* while five
> more shipped, which is **C-76** again on the same page that names it). So:
>
> ```
> conformant  ⟺  your_pin >= obliges_consumers_since
> ```
>
> An observation-only bump moves `[meta] version` and leaves the floor still; you stay green. When a
> row appears that asks something of you, the floor rises and you go red **with something to do** —
> the only thing a red build should ever mean. Every edition declares which it is, in
> `[edition."x.y.z"].obliges_consumers`. See seam contract **§10.1**.
>
> **Why this README no longer names a specific tag:** it named `appwrite-seam-v1.4.4` for seven
> editions after that stopped being current, and every gate here stayed green throughout. A number
> on this page is a claim nothing checks. Registered as **C-76**.
---

## Current posture

> **Contract home: live. Code: activated 2026-11-17, not yet written.**

**What is live here** is everything in the table above: the seam contract, the coordinate registry,
and the deployment pattern. Six other repositories reference them **by URL at a pinned tag**.
Changes come by supersession and a version bump, never by silent edit (§10).

**What is no longer parked** is a shared Appwrite client library. There is still no `src/` and no
`pyproject.toml` — nothing has been written — but the deferral ended on **2026-11-17** when trigger
**T3** fired and the operator activated Phase 1.

**What fired it.** Appwrite 1.8 renamed the Databases API to TablesDB, and a key created in the
console after that rename cannot call the old endpoints at all (measured by views-crafdapi,
2026-11-13). The fix was applied in views-crafdapi and is still owed in four other repositories —
**21 files across five repositories import the Appwrite SDK directly**. T3 is written as *"a bug fix
that must be applied to both copies… a silent upload failure discovered in one copy and must be
fixed in both"*, and under views-pipeline-core's ADR-047 a refused read can leave the run exiting 0.
So it is T3's own named failure mode, at five copies rather than two.

**No consumer is obliged by this.** Nothing moves `obliges_consumers_since`; a repository adopts the
package when it chooses to. And nobody waits for this repo: views-pipeline-core's narrow TablesDB
fix goes first, so Phase 1 extracts code that is already correct.

→ **[The roadmap](docs/roadmap_shared_client.md)** — the full extraction plan and its decision log.
Start with **[Phase 1 as activated](docs/roadmap_shared_client.md#phase-1-as-activated-2026-11-17)**
and **Decision Log #12**: the older plan below them was written for two consumers and one SDK
generation, and its sequencing and cost are superseded.

Hosting a document creates no dependency edge on this repo's code maturity. That is precisely why
the seam's contract lives in the platform's only leaf that depends on nothing.

## Joining the seam

Building a new consumer API? → **[`joining_the_seam.md`](docs/ADRs/platform/joining_the_seam.md)** —
a non-normative checklist, in order, starting with pinning the contract before your first push.

## How this repository governs itself

| | |
|---|---|
| [ADRs 000–011](docs/ADRs/) | The constitutional decisions — declarations over inference, fail-loud, testing as infrastructure, naming of cross-repo contracts |
| [Contributor protocol](docs/contributor_protocols/carbon_based_agents.md) | The working agreement, including the **definition of done** and the rule this repo was built on: *a guard is not finished until it has been shown to fail* |
| [Risk register](reports/technical_risk_register.md) | Every known concern, tiered, with its trigger. Open findings are listed with the argument for accepting them, not just the fact of them |
| [`docs/validate_docs.sh`](docs/validate_docs.sh) | Nine checks, run on every pull request |

**What the guards do not cover** is stated as plainly as what they do: `views-faoapi` is private, so
the cross-repo reader comparison sees **two of three** canonical readers (C-51), and the secret scan
misses prose and notebook placements on this plan (C-67, C-30). An absence stated is an accepted
gap; an absence unstated is a blind one.
