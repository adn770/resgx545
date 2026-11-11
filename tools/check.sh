#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: tools/check.sh [--quick | --list]
#
# The one check script. Full: every check of the tree (cargo, libsgxfive, pytest, the records
# and views, glossary, isa book, reuse lint, the clean-room guard, no numpy, section
# references). --quick: the subset the pre-commit hook runs on the staged change (whitespace,
# the guard on the index, numpy, the cheap record checks), on the repository it is run in.
# --list: print the steps without running them.
#
# Environment: RESGX545_DATA (default: ../resgx545-data), RESGX545_REQUIRE_DATA (default 1),
# RESGX545_GUARD_DIR and RESGX545_REQUIRE_GUARD (default 1: a missing guard fails; set 0 to
# have it reported as NOT CHECKED), CHECK_TAIL (lines of output kept per step, default 25),
# CHECK_ONLY (an extended regex: run only the steps whose command line matches).
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$HERE")
mode=full
case "${1:-}" in
    --quick) mode=quick ;;
    --list) mode=list ;;
    "") ;;
    *) echo "usage: $0 [--quick | --list]" >&2; exit 2 ;;
esac

PY=python3
[ -x "$ROOT/.venv/bin/python" ] && PY="$ROOT/.venv/bin/python"
[ -d "$ROOT/.venv/bin" ] && export PATH="$ROOT/.venv/bin:$PATH"
export PYO3_PYTHON=$PY
[ -d "$ROOT/../resgx545-data" ] && export RESGX545_DATA=${RESGX545_DATA:-$ROOT/../resgx545-data}
export RESGX545_REQUIRE_DATA=${RESGX545_REQUIRE_DATA:-1}
export RESGX545_REQUIRE_GUARD=${RESGX545_REQUIRE_GUARD:-1}

failed=()
steps=0
step() {
    if [ -n "${CHECK_ONLY:-}" ] && ! printf '%s' "$*" | grep -Eq "$CHECK_ONLY"; then return; fi
    steps=$((steps + 1))
    if [ "$mode" = list ]; then echo "$*"; return; fi
    echo "=== $*"
    local out rc
    out=$("$@" 2>&1); rc=$?
    printf '%s\n' "$out" | tail -n "${CHECK_TAIL:-25}"
    echo "exit $rc"
    [ $rc -eq 0 ] || failed+=("$*")
}
# the numpy rule: numpy is for scratch venvs, never in a tracked .py
numpy_staged() {
    local f bad=0
    while IFS= read -r -d '' f; do
        git show ":$f" | grep -Eq '^[^#]*\b(import|from)[[:space:]]+numpy\b' \
            && { echo "$f imports numpy (scratch only)"; bad=1; }
    done < <(git diff --cached --no-renames --name-only --diff-filter=ACMR -z -- '*.py')
    return $bad
}
numpy_tracked() {
    local f bad=0
    while IFS= read -r -d '' f; do
        grep -Eq '^[^#]*\b(import|from)[[:space:]]+numpy\b' "$f" \
            && { echo "$f imports numpy (scratch only)"; bad=1; }
    done < <(git ls-files -z -- '*.py')
    return $bad
}

if [ "$mode" = quick ]; then
    TOP=$(git rev-parse --show-toplevel) || exit 2
    cd "$TOP" || exit 2
    step git diff --cached --check
    step "$PY" "$HERE/clean-room/guard.py" --staged "$TOP"
    step numpy_staged
    if [ -f "$TOP/tools/records/questions.py" ] && [ "$TOP" = "$ROOT" ]; then
        for t in questions evidence open_rows evidence_log citations register_coverage \
                 check_refs spec_coverage; do
            step "$PY" "tools/records/$t.py" --check
        done
        step "$PY" tools/clean-room/glossary.py --check
    fi
    "$PY" "$HERE/hooks/corrections.py" "$TOP" || true
else
    cd "$ROOT" || exit 2
    step cargo test --release -p sgx-pipe
    step cargo test --release -p sgx-sim
    step cargo clippy --workspace --all-targets
    step cargo fmt --check
    step make -C userspace/libsgxfive check
    step "$PY" -m pytest -q
    for t in questions evidence datasets frozen open_rows evidence_log citations register_coverage \
             check_refs spec_coverage; do
        step "$PY" "tools/records/$t.py" --check
    done
    step "$PY" tools/clean-room/glossary.py --check
    step "$PY" doc/isa/build.py --check
    step reuse lint
    step "$PY" tools/clean-room/guard.py --tree "$ROOT"
    step numpy_tracked
fi

[ "$mode" = list ] && exit 0
if [ ${#failed[@]} -gt 0 ]; then
    echo "check: $steps steps, ${#failed[@]} failed:"
    printf '  %s\n' "${failed[@]}"
    exit 1
fi
echo "check: $steps steps, all passed"
