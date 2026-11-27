# How to Tell Whether a Boundary Holds

**A working document. Not a decision record.** Nothing here obliges anyone to anything. It is a
catalogue of tests — things you can actually run against a repository to find out whether its
boundary with a vendor is real — together with what each test has said so far.

**Status:** open and expected to grow. Started 2026-11-25.

---

## What this is for

The effort this document serves is the one in `what_we_learned.md`: getting Appwrite out of the
repositories that contain it and behind a single boundary. ADR-012 is the decision record.
`what_we_learned.md` records what the literature says, one book at a time. **This document records
how to check the code**, because reading a book tells you what a good boundary looks like and tells
you nothing about whether yours is one.

Each test below says what it asks, how to run it, what it costs, and — most importantly — **what it
cannot tell you.** A test whose limits are not written down will eventually be trusted past them.
One already was, and it is the first entry for that reason.

**On the results recorded here.** Every result dated 2026-11-24 was measured that day and is
reproduced here from `ADRs/012_the_appwrite_gateway.md`. None has been re-run since. Treat a result
as good until the code moves, then re-run it; the commands are given so that re-running is cheap.

---

## 0. Count the vendor's nouns in the code — a failed instrument, kept as a warning

**What it asks.** Is the code written in the vendor's vocabulary? Measured by how often the vendor's
words appear outside the module that is supposed to contain them.

**How it was run.** Counted lines containing `bucket` outside each repository's Appwrite module.

**What it said, 2026-11-24.** 92 lines in 8 files in views-faoapi, 40 in 6 in views-crafdapi, 32 in 2
in views-pipeline-core, 38 in 8 in views-postprocessing — which has no Appwrite module at all. 202
lines across 24 files in four repositories. On this count
`views_pipeline_core/modules/datastore/datastore.py` was the worst single file at 26 hits, and the
conclusion drawn was that the shared abstraction is written in Appwrite's language.

**Why it was wrong.** Reading the file disproved the conclusion. Almost every hit was a docstring, a
comment, or a reference to a private attribute. **No public signature in that file takes a bucket.**
The abstraction's vocabulary was fine; the word count could not see the difference between a name in
an interface and a name in a comment.

**What this test cannot tell you.** Anything. Word frequency does not measure a boundary, because a
boundary is a property of signatures and imports, and a text search weights a docstring exactly as
heavily as a parameter. It is recorded here so that the next person who thinks of it can skip it.

**What to run instead.** Test 1.

---

## 1. Read every public signature

**What it asks.** Of the names and types that cross the boundary, which belong to the business and
which belong to the vendor? This is the test that the word count was a poor proxy for.

**How to run it.** List the public methods or routes of the component. For each, read the name, every
parameter and the return type. Ask of each name: is this a word the business uses, or a word the
vendor uses?

**Cost.** An hour for a component the size of `DatastoreModule`. Not automatable — it is a reading
task, and the judgment is the point.

**What it said, 2026-11-24.** `views_pipeline_core/modules/datastore/datastore.py`, 771 lines,
twelve public methods: `upload_predictions`, `upload_data`, `get_predictions_by_metadata`,
`download_prediction`, `get_latest_file_id`, `download_latest_file`, `get_file_metadata`,
`update_prediction_metadata`, `delete_prediction`, `list_all_predictions`,
`list_all_predictions_unfiltered`, `to_dict`. All twelve are named in forecast terms. No bucket
appears in any signature.

**And the finding that mattered.** Three of the twelve pass a vendor-issued identifier:

```
def get_latest_file_id(self, filters) -> Optional[str]
def get_file_metadata(self, file_id: str) -> OperationResult
def delete_prediction(self, file_id: str) -> OperationResult
```

The abstraction hides *where the file sits*. It does not hide *the vendor's name for the file*.

**What this test cannot tell you.** Whether a parameter typed `str` is carrying a vendor identifier.
`file_id: str` looks clean. Only the docstring at
`views_pipeline_core/modules/appwrite/file.py:308` says what that string is. For that, use test 2.

---

## 2. The primitive-identifier census

**What it asks.** For every identifier that crosses the boundary: **who issued this value, and could
anything other than the vendor have issued it?**

