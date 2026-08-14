"""Every test module must declare which gate it belongs to.

The anti-vacuity check for the marker scheme in `conftest.py`. Without it, a test
module added later carries no marker, is excluded from both `-m guard` and
`-m falsification`, and therefore runs in **no CI job** -- while still passing a
bare local `pytest`, so nothing ever reports it missing.

That is the cluster-G shape (C-52, C-55, C-68) reproduced inside the machinery
built to end it, which is why this file exists rather than a comment asking
people to remember.

Modules are parsed, not imported: a collection error in one module must not be
able to hide the kind of another, and several test modules here need sibling
repositories present to import cleanly.
"""

from __future__ import annotations

import ast
import pathlib
import re

import pytest

# GREEN AND BLOCKING. Protects a live invariant -- see tests/conftest.py for why
# the kind is declared rather than inferred from a filename.
pytestmark = pytest.mark.guard

TESTS_DIR = pathlib.Path(__file__).resolve().parent

KINDS = ("guard", "falsification")

# Every marker this repository declares, kind and CI lane together. A module-level
# marker outside this set is a typo (C-78) -- see the test at the bottom of the file.
KNOWN_MARKERS = set(KINDS) | {"crossrepo"}


def _module_level_marks(path: pathlib.Path) -> set[str]:
    """Marker names in a module's top-level `pytestmark`, read without importing.

    Handles both `pytestmark = pytest.mark.x` and
    `pytestmark = [pytest.mark.x, pytest.mark.y(...)]`.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets
        ):
            continue
        values = (
            node.value.elts
            if isinstance(node.value, (ast.List, ast.Tuple))
            else [node.value]
        )
        for v in values:
            if isinstance(v, ast.Attribute):                       # pytest.mark.x
                found.add(v.attr)
            elif isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute):
                found.add(v.func.attr)                             # pytest.mark.x(...)
    return found


def test_every_test_module_declares_exactly_one_kind():
    """No module may join both gates, and none may join neither."""
    offenders: list[str] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        kinds = _module_level_marks(path) & set(KINDS)
        if len(kinds) != 1:
            offenders.append(
                f"{path.name}: declares {sorted(kinds) or 'no kind'} "
                f"(expected exactly one of {list(KINDS)})"
            )

    assert not offenders, (
        "every test module must declare exactly one kind at module level:\n"
        "    pytestmark = pytest.mark.guard          # green, blocks merge\n"
        "    pytestmark = pytest.mark.falsification  # red by design, blocks nothing\n\n"
        + "\n".join(f"  {o}" for o in offenders)
        + "\n\nA module with no kind runs in NO CI job while still passing a bare "
        "`pytest`, so nothing would report it missing. Declare it. Do not delete "
        "this check to make the suite pass -- that is C-68 exactly."
    )


def test_the_two_kinds_partition_the_whole_suite():
    """`-m guard` plus `-m falsification` must account for every test module.

    The check above is per-module. This one is about the pair of selectors CI
    actually uses: if the two markers ever stop covering everything between them
    -- a third kind, a renamed marker -- some tests would quietly run nowhere.
    """
    modules = sorted(p.name for p in TESTS_DIR.glob("test_*.py"))
    covered = sorted(
        p.name
        for p in TESTS_DIR.glob("test_*.py")
        if _module_level_marks(p) & set(KINDS)
    )
    missing = sorted(set(modules) - set(covered))

    assert not missing, (
        f"{len(missing)} of {len(modules)} test modules are outside both CI "
        f"selectors: {missing}\n\n"
        "CI runs `-m guard` (blocking) and `-m falsification` (reporting). A "
        "module in neither is invisible to both."
    )


# --------------------------------------------------------------------------
# C-77 — the checks above verify DECLARATIONS. These verify SELECTION.
#
# Both tests above passed while `guards.yml` selected guard modules by FILENAME,
# so a new guard module declared its kind correctly, satisfied the meta-guard,
# and ran in no CI job. The marker scheme sat one layer below the thing that
# decided what actually ran. Declaring a kind is worthless if the workflow does
# not select on it.
# --------------------------------------------------------------------------

WORKFLOW = TESTS_DIR.parent / ".github" / "workflows" / "guards.yml"

# A guard step must select by marker expression. These are the two lanes; between
# them they cover `guard` exactly, and `crossrepo` is absence-safe so a module
# that declares no lane lands in the self-contained one rather than in none.
LANE_SELECTORS = ('-m "guard and not crossrepo"', '-m "guard and crossrepo"')


def test_the_workflow_selects_guards_by_marker_not_by_filename():
    """The C-77 regression: a `-m guard` step that also names test files.

    `-m` can only NARROW the paths it is given, never widen them. So a step that
    passes both a marker and a file list is selecting by file list, whatever the
    marker says — and a module absent from that list runs nowhere while looking
    correctly declared.
    """
    assert WORKFLOW.is_file(), f"{WORKFLOW} is missing; the guard jobs are defined there"
    text = WORKFLOW.read_text(encoding="utf-8")

    offenders = [
        line.strip()
        for line in text.splitlines()
        if "-m " in line
        and "pytest" in line
        and re.search(r"tests/test_\w+\.py", line)
    ]
    assert not offenders, (
        "a guard step in guards.yml names test FILES alongside `-m`:\n  "
        + "\n  ".join(offenders)
        + "\n\nThat is C-77. `-m` narrows the given paths and cannot widen them, so "
        "the file list — not the marker — decides what runs, and a guard module "
        "missing from it joins no job while passing every check in this file. "
        "Pass a directory and let the marker expression select."
    )


def test_both_ci_lanes_are_present_in_the_workflow():
    """The other half: selecting by marker is only safe if BOTH lanes exist.

    Drop `-m "guard and crossrepo"` and the cross-repo guards stop running while
    the self-contained job stays green — the same silence C-77 describes, arrived
    at from the opposite direction.
    """
    assert WORKFLOW.is_file(), f"{WORKFLOW} is missing"
    text = WORKFLOW.read_text(encoding="utf-8")

    missing = [sel for sel in LANE_SELECTORS if sel not in text]
    assert not missing, (
        f"guards.yml no longer contains these lane selectors: {missing}\n\n"
        "Every module marked `guard` must be collected by exactly one of:\n"
        f"    {LANE_SELECTORS[0]}   (self-contained job)\n"
        f"    {LANE_SELECTORS[1]}       (cross-repo job)\n\n"
        "If a lane is renamed, update LANE_SELECTORS here in the same change — "
        "this constant and the workflow are two statements of one fact, and the "
        "point of this test is that they must agree."
    )


def test_crossrepo_is_only_ever_used_alongside_guard():
    """`crossrepo` routes a module to a job that only runs blocking guards.

    On a falsification module it would be a no-op the author would not notice:
    the reporting job selects `-m falsification` and would ignore it, so the
    module would run there and the marker would mean nothing. Declared markers
    that quietly mean nothing are how a scheme stops being trusted.
    """
    offenders = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        marks = _module_level_marks(path)
        if "crossrepo" in marks and "guard" not in marks:
            offenders.append(f"{path.name}: declares {sorted(marks)}")

    assert not offenders, (
        "`crossrepo` is a CI lane for GUARDS and is meaningless without it:\n  "
        + "\n  ".join(offenders)
        + "\n\nEither add `pytest.mark.guard`, or drop `crossrepo`."
    )


def test_no_module_declares_an_unknown_marker():
    """C-78 — the check `--strict-markers` was supposed to be and is not.

    `tests/conftest.py` sets `config.option.strict_markers = True`, and its
    docstring used to claim that made a typo an error. It does not: setting the
    option from `pytest_configure` is too late for pytest to honour, so
    `pytest.mark.guardd` emits a `PytestUnknownMarkWarning` and the module PASSES.
    Measured, not assumed.

    Nothing else covers the interesting case. `test_every_test_module_declares_
    exactly_one_kind` catches a module that declares NO valid kind -- but a module
    marked `guard` plus a mistyped `crossrepoo` declares a perfectly good kind, so
    that test is satisfied while the lane marker silently means nothing and the
    module lands in the wrong CI job. That is C-77's failure re-entering through
    a spelling mistake.

    KNOWN LIMIT, stated rather than discovered later: this reads module-level
    `pytestmark` only. A custom marker applied to a single test function
    (`@pytest.mark.something`) is invisible here. None exist today -- the only
    function-level marker in this suite is `_D05`, which wraps the BUILTIN
    `xfail` -- and closing that would mean either a `pytest.ini` carrying
    `--strict-markers` or walking every decorator, neither of which is worth it
    until a custom function-level marker exists.
    """
    offenders: list[str] = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        unknown = _module_level_marks(path) - KNOWN_MARKERS
        if unknown:
            offenders.append(f"{path.name}: {sorted(unknown)}")

    assert not offenders, (
        "these modules declare a marker this repository does not define:\n  "
        + "\n  ".join(offenders)
        + f"\n\nKnown markers: {sorted(KNOWN_MARKERS)}\n"
        "Almost always a typo. An unknown marker is NOT an error to pytest here "
        "(C-78: `strict_markers` set from `pytest_configure` is inert), so without "
        "this check it would warn and pass — and a mistyped `crossrepo` would put "
        "a guard in the wrong CI job silently.\n\n"
        "If the marker is genuinely new, add it to KNOWN_MARKERS *and* register it "
        "in tests/conftest.py, and say which CI job selects it."
    )
