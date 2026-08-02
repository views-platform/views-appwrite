#!/usr/bin/env bash
# Validates internal consistency of base_docs documentation set.
# Exit 0 if clean, exit 1 if issues found.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

errors=0

echo "=== base_docs validation ==="
echo ""

# 1. Check for unfilled template placeholders in accepted/active files
#    (skip files whose names contain "template" — those are expected to have placeholders)
#    These are warnings only (non-blocking) since in the template repo some
#    files are legitimately Accepted with placeholder dates.
echo "--- Checking for template placeholders in accepted/active files ---"
warnings=0
while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    [[ "$file" == *template* ]] && continue
    if grep -q 'YYYY-MM-DD' "$file"; then
        echo "  WARN: Unfilled date placeholder in $file"
        warnings=$((warnings + 1))
    fi
    if grep -q '<roles / team>' "$file"; then
        echo "  WARN: Unfilled deciders placeholder in $file"
        warnings=$((warnings + 1))
    fi
    if grep -q '<ClassName>' "$file"; then
        echo "  WARN: Unfilled ClassName placeholder in $file"
        warnings=$((warnings + 1))
    fi
done < <(grep -rl 'Status:.*\(Accepted\|Active\)' --include='*.md' . 2>/dev/null || true)
if [ "$warnings" -eq 0 ]; then
    echo "  OK"
fi

# 2. Verify CIC active contracts exist (skip blockquote/example lines)
echo "--- Checking CIC active contract references ---"
if [ -f "CICs/README.md" ]; then
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        contract=$(echo "$line" | sed -n 's/^- `\(.*\.md\)`.*$/\1/p')
        if [ -n "$contract" ] && [ ! -f "CICs/$contract" ]; then
            echo "  ERROR: CIC contract listed but missing: CICs/$contract"
            errors=$((errors + 1))
        fi
    done < <(grep -E '^- `[A-Z].*\.md`' CICs/README.md 2>/dev/null | grep -v '>' || true)
fi

# 3. Cross-ADR reference integrity (constitutional ADRs 000-009 only;
#    higher numbers are project-specific and not expected in the template repo)
echo "--- Checking cross-ADR references (constitutional: 000-009) ---"
while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    file=$(echo "$ref" | cut -d: -f1)
    adr_num=$(echo "$ref" | grep -oP 'ADR-00\K[0-9]' | head -1)
    if [ -n "$adr_num" ]; then
        match_count=$(find ADRs -name "00${adr_num}_*.md" 2>/dev/null | wc -l)
        if [ "$match_count" -eq 0 ]; then
            echo "  ERROR: $file references ADR-00${adr_num} but no matching file found"
            errors=$((errors + 1))
        fi
    fi
done < <(grep -rn 'ADR-00[0-9]' --include='*.md' . 2>/dev/null || true)

# 4. Check that referenced protocol files exist
echo "--- Checking protocol file references ---"
while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    file=$(echo "$ref" | cut -d: -f1)
    proto=$(echo "$ref" | grep -oP 'contributor_protocols/[a-z_]+\.md' | head -1)
    if [ -n "$proto" ] && [ ! -f "$proto" ]; then
        echo "  ERROR: $file references $proto but file does not exist"
        errors=$((errors + 1))
    fi
done < <(grep -rn 'contributor_protocols/' --include='*.md' . 2>/dev/null || true)

# 5. Report template status markers
echo "--- Checking template status markers ---"
template_count=$(grep -rl '\-\-template\-\-' --include='*.md' . 2>/dev/null | wc -l)
echo "  INFO: $template_count files still have --template-- status (expected in template repo)"

# 6. The seam contract resolves, and its retired alias still points somewhere.
#    Check 3 above hard-codes ADR-00[0-9] and is structurally blind to the
#    platform tier — which is this repo's only live artifact. þing-02 /falsify
#    C-32: the one automated check could not see the one thing that ships.
#    ADR-011 retired the PLATFORM-NNN scheme; this check follows the rename.
echo "--- Checking seam-contract references ---"
SEAM="ADRs/platform/appwrite_seam_contract.md"
if [ ! -f "$SEAM" ]; then
    echo "  ERROR: the seam contract is missing from $SEAM"
    errors=$((errors + 1))
else
    # The retired name must remain resolvable: anything still citing PLATFORM-001
    # has to find the alias recorded in the contract, or the rename stranded it.
    if grep -rqn 'PLATFORM-001' --include='*.md' . 2>/dev/null; then
        if ! grep -q 'Former name' "$SEAM"; then
            echo "  ERROR: docs still cite PLATFORM-001 but $SEAM records no 'Former name' alias"
            errors=$((errors + 1))
        fi
    fi
    # No document may POINT AT the pre-rename path. A markdown link resolves and
    # therefore breaks; inline code in prose is a quotation and does not. ADR-011
    # quotes the retired filename as its own evidence, which must stay readable —
    # so match link syntax, not every occurrence.
    # Scanned from the REPO ROOT, not from docs/. The script cd's to docs/ at
    # line 8, so every other check here is blind to README.md, reports/ and
    # tests/ — and README.md is the likeliest place for a stale contract link.
    # Verified by planting one: under the docs/-only scope it was not caught.
    # This check widens its own scope only; the rest of the script is unchanged.
    while IFS= read -r stale; do
        [[ -z "$stale" ]] && continue
        echo "  ERROR: ${stale%%:*} links to the pre-rename contract path"
        errors=$((errors + 1))
    done < <(grep -rn '](\([^)]*\)\?PLATFORM-001_identity_secrets_configuration_contract\.md' \
             --include='*.md' .. 2>/dev/null || true)
    # In TOML and shell there is no prose, so any occurrence is a pointer.
    while IFS= read -r stale; do
        [[ -z "$stale" ]] && continue
        case "${stale%%:*}" in ./validate_docs.sh) continue ;; esac
        echo "  ERROR: ${stale%%:*} references the pre-rename contract path"
        errors=$((errors + 1))
    done < <(grep -rn 'PLATFORM-001_identity_secrets_configuration_contract\.md' \
             --include='*.toml' --include='*.sh' . 2>/dev/null || true)
