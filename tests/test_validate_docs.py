"""`docs/validate_docs.sh` under test — one mutation per check.

WHY THIS FILE EXISTS
--------------------
`validate_docs.sh` is 361 lines, runs as a REQUIRED check on every pull request,
and had no tests at all. Only checks 8 and 9 were ever shown to fail, both by hand,
both once. Everything else was trusted because it was green -- which is the exact
posture this repository registers as cluster G.

The rule is "a guard is not finished until it has been shown to fail". These tests
make that permanent instead of ceremonial: each one introduces the fault the check
exists to catch and asserts the script says so.

HOW IT WORKS
------------
Every test builds a small but complete doc-tree in `tmp_path` and copies the REAL
script into it. Nothing is paraphrased -- if the shipped script changes, these
tests exercise the change. The script `cd`s to its own directory, so a copy in a
temporary tree operates entirely on that tree and cannot touch this repository.

WHAT IS DELIBERATELY NOT ASSERTED
---------------------------------
Exact wording. The tests assert the exit code and a short, load-bearing SUBSTRING
of the message -- the coordinate, the filename, the word ERROR. Pinning whole
sentences would make every prose improvement a test failure, and a guard that
cries wolf at rewording gets deleted (the reasoning
`test_the_reservation_rule_is_still_written_down` already records).
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess

import pytest

# GREEN AND BLOCKING. Self-contained: needs no sibling repositories, so it carries
# no `crossrepo` lane marker and lands in `guards (self-contained)` automatically.
pytestmark = pytest.mark.guard

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "docs" / "validate_docs.sh"


# ---------------------------------------------------------------------------
# Fixture tree
# ---------------------------------------------------------------------------

CONTRACT = """# The Appwrite Seam Contract

| Field | Value |
|---|---|
| **Former name** | `PLATFORM-001` — retired, alias retained |
| Status | Accepted |
| Version | **1.0.0** |

Body. See ADR-000 for the practice.
"""

REGISTRY = """[meta]
contract = "fixture"
version = "1.0.0"
obliges_consumers_since = "1.0.0"
"""

PATTERN = """# The Consumer-API Deployment Pattern

| Field | Value |
|---|---|
| Status | Accepted |
| Version | **1.0.0** |
"""

ADRS_README = """# ADR index

- **ADR-000** — [Use of ADRs](000_use_of_adrs.md)
- **ADR-001** — [Ontology](001_ontology.md)

Contributors follow `contributor_protocols/carbon_based_agents.md`.
"""

CICS_README = """# Class Intent Contracts

## Active Contracts

