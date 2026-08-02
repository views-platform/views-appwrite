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
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
WORKSPACE = REPO.parent
FIXTURES = REPO / "tests" / "fixtures"

VALID_FIXTURE = FIXTURES / "registry_valid.toml"
VALUELESS_FIXTURE = FIXTURES / "registry_valueless_target.toml"

# Every canonical reader on the platform, by the path consumers invoke.
READER_PATHS = {
    "views-models": WORKSPACE / "views-models" / "tools" / "registry_to_env.py",
    "views-faoapi": WORKSPACE / "views-faoapi" / "deployment" / "registry_to_env.py",
    "views-crafdapi": WORKSPACE / "views-crafdapi" / "deployment" / "registry_to_env.py",
}


def _present() -> dict[str, pathlib.Path]:
    """Readers that exist in this checkout. A sibling repo may not be cloned."""
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


def test_all_present_readers_are_structurally_identical():
    """The check the two-copies decision left out.

    Prose may differ. Parsed syntax may not.
    """
    found = _present()
    if len(found) < 2:
        pytest.skip(
            f"only {list(found)} checked out — agreement needs at least two readers"
        )
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
    exe = _interpreter_with_tomllib()
    if exe is None:
        pytest.skip(
            "no interpreter with stdlib tomllib (3.11+) available; the readers "
            "cannot be executed here. The structural test above still ran."
        )
    if len(found) < 2:
        pytest.skip(f"only {list(found)} checked out — nothing to compare")

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
    """The C-29 shape. Every reader must refuse it, loudly.

    This is the property that makes the registry's own guard meaningful: if a
    reader ever starts tolerating a value-less `[target]` entry, a consumer
    silently receives an incomplete coordinate set instead of failing.
    """
    found = _present()
    exe = _interpreter_with_tomllib()
    if exe is None:
        pytest.skip(
            "no interpreter with stdlib tomllib (3.11+) available; the readers "
            "cannot be executed here. The structural test above still ran."
        )

    tolerant = [
        name
        for name, p in found.items()
        if _run(exe, p, VALUELESS_FIXTURE).returncode == 0
    ]
    assert not tolerant, (
        f"these readers ACCEPTED a value-less [target] slot: {tolerant}. "
        "They must reject it. A tolerated value-less coordinate is how a "
        "consumer ends up running against a partial registry without knowing "
        "(C-29)."
    )