**Why it needs its own test.** A dependency carried in a `str` or an `int` is invisible to every
check that can be automated. No import of the vendor is needed to declare it. A search for the
vendor's name does not return it. A type checker accepts it. The knowledge that makes it a
dependency lives in a parameter name and a docstring. Ousterhout §4.2 is explicit that the informal
part of an interface is *"not specified in a way that can be understood or enforced by the
programming language"* — this test is the manual substitute for the enforcement that cannot exist.

**How to run it.** For each public signature crossing a repository boundary, list every parameter and
return value typed `str`, `int` or `bytes` whose name suggests an identifier — `_id`, `_key`,
`_handle`, `_name`, `_path`. For each one, answer the question above in writing. An identifier the
business issues (a run name, a level, an outcome, a content hash) is fine. One the vendor issues is
the finding.

**Cost.** Half a day per repository. Mostly judgment. Not automatable, and the attempt to automate it
is test 0 all over again.

**What it has said so far.** Not yet run as a census. The three signatures in test 1 were found
incidentally, which is not the same as having looked. **Not run on any repository.**

**What this test cannot tell you.** Whether a vendor identifier that is being passed around has
escaped into stored or published state. For that, follow each one found: is it written into a
metadata record, a log, a cited URL, a bookmark? `fileId` is a required field of
`FIXED_METADATA_ATTRIBUTES` in `views_pipeline_core/modules/appwrite/provisioning.py`, so in this
platform at least one of them has.

---

## 3. The import-direction test

**What it asks.** Which source files have to name the vendor in order to compile or import? This is
the dependency arrow, measured directly rather than inferred from a diagram.

**How to run it.**

```bash
grep -rln "^from appwrite\|^import appwrite\|from appwrite\." --include=*.py .
```

Then read each file returned and ask one question: **does this file also contain a forecasting
decision?** Every hit should be in an adapter directory or in the one file that wires the program
together. A hit in a file that also decides something about forecasts means the dependency has not
been inverted there, whatever the structure diagram says.

**Cost.** One command plus reading a dozen files. Under an hour.

**Use this grep, not the one above.** **Corrected 2026-11-27.** The pattern as first written
over-reports badly, because it matches any import whose module path merely contains the vendor's
name. Three repositories here have first-party modules called `appwrite_env`, `appwrite_api` and
`appwrite_manager`, and the loose pattern counts those as vendor coupling. Anchor it instead:

```bash
grep -rln "^\s*from appwrite[. ]\|^\s*import appwrite$\|^\s*import appwrite\." \
  --include=*.py . | grep -v "/envs/\|site-packages"
```

**What it said, 2026-11-27. Fact, checked that day across seven repositories.**

| repository | files importing the SDK |
|---|---|
| views-pipeline-core | **17** |
| views-faoapi | **11** |
| views-crafdapi | **6** |
| views-postprocessing | **0** |
| views-models | **0** |
| views-datafactory | **0** |
| views-appwrite | 0 (ships no code) |

**Three repositories, 34 files. Not six repositories, and not five.** views-postprocessing,
views-models and views-datafactory name Appwrite in comments, documentation and *their own module
names*, and import the SDK nowhere. They already reach the store through views-pipeline-core.

**This corrects the plan of record.** `docs/roadmap_shared_client.md`, under "Phase 1 as activated",
states *"five repositories import the `appwrite` SDK directly — 21 files: views-crafdapi 5,
views-faoapi 5, views-pipeline-core 7, views-postprocessing 2, views-models 2"*, checked
2026-11-17. Two of those five import only first-party modules whose names begin `appwrite_`. The
true scope is **smaller in repositories and larger in files** than the roadmap assumes, and two
repositories it schedules for migration need none.

**What this test cannot tell you.** Anything about identifiers carried as primitives — a file with no
vendor import can still be handing out vendor handles. Tests 2 and 3 are complementary and neither
replaces the other. It also says nothing about *how much* of the vendor each file uses, which is
test 11.

---

## 4. The deployability test

**What it asks.** Can the business half be built and imported with the vendor's SDK absent? Martin
treats this as the defining property of a full architectural boundary: *"independently compilable and
deployable components."* It is the strictest clause in his description and the only one with a yes-or-no
answer.

**How to run it.** In a clean virtual environment, install the repository without the Appwrite SDK,
then import its top-level package and its business modules. If the import raises, the boundary is not
full, and the traceback names the file where it stops being full.

