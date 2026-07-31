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

# 6. Platform-tier reference integrity (PLATFORM-NNN -> ADRs/platform/)
#    Check 3 above hard-codes ADR-00[0-9] and is structurally blind to the
#    platform tier — which is this repo's only live artifact. þing-02 /falsify
#    C-32: the one automated check could not see the one thing that ships.
echo "--- Checking platform-tier ADR references (PLATFORM-NNN) ---"
while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    file=$(echo "$ref" | cut -d: -f1)
    pnum=$(echo "$ref" | grep -oP 'PLATFORM-\K[0-9]{3}' | head -1)
    if [ -n "$pnum" ]; then
        match_count=$(find ADRs/platform -name "PLATFORM-${pnum}_*.md" 2>/dev/null | wc -l)
        if [ "$match_count" -eq 0 ]; then
            echo "  ERROR: $file references PLATFORM-${pnum} but no matching file found"
            errors=$((errors + 1))
        fi
    fi
done < <(grep -rn 'PLATFORM-[0-9][0-9][0-9]' --include='*.md' . 2>/dev/null || true)

# 7. Contract/registry version coherence
#    PLATFORM-001 §10: "The registry and this contract version together."
#    That rule was ratified and held by hand in two files. þing-02 /falsify
#    C-33: nothing enforced it, and the v1.2.0 edit touches both.
echo "--- Checking contract/registry version coherence ---"
CONTRACT="ADRs/platform/PLATFORM-001_identity_secrets_configuration_contract.md"
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
        echo "  ERROR: PLATFORM-001 is v${contract_ver} but coordinate_registry.toml is v${registry_ver}"
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
if [ "$errors" -gt 0 ]; then
    echo "=== FAILED: $errors issue(s) found ==="
    exit 1
else
    echo "=== PASSED: no issues found ==="
    exit 0
fi
