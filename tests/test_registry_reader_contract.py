"""The registry's contract with its readers.

Every consumer on the seam reads `coordinate_registry.toml` through one of two
near-identical stdlib readers (views-models/tools/registry_to_env.py,
views-faoapi/deployment/registry_to_env.py). Both scan exactly two tables --
`connection` and `target` -- and both RAISE on any entry there without a `value`:

    ValueError: registry coordinate 'X' (class 'target') has no value

So a value-less entry in either table does not degrade a reader. It kills it.

WHY THIS FILE EXISTS
--------------------
Commit 2186d45 added four `status = "planned"` slots to `[target]` with no values,
to declare coordinates for an incoming consumer before its repo existed. Every
registry read on the platform failed from that commit until it was fixed -- and
the failure was invisible here, because this repo has no runtime and the readers
live in other repos.

It mattered because `un_fao/run.sh` exports only GITHUB_TOKEN and
APPWRITE_DATASTORE_API_KEY from `.env`. Coordinates reach the delivery process
ONLY from the registry. An unreadable registry means the delivery runs with no
coordinates at all, and `run.sh` warns and continues rather than stopping.

These tests are GREEN and must stay green. They are not falsification stubs.
"""

from __future__ import annotations

import pathlib

import pytest

# The READERS require Python >= 3.11 for stdlib tomllib. These tests must run on
# whatever interpreter this repo's suite uses, so they fall back to `tomli` --
# the same parser, vendored for 3.10. Skipping instead would make the file a
# decoration: it skipped silently on the first run, on the exact registry break
# it was written to catch.
try:
    import tomllib
except ModuleNotFoundError:            # Python < 3.11
    try:
        import tomli as tomllib       # type: ignore[no-redef]
    except ModuleNotFoundError:
        tomllib = None

REGISTRY = (
    pathlib.Path(__file__).resolve().parent.parent
    / "docs" / "ADRs" / "platform" / "coordinate_registry.toml"
)

# The tables both readers scan. Mirrors `_COORDINATE_CLASSES` in each of them.
READER_SCANNED_TABLES = ("connection", "target")


def _load() -> dict:
    if tomllib is None:
        pytest.fail(
            "no TOML parser available (neither stdlib tomllib nor tomli). "
            "These checks must not skip: the registry break they exist to catch "
            "is invisible in this repo, which has no runtime of its own."
        )
    with REGISTRY.open("rb") as fh:
        return tomllib.load(fh)


def test_registry_parses():
    assert _load(), "the registry is empty or unparseable"


def test_every_reader_scanned_entry_has_a_value():
    """The invariant 2186d45 broke.

    A slot without a value belongs in a table the readers do not scan --
    `[planned]` -- not in `[connection]` or `[target]`.
    """
    registry = _load()
    offenders = [
        f"[{table}.{name}]"
        for table in READER_SCANNED_TABLES
        for name, entry in registry.get(table, {}).items()
        if "value" not in entry
    ]
    assert not offenders, (
        "these entries would make BOTH canonical readers raise, and the un_fao "
        "delivery would run with no coordinates:\n  "
        + "\n  ".join(offenders)
        + "\n\nA slot with no value is a declaration of intent, not a coordinate. "
        "Put it in [planned] until the operator supplies a value."
    )


def test_planned_slots_are_outside_the_scanned_tables():
    """The positive half: planned slots must still be declared somewhere.

    Moving them out of `[target]` fixes the readers; deleting them would lose the
    declaration that lets a new consumer find its slot on day one.
    """
    registry = _load()
    planned = registry.get("planned", {})
    if not planned:
        pytest.skip("no planned slots declared right now — nothing to check")
    for name, entry in planned.items():
        assert "value" not in entry, (
            f"[planned.{name}] has a value, so it is no longer planned. "
            "Move it into [target] where consumers will actually read it."
        )
        assert "status" in entry, (
            f"[planned.{name}] must say what it is waiting for; §3 requires the "
            "class and status be declared, never inferred."
        )


def test_no_secret_carries_a_value():
    """Standing registry rule, unrelated to the reader break but cheap to hold here.

    'Secrets appear only as SLOTS (name + required scopes) -- NEVER as values.
    No exceptions, ever.'
    """
    registry = _load()
    leaked = [name for name, entry in registry.get("secret", {}).items() if "value" in entry]
    assert not leaked, f"secret slots carrying a value: {leaked}"