**Cost.** About an hour per repository. Fully mechanical. Cheapest decisive test in this document.

**What it has said so far.** **Not run on any repository.**

**What this test cannot tell you.** How bad the failure is. An import error in one adapter module is
a different situation from an import error in a business module, and the test reports both as
failure. Read the traceback, do not just read the exit code. It also says nothing about identifiers:
a repository can pass this test cleanly and still hand out vendor handles.

---

## 5. The substitution test

**What it asks.** Can a fake store be put in the real one's place? This is the payoff Hohpe & Woolf
actually claim for a Messaging Gateway — that it can be tested against a Service Stub — so it tests
the premise ADR-012 is built on rather than its wording.

**How to run it.** Write a stub that satisfies the store interface and returns canned forecasts.
Wire it in. Run the existing test suite. Three possible outcomes, and all three are informative:
the suite passes, and the seam is real; the suite fails, and the failures name what the stub did not
reproduce; or **the stub cannot be wired in at all**, which means there is no seam to substitute at
and is the most useful result of the three.

**Cost.** A day per repository, and the stub is reusable afterwards.

**What it has said so far.** **Not run.**

**What this test cannot tell you.** Whether the real vendor behaves as the stub does. It tests the
shape of the boundary, not the fidelity of anything behind it.

---

## 6. Shared literals across the line

**What it asks.** Is the same design decision encoded independently on both sides of the boundary?
Ousterhout §5.2 calls this back-door information leakage and notes that it is *"more pernicious than
leakage through an interface, because it isn't obvious."*

**How to run it.** Extract every identifier-like string literal from the writing side and from the
reading side. Intersect the two sets. Discard the coincidences — `data`, `name`, `type` — and read
what is left.

**What it said, 2026-11-24.** 73 literals appear on both sides. Two clusters were real.

*The vendor's error vocabulary, hard-coded in three repositories.*
`views_pipeline_core/modules/appwrite/file.py:134-135` names
`storage_file_not_found` and `storage_bucket_not_found` as constants, correctly;
`views-faoapi/src/views_faoapi/managers/appwrite/manager.py:407,415` re-encodes the same two strings
as inline literals; `collection_not_found` appears in the retry logic of both. A vendor rename
reaches every repository holding these — which is the October TablesDB rename in miniature.

*The metadata record's field names.* Smaller than first reported. views-pipeline-core does declare
its half in `provisioning.py`, and views-postprocessing concentrates its knowledge of the shape in
`contract/store_metadata.py`, whose docstring says *"This is the only place that knows that shape"* —
which is §5.2's prescribed remedy, applied before anyone here had read the book. What is missing is
the contract's cross-reference to that declaration, not the declaration.

**What this test cannot tell you.** Which direction the knowledge flowed, or which side should own
it. It finds duplication; deciding where the single copy belongs is a separate judgment.

---

## 7. Change coupling from version control

**What it asks.** Do the two sides of the boundary actually change at different rates and for
different reasons? This turns "draw the line where things change for different reasons" from a
slogan into a measurement.

**How to run it.** For each commit touching the repository's source, record which files changed.
Count how often the vendor-facing files change alone, and how often they change in the same commit as
something outside them. Compare the commit count of the busiest business file with the commit counts
of the vendor files.

**What it said, 2026-11-24.** views-faoapi only. 234 commits touched `src`. The store client was
touched in 37 of them: 15 stayed inside the Appwrite module, 22 changed something outside it as well.
`managers/api.py` had 86 commits; the Appwrite files had 24, 9, 4, 4, 4, 2, 2 and 2. Roughly a
tenfold difference in churn rate across the line, which is the pattern the slogan predicts.

**A caution that cost something.** The median commit count was 2.0 on both sides. Taken alone it
says the two sides change at the same rate, which is the opposite of what the distribution shows.
The median was the wrong statistic and nearly produced the wrong conclusion.

**What this test cannot tell you.** Anything about two repositories that are deliberate copies of
each other. An attempt to compare views-faoapi with views-crafdapi after their 2026-08-02 split
produced five leaking commits per side — too small a sample to support any claim about drift, and
reported as inconclusive. **views-pipeline-core and views-postprocessing have not been measured.**

---

## 8. Interface width per consumer