None yet.
"""


def _tree(tmp_path: pathlib.Path) -> pathlib.Path:
    """A minimal doc-tree that passes every check, with the real script in it."""
    docs = tmp_path / "docs"
    (docs / "ADRs" / "platform").mkdir(parents=True)
    (docs / "CICs").mkdir()
    (docs / "contributor_protocols").mkdir()

    (tmp_path / "README.md").write_text(
        "# fixture repo\n\nPin against the floor: `obliges_consumers_since`.\n",
        encoding="utf-8",
    )
    (docs / "ADRs" / "000_use_of_adrs.md").write_text(
        "# ADR-000\n\n**Status:** Accepted\n\nSee ADR-001.\n", encoding="utf-8"
    )
    (docs / "ADRs" / "001_ontology.md").write_text(
        "# ADR-001\n\n**Status:** Accepted\n\nSee ADR-000.\n", encoding="utf-8"
    )
    (docs / "ADRs" / "README.md").write_text(ADRS_README, encoding="utf-8")
    (docs / "CICs" / "README.md").write_text(CICS_README, encoding="utf-8")
    (docs / "contributor_protocols" / "carbon_based_agents.md").write_text(
        "# Carbon protocol\n\n**Status:** Active\n", encoding="utf-8"
    )
    (docs / "ADRs" / "platform" / "appwrite_seam_contract.md").write_text(
        CONTRACT, encoding="utf-8"
    )
    (docs / "ADRs" / "platform" / "coordinate_registry.toml").write_text(
        REGISTRY, encoding="utf-8"
    )
    (docs / "ADRs" / "platform" / "consumer_api_deployment_pattern.md").write_text(
        PATTERN, encoding="utf-8"
    )

    shutil.copy2(SCRIPT, docs / "validate_docs.sh")
    return tmp_path


@pytest.fixture
def tree(tmp_path):
    return _tree(tmp_path)


def run(tree_root: pathlib.Path, ci: bool = False):
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin", "HOME": str(tree_root)}
    if ci:
        env["CI"] = "1"
    return subprocess.run(
        ["bash", str(tree_root / "docs" / "validate_docs.sh")],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def git(tree_root: pathlib.Path, *args: str):
    return subprocess.run(
        ["git", "-C", str(tree_root), *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def _git_init(tree_root: pathlib.Path, tag: str | None = None):
    """A committed repo with an `origin/main` ref, and optionally a tag."""
    git(tree_root, "init", "-q", "-b", "main")
    git(tree_root, "config", "user.email", "t@example.invalid")
    git(tree_root, "config", "user.name", "fixture")
    git(tree_root, "add", "-A")
    git(tree_root, "commit", "-q", "-m", "fixture")
    head = git(tree_root, "rev-parse", "HEAD").stdout.strip()
    git(tree_root, "update-ref", "refs/remotes/origin/main", head)
    if tag:
        git(tree_root, "tag", tag)


# ---------------------------------------------------------------------------
# The baseline. Every mutation below is measured against this.
# ---------------------------------------------------------------------------

def test_a_clean_tree_passes(tree):
    r = run(tree)
    assert r.returncode == 0, f"clean fixture tree should pass:\n{r.stdout}\n{r.stderr}"
    assert "PASSED" in r.stdout


def test_every_check_reports_what_it_scanned(tree):
    """C-09's other half: a green run must not be silent.

    Checks 2, 3, 4 and 6 used to print only a header on success, so a run that
    scanned nothing looked identical to one that checked everything. Each now
    states its counts.
    """
    r = run(tree)
    for expected in (
        "file(s) scanned",          # check 1
        "the two agree",            # check 2
        "reference(s) checked",     # check 3
        "protocol reference(s)",    # check 4
        "seam contract resolves",   # check 6
    ):
        assert expected in r.stdout, f"no evidence of work for {expected!r}:\n{r.stdout}"


# ---------------------------------------------------------------------------
# One mutation per check
# ---------------------------------------------------------------------------

def test_check1_warns_on_an_unfilled_placeholder(tree):
    """Check 1 is a WARNING, not an error — assert it warns and does not fail."""
    adr = tree / "docs" / "ADRs" / "000_use_of_adrs.md"
    adr.write_text(adr.read_text() + "\n**Date:** YYYY-MM-DD\n", encoding="utf-8")
    r = run(tree)
    assert "WARN" in r.stdout, f"placeholder not reported:\n{r.stdout}"
    assert r.returncode == 0, "check 1 is deliberately non-blocking"


def test_check1_now_scans_deferred_files(tree):
    """C-09: the Status filter read Accepted|Active, so a Deferred ADR was skipped."""
    (tree / "docs" / "ADRs" / "004_deferred.md").write_text(
        "# ADR-004\n\n**Status:** Deferred\n\n**Date:** YYYY-MM-DD\n", encoding="utf-8"
    )
    r = run(tree)
    assert "WARN" in r.stdout, f"a Deferred file was not scanned:\n{r.stdout}"


def test_check2_fires_when_a_listed_contract_is_missing(tree):
    readme = tree / "docs" / "CICs" / "README.md"
    readme.write_text(
        CICS_README.replace("None yet.", "- `DatastoreManager.md` — the facade"),
        encoding="utf-8",
    )
    r = run(tree)
    assert r.returncode == 1
    assert "DatastoreManager.md" in r.stdout


def test_check2_fires_when_a_contract_exists_but_is_unlisted(tree):
    """The always-runs companion (C-55's remedy) — the direction that used to be blind.

    This is the more likely defect once Phase 1 starts: a CIC written and never
    added to the index ADR-006 points readers at.
    """
    (tree / "docs" / "CICs" / "StorageManager.md").write_text("# CIC\n", encoding="utf-8")
    r = run(tree)
    assert r.returncode == 1
    assert "not listed" in r.stdout and "StorageManager.md" in r.stdout


def test_check3_fires_on_a_reference_to_a_nonexistent_adr(tree):
    readme = tree / "docs" / "ADRs" / "README.md"
    readme.write_text(readme.read_text() + "\nSee ADR-099 for details.\n", encoding="utf-8")
    r = run(tree)
    assert r.returncode == 1
    assert "ADR-099" in r.stdout


def test_check3_sees_the_010_plus_range(tree):
    """C-09's headline: the pattern was `ADR-00[0-9]`, so ADR-010+ was invisible.

    ADR-011 exists in the real tree and was cited 7 times without ever being
    checked. Here the reference is to a 010+ number with no file, which the old
    pattern could not even see.
    """
    (tree / "docs" / "ADRs" / "README.md").write_text(
        ADRS_README + "\nAlso see ADR-010.\n", encoding="utf-8"
    )
    r = run(tree)
    assert r.returncode == 1, "a broken ADR-010+ reference was not caught"
    assert "ADR-010" in r.stdout


def test_check3_ignores_foreign_and_candidate_adrs(tree):
    """The exclusions, which must not be silently over-broad either.

    A foreign ADR belongs to another repository and a candidate deliberately does
    not exist. Both are cited in the real tree and neither is a defect.
    """
    (tree / "docs" / "ADRs" / "README.md").write_text(
        ADRS_README
        + "\n- **ADR-012 (candidate):** not written yet\n"
        + "\nThe wire format is views-postprocessing ADR-013.\n",
        encoding="utf-8",
    )
    r = run(tree)
    assert r.returncode == 0, f"a foreign or candidate ADR was wrongly flagged:\n{r.stdout}"


def test_check4_fires_on_a_missing_protocol_file(tree):
    (tree / "docs" / "contributor_protocols" / "carbon_based_agents.md").unlink()
    r = run(tree)
    assert r.returncode == 1
    assert "carbon_based_agents.md" in r.stdout


def test_check6_fires_when_the_seam_contract_is_gone(tree):
    (tree / "docs" / "ADRs" / "platform" / "appwrite_seam_contract.md").unlink()
    r = run(tree)
    assert r.returncode == 1
    assert "seam contract is missing" in r.stdout


def test_check6_fires_when_the_former_name_alias_is_dropped(tree):
    """A doc still citing PLATFORM-001 must find the alias, or the rename stranded it."""
    contract = tree / "docs" / "ADRs" / "platform" / "appwrite_seam_contract.md"
    contract.write_text(CONTRACT.replace("**Former name**", "**Name**"), encoding="utf-8")
    (tree / "docs" / "ADRs" / "README.md").write_text(
        ADRS_README + "\nHistorically PLATFORM-001.\n", encoding="utf-8"
    )
    r = run(tree)
    assert r.returncode == 1
    assert "Former name" in r.stdout


def test_check7_fires_when_contract_and_registry_disagree(tree):
    reg = tree / "docs" / "ADRs" / "platform" / "coordinate_registry.toml"
    reg.write_text(REGISTRY.replace('version = "1.0.0"', 'version = "1.1.0"'), encoding="utf-8")
    r = run(tree)
    assert r.returncode == 1
    assert "v1.0.0" in r.stdout and "v1.1.0" in r.stdout


def test_check8_fires_when_a_changed_registry_did_not_bump_its_version(tree):
    """C-53's guard: the version VALUE must move when the file changes."""
    _git_init(tree)
    reg = tree / "docs" / "ADRs" / "platform" / "coordinate_registry.toml"
    reg.write_text(REGISTRY + '\n[target.NEW]\nvalue = "x"\n', encoding="utf-8")
    r = run(tree)
    assert r.returncode == 1
    assert "still v1.0.0" in r.stdout


def test_check8_passes_when_the_version_moved_with_the_content(tree):
    _git_init(tree)
    reg = tree / "docs" / "ADRs" / "platform" / "coordinate_registry.toml"
    contract = tree / "docs" / "ADRs" / "platform" / "appwrite_seam_contract.md"
    reg.write_text(
        REGISTRY.replace('version = "1.0.0"', 'version = "1.1.0"')
        + '\n[target.NEW]\nvalue = "x"\n',
        encoding="utf-8",
    )
    contract.write_text(CONTRACT.replace("**1.0.0**", "**1.1.0**"), encoding="utf-8")
    r = run(tree)
    assert r.returncode == 0, f"a correct bump was rejected:\n{r.stdout}"
    assert "v1.0.0 -> v1.1.0" in r.stdout


def test_check9_fires_when_the_readme_names_a_tag_that_does_not_exist(tree):
    _git_init(tree, tag="appwrite-seam-v1.0.0")
    readme = tree / "README.md"
    readme.write_text(
        readme.read_text() + "\nPin `appwrite-seam-v9.9.9`.\n", encoding="utf-8"
    )
    r = run(tree)
    assert r.returncode == 1
    assert "appwrite-seam-v9.9.9" in r.stdout


def test_check9_fires_when_the_readme_drops_the_floor_mechanism(tree):
    """C-76: the README must point at the obligation floor, not at a fixed tag."""
    (tree / "README.md").write_text("# fixture\n\nPin `appwrite-seam-v1.0.0`.\n", encoding="utf-8")
    _git_init(tree, tag="appwrite-seam-v1.0.0")
    r = run(tree)
    assert r.returncode == 1
    assert "obliges_consumers_since" in r.stdout


# ---------------------------------------------------------------------------
# The asymmetry. The single most valuable test in this file.
# ---------------------------------------------------------------------------

def test_a_check_that_cannot_run_skips_locally_but_fails_under_ci(tree):
    """Checks 8 and 9 SKIP when git state is unavailable — and must ERROR under CI.

    This is the property C-53, C-55 and C-70 were all about, and until now it
    rested entirely on a comment. `actions/checkout` creates neither `origin/main`
    nor tags, so the skip path is the DEFAULT on a runner, not the exception: if
    this asymmetry ever breaks, the gating job goes green with both checks inert
    and nothing says so.

    No git repository here at all, which is the strongest form of "cannot run".
    """
    local = run(tree, ci=False)
    assert local.returncode == 0, "a developer without git state should not be blocked"
    assert "SKIP" in local.stdout, f"expected a visible skip:\n{local.stdout}"

    in_ci = run(tree, ci=True)
    assert in_ci.returncode == 1, (
        "CI is set and the check could not run, but the script PASSED. A gate that "
        f"cannot run must not pass:\n{in_ci.stdout}"
    )
    assert "ERROR" in in_ci.stdout
