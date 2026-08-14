"""The three canonical registry readers must agree.

Consumers do not read `coordinate_registry.toml` directly. Each reaches it through
a per-consumer copy of a stdlib-only reader:

    views-models/tools/registry_to_env.py
    views-faoapi/deployment/registry_to_env.py
    views-crafdapi/deployment/registry_to_env.py

Copying that reader is a deliberate, ratified choice -- WET before DRY. Its own
header says why: "the single source of truth is the DATA (the registry), never
the reader." This file does not challenge that. It supplies the thing the
decision left out: **a check that the copies still agree.**

Nothing else verifies it. If one copy is fixed, extended, or has its class filter
changed and the others are not, two runtimes disagree about what a coordinate IS,
and no test anywhere fails.

TWO TIERS, DELIBERATELY
-----------------------
1. STRUCTURAL -- compares the readers' parsed syntax with module docstrings
   removed. Needs no interpreter beyond this one, so it ALWAYS runs. Catches
   logic drift, which is the failure mode that matters.
2. BEHAVIOURAL -- actually executes all three on a fixture registry and compares
   stdout. Needs Python >= 3.11 (the readers use stdlib `tomllib`), so it is
   conditional -- but it reports loudly when it cannot run rather than passing.

WHY "IDENTICAL OUTPUT" IS NOT SUFFICIENT ON ITS OWN
---------------------------------------------------
On 2026-08-02 all three readers CRASHED identically on the live registry (C-29).
A naive "same output" comparison would have reported them as agreeing -- a
vacuous pass on a total platform outage. So the behavioural test asserts
non-empty, successful, matching output, and separately asserts they all still
REJECT the shape that caused that outage.

The readers are never imported. They are read as text and run as subprocesses,
which is how consumers actually use them, and creates no dependency edge on any
consumer repo.
"""

from __future__ import annotations

import ast
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

# GREEN AND BLOCKING. These protect a live invariant, so they run in the gating
# CI job -- see tests/conftest.py for why the kind is declared, not inferred.
#
# `crossrepo` is the CI LANE, and it is why this module is not in the
# self-contained job: every test below needs sibling repositories on disk, and
# `test_at_least_one_reader_is_present` correctly FAILS on a lone runner. The
# workflow used to express that by naming this file; it now selects on this
# marker (C-77).
pytestmark = [pytest.mark.guard, pytest.mark.crossrepo]

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = REPO.parent
FIXTURES = REPO / "tests" / "fixtures"

VALID_FIXTURE = FIXTURES / "registry_valid.toml"
VALUELESS_FIXTURE = FIXTURES / "registry_valueless_target.toml"
RESERVATION_FIXTURE = FIXTURES / "registry_planned_reservation.toml"

# Every canonical reader on the platform, by the path consumers invoke.
#
# C-52: this dict named `views-models/tools/registry_to_env.py` from the day the
# file was written. views-models#309 had already moved the reader to
# `tools/credentials/`, so `_present()` dropped it silently and the whole file
# graded views-faoapi against views-crafdapi -- byte-identical clones that agree
# trivially. The one guard written to detect reader divergence could not see the
# divergence that existed (C-51). A missing reader is now an ERROR, not a filter.
READER_PATHS = {
    "views-models": WORKSPACE / "views-models" / "tools" / "credentials" / "registry_to_env.py",
    "views-faoapi": WORKSPACE / "views-faoapi" / "deployment" / "registry_to_env.py",
    "views-crafdapi": WORKSPACE / "views-crafdapi" / "deployment" / "registry_to_env.py",
}

# Why xfail rather than a plain assert on the two divergence tests below: the
# readers genuinely disagree today, that disagreement is REGISTERED (D-05), and
# it cannot be settled from this repo -- views-models' opposing behaviour is
# pinned by its own ratified test. A red test would say "someone broke
# something"; that is false, and a permanently-red suite trains people to ignore
# it. `strict=True` is the load-bearing part: if the readers ever converge, the
# XPASS FAILS the suite and forces this file and D-05 to be closed together.
#
# `raises=AssertionError` is not decoration. An unconstrained `xfail` absorbs
# ANY exception as an expected failure -- a corrupt reader, a SyntaxError out of
# `ast.parse`, a subprocess timeout -- and reports the suite green. That would
# turn a marker meant to TRACK one known disagreement into a blanket amnesty for
# this file. Constrained, only the deliberate `assert` below may fail; anything
# else propagates and is seen.
_D05 = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "D-05 / C-51: views-models honours `status = \"planned …\"` and skips; "
        "views-faoapi and views-crafdapi ignore the marker and raise. Ratified "
        "both ways, in two repos. Settle D-05, then delete this marker."
    ),
)