**What it asks.** Of the operations the component offers, how many does each consumer actually use?
Ousterhout's deep-module argument says the cost of a component is its interface and the benefit is
its functionality, so an interface wider than any caller needs is paying cost for nothing.

**How to run it.** For each consumer repository, grep for calls to each public method of the shared
component. Tabulate consumer against method.

**Cost.** An hour or two. Mostly mechanical.

**What it said, 2026-11-25. Fact, checked that day across fifteen repositories in
`views_platform`.** Searched every `.py` file for a call to each of `DatastoreModule`'s public
methods, with docstrings and comments stripped, vendored virtualenvs under `views-models/envs/`
excluded, and `to_dict` dropped from the analysis because the name also belongs to pandas, torch and
xarray and cannot be attributed. That leaves eleven store operations.

**Five of the eleven are called from production source. Six are not.**

| operation | called from production source by |
|---|---|
| `upload_data` | views-pipeline-core (3 files), views-postprocessing (2) |
| `get_predictions_by_metadata` | views-faoapi, views-crafdapi, views-postprocessing (2) |
| `download_prediction` | views-faoapi (2), views-crafdapi (2), views-postprocessing (2) |
| `get_latest_file_id` | views-faoapi (2), views-crafdapi (3), views-postprocessing (2) |
| `get_file_metadata` | views-postprocessing (2) only |
| `upload_predictions` | **nothing — 9 test files only** |
| `download_latest_file` | **nothing — 2 test files only** |
| `update_prediction_metadata` | **nothing — 2 test files only** |
| `delete_prediction` | **nothing — 4 test files only** |
| `list_all_predictions` | **nothing — 2 test files only** |
| `list_all_predictions_unfiltered` | one audit tool, `views-models/tools/audit/verify_shelf_copy.py` |

**Three findings, in order of how much they decide.**

*The five-method store port is not a subset. It is the union.* The live set is exactly
`upload_data`, `get_predictions_by_metadata`, `download_prediction`, `get_latest_file_id`,
`get_file_metadata` — which is precisely what
`views-postprocessing/views_postprocessing/{unfao,crafd}/store_port.py` already declares. ADR-012's
"Still open — what operations it offers" names that port as one of two candidate shapes. It is not a
candidate; it is the measured answer. **The gateway needs five operations.**

*The reading side needs three.* views-faoapi's own source calls `get_predictions_by_metadata`,
`download_prediction` and `get_latest_file_id`, and nothing else. views-crafdapi calls the same
three. `get_file_metadata` is used only by views-postprocessing, and `upload_data` only on the
writing side. So the two repositories where the duplication actually lives need three operations
between them.

*Every one of the eleven is implemented three times.*
`views-faoapi/src/views_faoapi/managers/prediction/manager.py` and
`views-crafdapi/src/views_crafdapi/managers/prediction/manager.py` each define all eleven, as does
`DatastoreModule`. So each API maintains an eleven-operation store client in order to call three of
them, and six operations that no production code path anywhere calls are maintained in triplicate.

**What this test cannot tell you — and these caveats matter more than usual here.** *Test-only is not
the same as unnecessary.* A test exists because somebody intended the behaviour, and the intention
may be real even where the call site is not. The finding is that no production path reaches it, not
that it should be deleted. *The search was Python only.* Notebooks, shell scripts, anything deployed
outside `views_platform`, and any partner-side code were not searched. *The two APIs call their own
implementations, not pipeline-core's.* The table counts operations performed against the store,
which is the right unit for designing routes, but it is not an import graph. *`to_dict` is excluded*
and is a value-object method rather than a store operation in any case.

**What this test cannot tell you.** Whether a method nobody calls today is one somebody needs
tomorrow. It measures present use, which is evidence, not a mandate.

---

## 9. Does our own instrument cover this?

**What it asks.** Of the things these tests find, how many does the platform's existing contract
already govern? A boundary document that omits a class of coupling will not notice it drifting.

**How to run it.** Take the findings from tests 2, 6 and 8 and search the governing contract for each
one by name.

**What it said, 2026-11-24.** The Appwrite Seam Contract was searched for every metadata field name
and every Appwrite error code found by test 6: **zero matches.** The contract and the coordinate
registry centralise the *coordinates* — which bucket, which collection, which environment variable
carries which value. They say nothing about the shape of the record stored at those coordinates, nor
about the vendor's error taxonomy. The instrument exists and its scope stops one level short of the
leak.

