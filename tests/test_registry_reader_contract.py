"""The registry's contract with its readers.

Every consumer on the seam reads `coordinate_registry.toml` through one of three
near-identical stdlib readers (views-models/tools/credentials/registry_to_env.py,
views-faoapi/deployment/registry_to_env.py,
views-crafdapi/deployment/registry_to_env.py). All three scan exactly two tables
-- `connection` and `target` -- and all three RAISE on an entry there that has
neither a `value` nor a reservation marker:

    ValueError: registry coordinate 'X' (class 'target') has no value

So a value-less entry in either table does not degrade a reader. It kills it.

One caveat, added 2026-08-02: if such an entry carries `status = "planned …"`,
the readers no longer agree -- views-models skips it and emits a PARTIAL set
where the other two still raise (C-51 / D-05). This file asserts the registry's
own shape, which is unaffected; the cross-reader question lives in
`test_registry_readers_agree.py`.

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

# GREEN AND BLOCKING. These protect a live invariant, so they run in the gating
# CI job -- see tests/conftest.py for why the kind is declared, not inferred.
pytestmark = pytest.mark.guard

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
    for name, entry in planned.items():
        assert "value" not in entry, (
            f"[planned.{name}] has a value, so it is no longer planned. "
            "Move it into [target] where consumers will actually read it."
        )
        assert "status" in entry, (
            f"[planned.{name}] must say what it is waiting for; §3 requires the "
            "class and status be declared, never inferred."
        )


def test_the_reservation_rule_is_still_written_down():
    """C-55: what the test above cannot check when there is nothing to check.

    That test used to `pytest.skip` when no `[planned]` slots existed. On
    2026-08-02 the last four graduated to `[target]`, so it began skipping on
    every run -- switching itself off during the ONE window where its guidance
    matters: after the last reservation is gone, and before the next author
    writes one. A guard that stands down whenever it is not already satisfied
    protects nobody.

    So the invariant is restated as one that always has something to assert. The
    reservation rule is prose -- prose is what decayed in C-54, where the warning
    stayed byte-identical while the data beneath it inverted -- and this pins the
    load-bearing parts of it to the file that must carry them.
    """
    text = REGISTRY.read_text(encoding="utf-8")
    # Deliberately the shortest token that carries each fact, not the sentence
    # around it. A phrase-level check fires on innocent rewording, and a guard
    # that cries wolf at prose edits gets deleted by the third person who hits
    # it. These four are the things that cannot be rephrased away: the table
    # name, the readers, the incident, the open divergence.
    required = {
        "the reserved-slot table": "[planned.*]",
        "the reader list": "registry_to_env.py",
        "the incident": "2186d45",
        "the divergence": "C-51",
    }
    missing = [label for label, needle in required.items() if needle not in text]
    assert not missing, (
        "the registry no longer explains how to reserve a value-less coordinate: "
        f"missing {missing}. Someone deleted the standing rule, most likely while "
        "tidying a section that had no entries left under it. Restore it -- that "
        "block is the only thing standing between the next editor and a repeat of "
        "2186d45, and it must survive the periods when no reservation exists."
    )


def test_the_contract_table_is_not_empty_while_the_clause_declares_it():
    """The always-runs companion to the two `[contract]` guards below.

    Both of those `pytest.skip` when no facts are declared -- which is C-55's shape
    exactly, and C-55 is registered in this repository for it: a guard that stands
    down when there is nothing to check is off during the one window that matters.
    Caught reviewing this file's own diff, one story after registering it.

    The skips are kept, because an empty `[contract]` table is a legitimate state
    and asserting over nothing is not a check. What makes them safe is this: while
    the seam contract declares §4.1, the table must have at least one row. Deleting
    the last fact then fails HERE rather than quietly switching two guards off.
    """
    registry = _load()
    facts = registry.get("contract", {})
    if facts:
        return  # the guards below have something to check; nothing to prove here

    contract = REGISTRY.parent / "appwrite_seam_contract.md"
    declares = "[contract.*]" in contract.read_text(encoding="utf-8")
    assert not declares, (
        "the seam contract declares §4.1 (`[contract.*]`) but the registry has no "
        "facts in it. Either a row was deleted -- in which case the two guards "
        "below have silently stopped checking anything -- or the clause was added "
        "without its first row. Both are states someone should have to notice."
    )


def test_every_contract_fact_is_usable_as_an_authority():
    """`[contract.*]` rows exist to be checked against. An empty one cannot be.

    Added with the table itself (v1.5.0). No reader scans `[contract]`, so a
    malformed row here cannot break a delivery the way a value-less `[target]`
    entry does (C-29) -- it fails differently and more quietly. The producer's
    check compares its copy against this row; if the row has no value, that
    comparison has nothing on one side, and whether it then errors or silently
    passes is the consuming repo's business, not something this file should leave
    to chance.

    `producer` and `consumer` are required because a fact with no named parties
    is not checkable by anyone: the whole mechanism is that BOTH sides verify
    themselves against the row, and a row that does not say who they are cannot
    be audited for whether they did.
    """
    registry = _load()
    facts = registry.get("contract", {})
    if not facts:
        pytest.skip("no [contract] facts declared yet — nothing to check")

    required = ("value", "producer", "consumer")
    offenders = [
        f"[contract.{name}] is missing {sorted(set(required) - set(entry))}"
        for name, entry in facts.items()
        if not set(required).issubset(entry)
    ]
    assert not offenders, (
        "a shared fact must carry a value and name both parties:\n  "
        + "\n  ".join(offenders)
        + "\n\nThese rows are the authority two repositories check themselves "
        "against. One without a value is an authority with nothing in it; one "
        "without named parties cannot be audited for whether they checked."
    )


def test_contract_facts_are_never_in_a_scanned_table():
    """A shared fact must not leak into any consumer's process environment.

    The readers scan `connection` and `target`. Putting a contract fact there
    would push it into the environment of every consumer on the seam -- including
    ones with no interest in it -- and turn a fact two parties agree on into a
    variable everyone receives. It would also make it a coordinate, which is the
    charter distinction v1.5.0 was careful to draw.
    """
    registry = _load()
    fact_names = set(registry.get("contract", {}))
    if not fact_names:
        pytest.skip("no [contract] facts declared yet — nothing to check")

    leaked = [
        f"[{table}.{name}]"
        for table in READER_SCANNED_TABLES
        for name in registry.get(table, {})
        if name in fact_names
    ]
    assert not leaked, (
        f"these names are declared as contract facts AND sit in a scanned "
        f"table: {leaked}. Every reader would emit them into the environment. "
        "A contract fact belongs in [contract] only (seam contract §4.1)."
    )


def test_no_secret_carries_a_value():
    """Standing registry rule, unrelated to the reader break but cheap to hold here.

    'Secrets appear only as SLOTS (name + required scopes) -- NEVER as values.
    No exceptions, ever.'
    """
    registry = _load()
    leaked = [name for name, entry in registry.get("secret", {}).items() if "value" in entry]
    assert not leaked, f"secret slots carrying a value: {leaked}"


# Every table the registry may contain, and what this repository does with it.
#
# C-75. Nothing here enumerated the tables, and a mutation proved it: a whole
# `[shadow.*]` table carrying a connection-classed live URL passed every guard and
# `validate_docs.sh`. Seven tables existed; the guards knew four between them, each
# hard-coded at the point of use.
#
# views-postprocessing -- a CONSUMER -- shipped this check on THIS file before we did
# (`test_every_table_in_the_registry_is_classified_here`, 2026-08-11). Their reason was
# exact: `[contract]` arrived carrying an obligation for them and their edition check was
# the only thing that noticed. The publisher should not learn the shape of its own file
# from the people reading it.
#
# The value is a note to the next person, not a machine-readable class -- the registry
# declares class per ENTRY (`class = "..."`), and a second vocabulary at table level would
# be a fact that must agree with a fact, which is C-53's exact shape.
KNOWN_TABLES = {
    "meta": "the edition itself: version, ratification, the amendment summary",
    "edition": "one row per published edition; `obliges_consumers` is the machine-readable half of §10",
    "connection": "SCANNED by every reader -- how to reach Appwrite",
    "target": "SCANNED by every reader -- what to read and write",
    "planned": "reservations with no value yet; deliberately unscanned (D-05, C-29)",
    "contract": "non-secret facts two seam parties must agree on; unscanned (§4.1)",
    "secret": "slots only, never values",
    "excluded": "named here so its absence is a decision rather than an oversight",
    "test_environment": "the test-project question, recorded pending an operator decision",
}


def test_every_table_in_the_registry_is_classified_here():
    """A table nobody classified is a change to this file's charter that nobody read.

    Deliberately asymmetric, and the asymmetry is the point. An UNKNOWN table fails:
    this file's scope grew and the growth must be a decision (§4.1 exists because that
    had started happening silently). A table listed here but currently ABSENT does not
    fail: `[planned]` is empty whenever there are no reservations, which is its normal
    resting state, and C-55 is what happens when a guard treats "nothing to check" as a
    problem.
    """
    registry = _load()
    unknown = sorted(set(registry) - set(KNOWN_TABLES))
    assert not unknown, (
        f"these tables are in the registry and classified nowhere: {unknown}.\n\n"
        "Adding a table widens what this file may contain, which is a charter change "
        "and belongs in the seam contract, not in a commit nobody reads. Classify it "
        "in KNOWN_TABLES above -- saying what this repository does with it -- and say "
        "so in the contract's amendment log."
    )


def _semver(text: str) -> tuple:
    """`"1.5.2"` -> `(1, 5, 2)`. Deliberately strict: this file's versions are always
    three numeric parts, and a lenient parse would silently order a malformed one."""
    parts = text.split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts), (
        f"version {text!r} is not three numeric parts; §10 versions always are"
    )
    return tuple(int(p) for p in parts)


def test_the_current_edition_is_classified():
    """Bumping the version without saying whether the bump obliges anyone is the
    omission this table exists to prevent.

    §10 requires every change to bump the version. §10.1 requires every bump to declare
    whether a consumer must act. Without this, `[edition]` decays into a log that stops
    a version or two behind the file it describes -- which is what happened to the
    amendment log's prose and is why #76 was filed against us rather than by us.
    """
    registry = _load()
    current = registry["meta"]["version"]
    editions = registry.get("edition", {})
    assert current in editions, (
        f"[meta] version is {current!r} and no [edition.\"{current}\"] row classifies it. "
        "Every bump must say whether it obliges a consumer to act (§10.1). If this bump "
        "only records an observation, say so -- that is the answer #76 asked for, and "
        "`false` is a real answer, not a default."
    )


def test_every_edition_states_whether_it_obliges_consumers():
    """A row present but unclassified is worse than no row: it looks answered."""
    registry = _load()
    missing = sorted(
        v for v, body in registry.get("edition", {}).items()
        if not isinstance(body.get("obliges_consumers"), bool)
    )
    assert not missing, (
        f"these editions have a row but no boolean `obliges_consumers`: {missing}. "
        "A consumer reads this field to decide whether to act; absent or non-boolean, "
        "it cannot."
    )


def test_the_obligation_floor_matches_the_editions():
    """`[meta] obliges_consumers_since` is DERIVED, and this is what stops it drifting.

    It is duplicated from the table on purpose -- without it every consumer writes its
    own semver sort, and five copies of one comparison is how the three readers came to
    disagree (C-52). One copy is fine; one copy nothing checks is C-53, where two numbers
    that must agree were compared to each other and to nothing else.
    """
    registry = _load()
    obliging = [
        v for v, body in registry.get("edition", {}).items()
        if body.get("obliges_consumers") is True
    ]
    assert obliging, (
        "no edition is marked obliges_consumers = true. At least one must be: a floor "
        "of 'nothing has ever obliged anyone' would make every consumer's check vacuous."
    )
    newest = max(obliging, key=_semver)
    declared = registry["meta"].get("obliges_consumers_since")
    assert declared == newest, (
        f"[meta] obliges_consumers_since is {declared!r} but the newest edition marked "
        f"obliges_consumers = true is {newest!r}. Consumers pin against the [meta] "
        "field; if it disagrees with the table, a consumer that should have acted stays "
        "green. Fix the field, or the row's classification -- not both to meet in the "
        "middle."
    )