def _present() -> dict[str, pathlib.Path]:
    """Readers that exist in this checkout. A sibling repo may not be cloned.

    Absence is reported by `test_every_declared_reader_path_resolves`, which is
    what stops a typo'd path from quietly shrinking the comparison set again.
    """
    return {name: p for name, p in READER_PATHS.items() if p.is_file()}


def _structure(path: pathlib.Path) -> str:
    """Parsed syntax with the module docstring dropped.

    The copies differ in prose -- one carries the þing-01 pattern note, one says
    `python3` in its usage line. Those differences are legitimate and must not
    fail the test. Divergence in *behaviour* must.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        tree.body.pop(0)
    return ast.dump(tree, annotate_fields=True)


def _interpreter_with_tomllib() -> str | None:
    """An interpreter the readers can actually run under (stdlib tomllib, 3.11+)."""
    candidates = [sys.executable, "python3.13", "python3.12", "python3.11"]
    candidates += [
        str(p) for p in sorted(WORKSPACE.glob("*/envs/*/bin/python"))
    ]
    for cand in candidates:
        exe = cand if pathlib.Path(cand).is_file() else shutil.which(cand)
        if not exe:
            continue
        probe = subprocess.run(
            [exe, "-c", "import tomllib"], capture_output=True, timeout=30
        )
        if probe.returncode == 0:
            return exe
    return None


def _require_interpreter() -> str:
    """The interpreter, or SKIP locally and FAIL under CI.

    Locally a skip is right: not every machine has 3.11+, and a developer should not
    be blocked by that. **In CI it must not skip.** The `guards (cross-repo)` job pins
    `python-version: "3.12"` and its comment says why -- but nothing connected that pin
    to these tests, so lowering it turned the behavioural half of this guard off and
    left the job green.

    Proven before this helper existed: with no 3.11+ interpreter reachable and `CI`
    set, three tests skipped and pytest exited **0**. The counts also moved from
    `4 passed, 2 xfailed` to `2 passed, 3 skipped, 1 xfailed` -- so one of the two
    `xfail(strict=True)` D-05 ratchets silently disarmed as well, and the signal that
    tells us when views-models executes the ruling would simply stop arriving.

    Same asymmetry, and the same reasoning, as `docs/validate_docs.sh` check 8: the
    workflow step is the thing most likely to be simplified later, so the workflow
    pins the version AND this refuses to pass without it. Belt and braces on purpose.
    """
    exe = _interpreter_with_tomllib()
    if exe is not None:
        return exe
    message = (
        "no interpreter with stdlib tomllib (3.11+) available; the readers cannot be "
        "executed here"
    )
    if os.environ.get("CI"):
        pytest.fail(
            f"CI is set and {message}. A gate that cannot run must not pass: the "
            'behavioural reader comparison would be silently absent. Check '
            '`python-version` in .github/workflows/guards.yml — it must be >= 3.11.'
        )
    pytest.skip(f"{message}. The structural tests above still ran.")


def _require_two_readers(found: dict) -> None:
    """At least two readers, or SKIP locally and FAIL under CI.

    C-52 is what this prevents: the guard spent its life comparing two byte-identical
    clones and agreeing trivially, because the third had moved and was dropped without
    a word. `guards (cross-repo)` now refuses to run against fewer readers than it
    cloned -- but that check lives in the workflow, and this one lives with the test.
    Either alone can be removed by someone tidying; both is the point.
    """
    if len(found) >= 2:
        return
    message = f"only {sorted(found)} checked out — agreement needs at least two readers"
    if os.environ.get("CI"):
        pytest.fail(
            f"CI is set and {message}. A comparison of one is not a smaller signal, "
            "it is C-52. The workflow clones the public siblings; if they are absent "
            "here, that step failed or was removed."
        )
    pytest.skip(message)


def _run(exe: str, reader: pathlib.Path, registry: pathlib.Path):
    return subprocess.run(
        [exe, str(reader), str(registry)], capture_output=True, text=True, timeout=60
    )


# --------------------------------------------------------------------------
# Tier 1 -- structural. Always runs.
# --------------------------------------------------------------------------

def test_at_least_one_reader_is_present():
    """Guard against the whole file passing vacuously in a lone checkout."""
    found = _present()
    assert found, (
        "no canonical reader found in this checkout, so nothing below can have "
        "verified anything. Expected at least one of:\n  "
        + "\n  ".join(str(p) for p in READER_PATHS.values())
    )


def test_every_declared_reader_path_resolves():
    """A CLONED repo whose reader is missing means the path here is wrong (C-52).

    `_present()` has to tolerate an uncloned sibling -- not everyone checks out
    all five repos. But that tolerance is exactly what let a stale path hide: the
    reader had MOVED, so its repo was present and its file was not, and the suite
    read that as "not cloned" and carried on comparing the survivors.

    Distinguishing the two cases is the whole fix. Repo absent -> fine. Repo
    present, reader absent -> the map in this file is lying about where the
    platform's readers live, and every comparison below is weaker than it looks.
    """
    stale = []
    for name, path in READER_PATHS.items():
        repo = WORKSPACE / name
        if repo.is_dir() and not path.is_file():
            stale.append(f"{name}: repo is checked out but {path} does not exist")
    assert not stale, (
        "READER_PATHS points at files that are not there, so those readers were "
        "silently excluded from every comparison in this file:\n  "
        + "\n  ".join(stale)
        + "\n\nFind where the reader moved and update READER_PATHS. Do NOT delete "
        "the entry -- that is how C-52 happened."
    )


@_D05
def test_all_present_readers_are_structurally_identical():
    """The check the two-copies decision left out.

    Prose may differ. Parsed syntax may not.
    """
    found = _present()
    _require_two_readers(found)
    structures = {name: _structure(p) for name, p in found.items()}
    reference_name, reference = next(iter(structures.items()))
    diverged = [name for name, s in structures.items() if s != reference]
    assert not diverged, (
        f"registry readers have diverged from {reference_name}: {diverged}.\n"
        "Two runtimes now disagree about what a coordinate is, and nothing else "
        "on the platform would have failed. Reconcile them, or the registry has "
        "as many meanings as it has readers."
    )


# --------------------------------------------------------------------------
# Tier 2 -- behavioural. Needs an interpreter the readers can run under.
# --------------------------------------------------------------------------

def test_all_present_readers_emit_identical_nonempty_output():
    """Same input, same output -- and the output must not be empty.

    The non-empty assertion is the point. All three crashed identically during
    the C-29 outage; a bare equality check would have called that agreement.
    """
    found = _present()
    exe = _require_interpreter()
    _require_two_readers(found)

    results = {name: _run(exe, p, VALID_FIXTURE) for name, p in found.items()}

    failed = {n: r.stderr.strip()[-300:] for n, r in results.items() if r.returncode != 0}
    assert not failed, (
        "readers failed on a VALID fixture registry — identical failure is not "
        f"agreement:\n{failed}"
    )

    empty = [n for n, r in results.items() if not r.stdout.strip()]
    assert not empty, f"readers emitted nothing on a valid registry: {empty}"

    outputs = {n: r.stdout for n, r in results.items()}
    ref_name, ref = next(iter(outputs.items()))
    diverged = {n: o for n, o in outputs.items() if o != ref}
    assert not diverged, (
        f"readers disagree on the same registry. {ref_name} emitted:\n{ref}\n"
        f"but these differ: {list(diverged)}"
    )


def test_all_present_readers_reject_a_valueless_target_slot():
    """The unambiguous half of the C-29 shape: no value, no marker, no excuse.

    All three readers reject this today, so it is a real green test rather than
    an aspiration. Keeping it separate from the reservation case below is what
    makes each verdict readable: this one asks "is malformed data refused?", and
    the answer is yes everywhere.
    """
    found = _present()
    exe = _require_interpreter()

    tolerant = [
        name
        for name, p in found.items()
        if _run(exe, p, VALUELESS_FIXTURE).returncode == 0
    ]
    assert not tolerant, (
        f"these readers ACCEPTED a [target] entry with no value and no "
        f"reservation marker: {tolerant}. Nothing in that entry declares intent, "
        "so continuing hands a consumer a partial coordinate set with no signal "
        "(C-29)."
    )


@_D05
def test_all_present_readers_agree_on_a_planned_reservation():
    """The disputed half (D-05) -- and the one that actually bit.

    `2186d45` used THIS shape, not the bare one above. Under today's readers it
    would no longer crash the platform loudly; views-models would skip the four
    reserved names and hand the UN FAO delivery 12 of 16 coordinates in silence.
    C-29 records a loud failure that the platform can no longer reproduce.

    Asserting agreement (not a specific verdict) is deliberate: this repo owns
    the contract, not views-models' behaviour, and D-05 has not been settled.
    Either answer closes this test; disagreement is what may not stand.
    """
    found = _present()
    exe = _require_interpreter()
    _require_two_readers(found)

    verdicts = {
        name: ("skip" if _run(exe, p, RESERVATION_FIXTURE).returncode == 0 else "raise")
        for name, p in found.items()
    }
    assert len(set(verdicts.values())) == 1, (
        "the canonical readers disagree about a reserved (value-less, "
        f"status=planned) [target] entry: {verdicts}.\n\n"
        "This is NOT a reader bug to patch here — both behaviours are pinned by "
        "ratified tests in their own repos (D-05). A registry edit that is "
        "harmless to one consumer is fatal to another, and which one you get "
        "depends on who reads the file. Settle D-05 first."
    )
