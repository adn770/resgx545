#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# usage: recheck.sh BASE TIP     (run in the fork clone that holds BASE..TIP)
#
# The series check of a fork's commits on a build host: bundle BASE..TIP to the host's clone,
# send fork-check.sh, run it there, and only if every commit has a PASS line and none FAILs
# write the pass file naming TIP. fork-land.sh lands a tip only when the pass file names it.
#
# Environment (tools/bringup/local.env is sourced when present):
#   FORK_CHECK_HOST     ssh destination (default: SGX_BUILD_HOST, else sgx-build)
#   FORK_CHECK_SSH      the ssh command (default: ssh -o BatchMode=yes HOST); a test sets sh -c
#   FORK_CHECK_CLONE    the host's clone, relative to its $HOME (required)
#   FORK_CHECK_RUNNER   docker (default) or chroot (the laptop's build root)
#   FORK_CHECK_WORK     the host's build and log directory (default: the script's own)
#   FORK_CHECK_SCRIPT   the check script to send (default: fork-check.sh beside this one)
#   FORK_PASS_FILE      where the tested tip is written (default: <git dir>/fork-check.pass)
#   FORK_CHECK_LOG      the log file (default: <git dir>/fork-check.log)
#   CHECK_DRY_RUN=1     print the commands the check would run; nothing is built or recorded
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
LOCAL=$HERE/../bringup/local.env
[ -f "$LOCAL" ] && . "$LOCAL"
BASE=${1:-}
TIP=${2:-}
[ -n "$BASE" ] && [ -n "$TIP" ] || { echo "usage: recheck.sh BASE TIP" >&2; exit 2; }
CLONE=${FORK_CHECK_CLONE:-}
[ -n "$CLONE" ] || { echo "recheck.sh: FORK_CHECK_CLONE is not set" >&2; exit 2; }
TIP=$(git rev-parse --verify -q "$TIP^{commit}") || { echo "recheck.sh: no such tip" >&2; exit 1; }
BASE=$(git rev-parse --verify -q "$BASE^{commit}") || { echo "recheck.sh: no such base" >&2; exit 1; }
GITDIR=$(git rev-parse --git-common-dir)
PASSFILE=${FORK_PASS_FILE:-$GITDIR/fork-check.pass}
LOG=${FORK_CHECK_LOG:-$GITDIR/fork-check.log}
SCRIPT=${FORK_CHECK_SCRIPT:-$HERE/fork-check.sh}
SSH=${FORK_CHECK_SSH:-ssh -o BatchMode=yes ${FORK_CHECK_HOST:-${SGX_BUILD_HOST:-sgx-build}}}
RUNNER=${FORK_CHECK_RUNNER:-docker}
REMOTE=check-${TIP:0:12}.sh
n=$(git rev-list --count "$BASE..$TIP")
[ "$n" -gt 0 ] || { echo "recheck.sh: $BASE..$TIP is empty" >&2; exit 1; }

rm -f "$PASSFILE"                       # a stale pass never outlives a new run
# a bundle needs a ref to name: a temporary one, removed again
git update-ref refs/fork-recheck/tip "$TIP"
git bundle create - "refs/fork-recheck/tip" "^$BASE" 2>/dev/null |
    $SSH "cd && cd $CLONE && git bundle unbundle /dev/stdin >/dev/null"
sent=$?
git update-ref -d refs/fork-recheck/tip
[ $sent -eq 0 ] || exit 1
$SSH "cd && cd $CLONE && git rev-parse --verify -q $TIP >/dev/null" ||
    { echo "recheck.sh: the tip is not in the host's clone: stop" >&2; exit 1; }
$SSH "cd && cat > $REMOTE" < "$SCRIPT" || exit 1
work=
[ -n "${FORK_CHECK_WORK:-}" ] && work="CHECK_WORK=$FORK_CHECK_WORK"
$SSH "cd && cd $CLONE && CHECK_DRY_RUN=${CHECK_DRY_RUN:-} CHECK_RUNNER=$RUNNER $work sh ~/$REMOTE $BASE $TIP" 2>&1 | tee "$LOG"
[ -n "${CHECK_DRY_RUN:-}" ] && exit 0

pass=$(grep -c '^PASS ' "$LOG")
bad=$(grep -c '^FAIL ' "$LOG")
if [ "$bad" -ne 0 ] || [ "$pass" -lt "$n" ]; then
    echo "series check: $pass PASS, $bad FAIL ($n commits need a PASS each): nothing recorded"
    exit 1
fi
for c in $(git rev-list "$BASE..$TIP"); do
    grep -q "^PASS ${c:0:12} " "$LOG" || { echo "series check: no PASS for ${c:0:12}: nothing recorded"; exit 1; }
done
echo "$TIP" > "$PASSFILE"
echo "series check passed: $pass PASS for $n commits, tip $TIP"
