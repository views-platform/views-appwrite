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

import pytest

# GREEN AND BLOCKING. Protects a live invariant -- see tests/conftest.py for why
# the kind is declared rather than inferred from a filename.
pytestmark = pytest.mark.guard

TESTS_DIR = pathlib.Path(__file__).resolve().parent

KINDS = ("guard", "falsification")


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