**What this test cannot tell you.** Whether the gap is a defect or a deliberate scope boundary. It
finds silence; whether the silence is wrong is a judgment.

---

## 10. Dead defaults

**What it asks.** Does the code state a default that production never uses? A misleading default
costs a reader time and can cost a new deployment correctness.

**How to run it.** For each configuration field with a default, find what production actually passes.

**What it said, 2026-11-24.** `bucket_id: str = "production_forecasts"` at
`views-faoapi/src/views_faoapi/managers/appwrite/config.py:38` and
`views-crafdapi/src/views_crafdapi/managers/appwrite/config.py:39`. Production passes
`APPWRITE_UNFAO_BUCKET_ID` and `APPWRITE_CRAFD_BUCKET_ID` respectively, so neither default is ever
used, and both are identical across the two repositories because they predate the fork.

**What this test cannot tell you.** Whether removing the default is safe — something outside the
searched repositories may rely on it.

---

## 11. Count the vendor's actual surface

**What it asks.** How many distinct things from the vendor's library does the platform use? Not how
many lines wrap them — how many names you would have to re-implement or re-point if the vendor
changed.

**Why it is worth its own test.** Everything else here measures *our* code. This measures the
*vendor's* footprint, and it is the number that sizes a migration. A 5,000-line wrapper around 18
names is an 18-name problem with 5,000 lines of our own opinion attached; the two are moved by
different work.

**How to run it.**

```bash
grep -rh "from appwrite[a-z._]* import" --include=*.py <repos> | grep -v "/envs/" \
  | sed 's/.*import //' | tr ',' '\n' | sed 's/\s//g' | sort -u
```

Read the output by hand afterwards: comment lines, `# noqa` suffixes and docstring text come through
and must be discarded, which is judgment, not scripting.

**What it said, 2026-11-27. Fact, checked that day.** **Eighteen distinct names, platform-wide:**

| kind | names |
|---|---|
| services (the things that act) | `Client`, `Storage`, `Databases`, `TablesDB`, `Users` |
| helpers | `Query`, `ID`, `InputFile`, `Permission`, `Role` |
| errors | `AppwriteException` |
| return types | `File`, `FileList`, `Document`, `DocumentList`, `RowList`, `Bucket`, `Preferences` |

**Five service classes do all the work.** Seven of the eighteen are types the SDK hands back rather
than anything we call.

**And the client is constructed in exactly three places** — `views-faoapi/.../appwrite/manager.py:97`,
`views-crafdapi/.../appwrite/manager.py:41`, and
`views-pipeline-core/.../modules/appwrite/file.py:1475`. Every credential and coordinate the platform
holds passes through one of those three lines. **That is the narrowest definition of the seam this
platform has.**

**What this test cannot tell you.** Whether those names are used well. Five service classes could be
called correctly from one place or badly from forty — test 3 counts the files, this counts the
surface, and the pair is more informative than either.

---

## 12. Diff the copies before merging them

**What it asks.** Of several look-alike implementations, which differences are style and which are
decisions? Run this **before** any consolidation, because the answer decides whether consolidation
is cheap, expensive, or harmful.

**Why it exists.** This repository's own design preferences adopt Sandi Metz's rule — *duplication
is far cheaper than the wrong abstraction* — and state that *similar shape is not evidence*. This
test is how you tell shape from substance instead of assuming.

**How to run it.** For each corresponding file pair, `diff` them twice: once raw, and once with each
repository's own name normalised away. The gap between the two counts separates naming from
behaviour. Then read every surviving hunk and classify it: style, added capability, or **two
answers to the same question**.

**What it said, 2026-11-27, for views-faoapi against views-crafdapi. Fact, checked that day.**

| | files | verdict |
|---|---|---|
| identical, or identical once the repo name is normalised | 3 | `constants.py`, `sdk_compat.py`, `provisioning.py` |
| trivially different — typing style, import order, one added field | 4 | `auth.py`, `__init__.py`, `config.py`, `results.py` |
| **substantially diverged, in both directions** | 3 | `manager.py`, `file_cache.py`, `metadata.py` |

The three diverged files are **2,145 of views-faoapi's 2,421 lines and 2,042 of views-crafdapi's
2,320**, and **neither repository is a superset of the other.**