fi

# 7. Contract/registry version coherence
#    Seam contract §10: "The registry and this contract version together."
#    That rule was ratified and held by hand in two files. þing-02 /falsify
#    C-33: nothing enforced it, and the v1.2.0 edit touched both.
echo "--- Checking contract/registry version coherence ---"
CONTRACT="$SEAM"
REGISTRY="ADRs/platform/coordinate_registry.toml"
if [ -f "$CONTRACT" ] && [ -f "$REGISTRY" ]; then
    contract_ver=$(grep -P '^\| Version \|' "$CONTRACT" | grep -oP '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    registry_ver=$(grep -oP '^version = "\K[0-9.]+' "$REGISTRY" | head -1)
    if [ -z "$contract_ver" ]; then
        echo "  ERROR: cannot parse a version from $CONTRACT (expected a '| Version |' row)"
        errors=$((errors + 1))
    elif [ -z "$registry_ver" ]; then
        echo "  ERROR: cannot parse a version from $REGISTRY (expected [meta] version = \"x.y.z\")"
        errors=$((errors + 1))
    elif [ "$contract_ver" != "$registry_ver" ]; then
        echo "  ERROR: the seam contract is v${contract_ver} but coordinate_registry.toml is v${registry_ver}"
        echo "         §10 requires them to version together. Bump both or neither."
        errors=$((errors + 1))
    else
        echo "  OK: contract and registry both at v${contract_ver}"
    fi
else
    echo "  ERROR: contract or registry missing from ADRs/platform/"
    errors=$((errors + 1))
fi

echo ""
echo "--- Checking that a changed contract/registry bumped its version ---"
# C-53. The check above compares the two versions TO EACH OTHER and to nothing
# else, so "bump neither" satisfies it perfectly. That is how four coordinates
# became canonical on 2026-08-02 while the registry still called itself v1.3.0 --
# green gate, broken rule (§10: "every change bumps the version").
#
# Consumers pin by version, and three of them resolve this file through
# /blob/main/, so an unbumped edit changes what they read with nothing to compare.
# The version is the only handle they have; if it can stand still through a
# content change, it carries no information.
#
# Compares against origin/main, the branch consumers actually resolve. Skipped
# with a visible note when there is no git or no origin/main to compare against
# -- a check that cannot run must say so rather than pass quietly.
if ! command -v git >/dev/null 2>&1 || ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo "  SKIP: not a git checkout — cannot diff against origin/main"
elif ! git rev-parse --verify --quiet origin/main >/dev/null 2>&1; then
    echo "  SKIP: no origin/main in this checkout — nothing to compare against"
else
    # Compares the version VALUE across the two revisions, not whether the line
    # that carries it was touched. Two earlier drafts of this check were wrong in
    # opposite directions, and both are worth not repeating:
    #
    #   "any changed line mentioning a semver"  -> passes when someone adds prose
    #       like "byte-identical to v1.3.0" and never touches the declaration.
    #   "the declaration line appears in the diff" -> passes when the declaration
    #       line changes for an unrelated reason. Editing the trailing comment on
    #       `version = "1.3.0"` satisfied it while the version stood still.
    #
    # Only the value answers the question consumers actually ask: is what I pinned
    # still what I would get?
    _version_of() {   # $1 = git revision or "" for the working tree, $2 = file
        if [ -z "$1" ]; then cat "$2" 2>/dev/null; else git show "$1:docs/$2" 2>/dev/null; fi \
        | if [ "$2" = "$REGISTRY" ]; then grep -oP '^version = "\K[0-9.]+'
          else grep -P '^\| Version \|' | grep -oP '[0-9]+\.[0-9]+\.[0-9]+'; fi \
        | head -1
    }
    for f in "$CONTRACT" "$REGISTRY"; do
        [ -f "$f" ] || continue
        git diff --quiet origin/main -- ":/docs/$f" 2>/dev/null && continue
        was=$(_version_of origin/main "$f")
        now=$(_version_of "" "$f")
        if [ -z "$now" ]; then
            echo "  ERROR: cannot parse a version from $(basename "$f")"
            errors=$((errors + 1))
        elif [ -z "$was" ] && git cat-file -e "origin/main:docs/$f" 2>/dev/null; then
            # The file exists on origin/main but no version parsed out of it. An
            # empty `was` would otherwise differ from `now` and report OK -- a
            # false pass on exactly the comparison this check exists to make.
            echo "  ERROR: $(basename "$f") exists on origin/main but no version could be parsed there."
            echo "         Cannot prove the version moved, so this is not a pass."
            errors=$((errors + 1))
        elif [ "$was" = "$now" ]; then
            echo "  ERROR: $(basename "$f") differs from origin/main but its version is still v${now}."
            echo "         §10: 'every change bumps the version. The registry and this"
            echo "         contract version together.' Consumers pin by version; an edit"
            echo "         they cannot detect is the failure mode this rule exists to stop."
            errors=$((errors + 1))
        else
            echo "  OK: $(basename "$f") changed and its version moved v${was} -> v${now}"
        fi
    done
fi

echo ""
if [ "$errors" -gt 0 ]; then
    echo "=== FAILED: $errors issue(s) found ==="
    exit 1
else
    echo "=== PASSED: no issues found ==="
    exit 0
fi
