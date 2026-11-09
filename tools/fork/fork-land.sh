#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: fork-land.sh HOME BRANCH BASE TIP
#
# Land a fork series: move BRANCH in the fork's home repository to TIP, only if
#   - BASE..TIP, every message and blob, passes the clean-room guard (fork patterns on),
#   - TIP is a fast-forward of BRANCH (landed commits never change) and BRANCH is not
#     checked out in a worktree,
#   - the series check passed for exactly this TIP: the pass file (recheck.sh) names it; when
#     it does not, FORK_CHECK_CMD (default recheck.sh, run in HOME) is run first, and the pass
#     file must name TIP afterwards.
# Nothing is pushed. FORK_LAND_DRY_RUN=1 does everything but the move. The environment is
# recheck.sh's (FORK_PASS_FILE, FORK_CHECK_*) and the guard's (RESGX545_GUARD_DIR,
# RESGX545_REQUIRE_GUARD, default 1 here).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(dirname "$(dirname "$HERE")")
[ $# -eq 4 ] || { echo "usage: fork-land.sh HOME BRANCH BASE TIP" >&2; exit 2; }
FHOME=$1 BRANCH=$2
die() { echo "fork-land: $*" >&2; exit 1; }
g() { git -C "$FHOME" "$@"; }
PY=python3
[ -x "$ROOT/.venv/bin/python" ] && PY="$ROOT/.venv/bin/python"
export RESGX545_REQUIRE_GUARD=${RESGX545_REQUIRE_GUARD:-1}

TIP=$(g rev-parse --verify -q "$4^{commit}") || die "no such tip $4"
BASE=$(g rev-parse --verify -q "$3^{commit}") || die "no such base $3"
OLD=$(g rev-parse --verify -q "refs/heads/$BRANCH") || die "no branch $BRANCH in $FHOME"
g merge-base --is-ancestor "$BASE" "$TIP" || die "the base is not below the tip"
g merge-base --is-ancestor "$OLD" "$TIP" || die "$BRANCH is not an ancestor of the tip: landed commits never change"
g worktree list --porcelain | grep -qx "branch refs/heads/$BRANCH" &&
    die "$BRANCH is checked out in a worktree of $FHOME"

"$PY" "$ROOT/tools/clean-room/guard.py" --history "$FHOME" --ref "$TIP" --base "$BASE" --fork ||
    die "the guard refused the series (or its data is absent)"

PASSFILE=${FORK_PASS_FILE:-$(g rev-parse --path-format=absolute --git-common-dir)/fork-check.pass}
export FORK_PASS_FILE=$PASSFILE
tested=$(cat "$PASSFILE" 2>/dev/null || true)
if [ "$tested" != "$TIP" ]; then
    echo "fork-land: the series check has not passed for $TIP; running it"
    (cd "$FHOME" && ${FORK_CHECK_CMD:-$HERE/recheck.sh} "$BASE" "$TIP") ||
        die "the series check failed"
    tested=$(cat "$PASSFILE" 2>/dev/null || true)
fi
[ "$tested" = "$TIP" ] || die "the pass file names ${tested:-nothing}, not $TIP"

if [ -n "${FORK_LAND_DRY_RUN:-}" ]; then
    echo "fork-land: dry run: would move $BRANCH $OLD -> $TIP"
    exit 0
fi
g update-ref -m "fork-land: $BRANCH to $TIP" "refs/heads/$BRANCH" "$TIP" "$OLD" || die "update-ref failed"
echo "fork-land: $BRANCH $OLD -> $TIP"
