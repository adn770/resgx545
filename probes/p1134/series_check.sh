#!/bin/bash
# Note 2026-11-09: the check script this copies lived in the retired rewrite kit; it is now
# tools/fork/fork-check.sh (same script) and the path below says so (it was also one level too
# high). Nothing else in this record changes.
# recheck1135.sh: the series check of the three phase 11.34 commits on the laptop, as p1129/recheck.sh
# does it (laptop's clone ~/src/linux-sgx-f1115, CHECK_RUNNER=chroot, CHECK_WORK=~/src/linux-sgx-checkout-check,
# incremental). With CHECK_DRY_RUN=1 only the commands are printed (nothing is built, no commit checked out).
# Writes recheck.pass (the tip) only when 6 or more lines PASS, none FAIL and all three subjects appear.
set -u
H=$(cd "$(dirname "$0")" && pwd)
BASE=3d9b8bdefe94
TIP=$(cut -d' ' -f3 "$H/commits.txt")
SSH="ssh -o HostKeyAlias=cedar -o BatchMode=yes jtorra@10.42.0.2"
CLONE=src/linux-sgx-f1115
LOG=$H/logs/recheck-series${CHECK_DRY_RUN:+-dry}.txt

[ "$(git -C "$H/fork" rev-parse p1135)" = "$TIP" ] || { echo "the fork's p1135 is not $TIP: stop"; exit 1; }
git -C "$H/fork" bundle create - $BASE..p1135 | $SSH "cd $CLONE && git bundle unbundle /dev/stdin >/dev/null" || exit 1
$SSH "cd $CLONE && git rev-parse --verify -q $TIP >/dev/null" || { echo "tip not in the clone: stop"; exit 1; }
scp -q -o HostKeyAlias=cedar "$H/../../tools/fork/fork-check.sh" jtorra@10.42.0.2:check1135.sh || exit 1
$SSH "cd $CLONE && CHECK_DRY_RUN=${CHECK_DRY_RUN:-} CHECK_WORK=\$HOME/src/linux-sgx-checkout-check CHECK_RUNNER=chroot sh ~/check1135.sh $BASE $TIP" 2>&1 | tee "$LOG"
[ -n "${CHECK_DRY_RUN:-}" ] && exit 0
n=$(grep -c '^PASS ' "$LOG")
bad=$(grep -c '^FAIL ' "$LOG")
if [ "$bad" -ne 0 ] || [ "$n" -lt 6 ]; then
	echo "series check: $n PASS, $bad FAIL (6 PASS needed): nothing installed"
	exit 1
fi
for s in "add a kpoke space for a render's background object" "keep the next closed render ctx" \
	 "add debugfs render_kept"; do
	grep -q "$s" "$LOG" || { echo "no line for '$s': nothing installed"; exit 1; }
done
echo "$TIP" > "$H/recheck.pass"
echo "series check passed: $n PASS"
