"""Test-kind declarations for this repository.

This repo's `tests/` holds two kinds of test that must never be run as one gate:

    guard          must be GREEN. Blocks merge. Protects a live invariant --
                   the C-29 registry shape, the agreement of the three canonical
                   readers, the contract/registry version lockstep.

    falsification  RED BY DESIGN. Blocks nothing. Each stub encodes an
                   unresolved risk-register finding and turns green only when
                   that finding is fixed. `docs/contributor_protocols/
                   carbon_based_agents.md` s1-2: expected-red, and "must not be
                   deleted to make a gate pass".

WHY A MARKER RATHER THAN A FILENAME GLOB
----------------------------------------
Until now the only thing separating the two kinds was the `test_falsification_*`
filename prefix. Selecting CI's blocking set by glob would be **inference from a
name**, and this repository forbids that twice over:

  - ADR-003, `authority of declarations over inference`;
  - `coordinate_registry.toml`, about its own data: "class is DECLARED here,
    never inferred from a name's prefix or carrier."

It would also mis-classify silently. A guard added later under a name the glob
does not match joins no gate and runs nowhere -- a new blind guard, introduced by
the epic written to remove blind guards (C-70, cluster G).

So the kind is declared, and `--strict-markers` makes a typo an error rather than
a silent no-op.

NOT A THIRD KIND: `xfail(strict=True)` in `test_registry_readers_agree.py`. Those
are GUARDS that currently fail for a known, registered reason (D-05), and they
fail the suite if they ever unexpectedly PASS. They belong to the blocking set.

THE META-GUARD LIVES IN `test_test_kinds.py`, NOT HERE. pytest does not collect
tests from `conftest.py`, so a check written in this file would silently never
run -- the precise failure it exists to prevent. It WAS written here first, and
the collected count not moving from 27 is what caught it. Left recorded because
the next person will reach for conftest.py too.
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register the two kinds and make unknown markers an error."""
    config.addinivalue_line(
        "markers",
        "guard: must be green; blocks merge. Protects a live invariant.",
    )
    config.addinivalue_line(
        "markers",
        "falsification: red by design; blocks nothing. Encodes an open register "
        "finding (carbon protocol s1-2).",
    )
    # A typo'd marker is exactly the silent no-op this repo keeps finding.
    config.option.strict_markers = True