**The three divergences that are decisions, not drift:**

- **`download_file` holds opposed resolutions of one incident class.** views-crafdapi hard-fails when
  the downloaded byte count does not match the recorded size. views-faoapi deliberately skips that
  check for SDK-auto-deserialised JSON, after a production incident on 2026-08-24 where re-serialised
  manifests (26,544 → 22,676 bytes) were wrongly rejected as truncated. **Picking either breaks the
  other.**
- **Replace-on-upload.** views-faoapi stages then swaps and closed a data-loss window (C-182);
  views-crafdapi still deletes the old file first.
- **The timeout patch.** views-faoapi's is lock-guarded and installed once per process (#616);
  views-crafdapi's documents in its own comment that it is not thread-safe.

**The conclusion this test produced, which is the point of running it:** these are not three copies
of one thing. They are three answers to three incidents, two of which only one repository has
suffered. **About 250 lines are genuinely shared and the rest is not duplication at all.**

**What this test cannot tell you.** Which answer is right. It tells you a choice exists and that
somebody must read the incident behind it. For `download_file` that is a correctness decision and
not a matter of taste.

---

## Coverage so far

A test is "run" only where it was actually executed against that repository, not where a result was
inferred from a sibling.

| | pipeline-core | faoapi | crafdapi | postprocessing | publicapi | datafactory |
|---|---|---|---|---|---|---|
| 1. Public signatures | read | — | — | partial | n/a, no code | — |
| 2. Identifier census | — | — | — | — | — | — |
| 3. Import direction | **run** | **run** | **run** | **run, zero** | n/a, no code | **run, zero** |
| 4. Deployability | — | — | — | — | n/a, no code | — |
| 5. Substitution | — | — | — | — | n/a, no code | — |
| 6. Shared literals | run | run | partial | run | n/a, no code | — |
| 7. Change coupling | — | run | inconclusive | — | n/a, no code | — |
| 8. Interface width | run | run | run | run | n/a, no code | run, no calls |
| 9. Instrument coverage | run, platform-wide | | | | | |
| 10. Dead defaults | — | run | run | — | n/a, no code | — |

| 11. Vendor surface | **run, platform-wide — 18 names, 3 client constructions** | | | | | |
| 12. Diff the copies | n/a | **run** | **run** | — | n/a, no code | — |

**Note on views-crafdapi.** It was a deliberate copy of views-faoapi, kept so the two could be
watched drifting apart. **Test 12 is that experiment reporting its result, 2026-11-27: they have
drifted, in both directions, and three files now hold opposed answers to the same incidents.** A
result from one was never evidence about the other; it is now demonstrably not.

---

## Still open

- **Four tests have still never been run, and two of them are the decisive ones.** Test 2 (the
  identifier census), test 4 (deployability — install a consumer with the SDK absent and import it),
  test 5 (substitution — put a fake store behind the operations and run the suite). Tests 4 and 5 are
  together about a day and they are what Hohpe & Woolf claim a gateway is *for*. Until one of them
  has run, every architectural claim in this repository's documents is an argument rather than a
  measurement.
- **views-datafactory has not been assessed at all.** Requested by the maintainer on 2026-11-25. It
  references Appwrite in `src/datafactory_http/retry.py`, `docs/ADRs/026_credential_management.md`,
  two consumer guides, its risk register and an investigation report, so it is in scope for this
  effort and has simply not been looked at. Test 3 has since been run against it: **zero SDK imports**, so it is further out of scope than
  assumed. Test 4 remains the cheapest place to start. Nothing is
  blocked on it.
- **What to do about six operations that only tests call.** Test 8 found them; it cannot say whether
  they were speculative or are simply between uses. Deciding needs the person who wrote them, or a
  decision that the gateway offers five routes and the rest are reconsidered if someone asks for one.
- **Which of tests 2 through 5 to run first.** Test 4 is the cheapest with a decisive answer. Test 2
  is the one tied to the finding ADR-012 calls load-bearing. Not decided.
- **Whether any of these should become a standing check** rather than a thing someone remembers to
  run. Test 3 could be a CI import-contract rule. Tests 2 and 5 cannot be automated, which is itself
  worth recording: the most important property of this boundary is the one no pipeline can guard.
