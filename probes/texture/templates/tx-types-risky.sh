#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# 11.32 tx-types-risky (Q113,Q114): RISKY, last: TEXTYPE 1, 2, 4, 5, 7 under smp2d and smp3d
# Run on the laptop after stage-p1132.sh has put the programs in ~/sgxprobes-stage-1132; the tool is
# ~/sgxfive-test-1126 (the landed userspace/libsgxfive). Raw outputs are KEPT: every job's whole tool
# output, gzip (mtime 0) in $KEEP/NAME.txt.gz, with its raw size and sha256 printed ("kept ..."), the
# case table in $KEEP/cases.tsv and the kernel log of the run in $KEEP/journal-k.txt.gz; the tool's standard
# error is kept apart (NAME.err.gz, when it is not empty) so that no message is mixed into a pixel row. Each job
# prints the sha256 of its 2048 pixels (raster order, 8 hex digits, comma joined) and, for the cases
# with a declared prediction under one named hypothesis, whether it matches; nothing is judged here:
# recompute/recompute_p1132.py recomputes everything from the kept dumps. No clock-gate register and
# no register at all is written by this script (no kreg, no kregnow, no /dev/mem write): the jobs are
# fills (probe --coords --pixels) and the only writes are debugfs reset and /dev/kmsg. Root: sudo -n.
set -u
T=${SGXFIVE_TEST:-$HOME/sgxfive-test-1126}
S=${SGXFIVE_PROBE_BINS:-$HOME/sgxprobes-stage-1132}
KEEP=${KEEP:-$HOME/p1132-dumps/tx-types-risky}
GATE=0
EVERY=1
D=$(sudo -n sh -c 'ls -d /sys/kernel/debug/dri/*/sgx' | head -n 1)
[ -x "$T" ] || { echo "no $T: build the landed userspace/libsgxfive for the laptop first"; exit 1; }
[ -n "$D" ] || { echo "no sgx debugfs directory (debug option off?)"; exit 1; }
mkdir -p "$KEEP"
START=$(date +%s)
echo "## uname"; uname -r
echo "## firmware"; sha256sum /lib/firmware/sgx545_ukernel.fw
echo "## installed module"; SRCV_FILE=$(modinfo -F srcversion gma500_gfx 2>/dev/null); echo "$SRCV_FILE"
echo "## loaded module"; SRCV_LOADED=$(sudo -n cat /sys/module/gma500_gfx/srcversion); echo "$SRCV_LOADED"
[ -n "$SRCV_FILE" ] && [ "$SRCV_FILE" = "$SRCV_LOADED" ] || { echo "the loaded module is not the installed one"; exit 1; }
echo "## tool"; sha256sum "$T"
echo "## clock"; date
reset_gpu() { echo 1 | sudo -n tee "$D/reset" >/dev/null; sleep 3; }
mark() { printf "resgx545 case %s %s\n" "$1" "$RUN" | sudo -n tee /dev/kmsg >/dev/null; }
RUN=$(date +%s)-$$
W=$(mktemp -d)
journal() { sudo -n journalctl -k --since "@$START" --no-pager 2>&1 | gzip -n -6 > "$KEEP/journal-k.txt.gz"
	echo "## journalctl -k: $(gzip -dc "$KEEP/journal-k.txt.gz" | wc -l | tr -d ' ') lines, $(gzip -dc "$KEEP/journal-k.txt.gz" | grep -ci 'sgxfive\|bif fault\|recovery' | tr -d ' ') naming sgxfive, a BIF fault or a recovery"; }
trap 'journal; rm -rf "$W"' EXIT
keep() { # NAME FILE: gzip the whole raw output, print its sizes and the raw sha256
	raw=$(wc -c < "$2" | tr -d ' ')
	sha=$(sha256sum "$2" | cut -d' ' -f1)
	gzip -n -6 -c "$2" > "$KEEP/$1.txt.gz"
	echo "  kept $1: $raw bytes raw, $(wc -c < "$KEEP/$1.txt.gz" | tr -d ' ') gz, raw sha256 $sha"
}
BAD=0
health() { # a plain triangle must still draw exactly; three failed recoveries stop the script
	sleep 3
	if sudo -n timeout 60 "$T" tri 2>&1 </dev/null | grep -q "^diff: 0 of 4096"; then BAD=0; echo "  health: ok"; return 0; fi
	reset_gpu; sleep 5
	if sudo -n timeout 60 "$T" tri 2>&1 </dev/null | grep -q "^diff: 0 of 4096"; then BAD=0; echo "  health: ok after a reset"; return 0; fi
	sleep 5
	if sudo -n timeout 60 "$T" tri 2>&1 </dev/null | grep -q "^diff: 0 of 4096"; then BAD=0; echo "  health: recovered on the retry"; return 0; fi
	BAD=$((BAD + 1)); echo "  health: the plain triangle does not draw ($BAD)"
	[ "$BAD" -ge 3 ] && { echo "## abort: the GPU did not recover three times"; exit 1; }
	return 1
}
health
PY=$(cat <<'PYEOF'
import collections, hashlib, re, sys
want = sys.argv[1] if len(sys.argv) > 1 else "-"
expect = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
c = collections.Counter()
vals = []
for line in sys.stdin:
    m = re.search(r"row (\d+): (.*)$", line)
    if not m:
        continue
    for v in m.group(2).split():
        v = v[2:] if v.startswith("0x") else v
        vals.append(v.rjust(8, "0"))
        c[v] += 1
sha = hashlib.sha256(",".join(vals).encode()).hexdigest()
top = " ".join("%s x%d" % kv for kv in c.most_common(3))
res = "" if want == "-" else ("  MATCH" if want == sha else "  MISMATCH (declared %s)" % want[:16])
print("  pixels %d: %d distinct; commonest %s" % (len(vals), len(c), top))
print("  pix sha256 %s%s" % (sha, res))
if len(vals) != expect:
    print("  PIXELS %d, not %d" % (len(vals), expect))
PYEOF
)


job() { # NAME BIN DECLARED_SHA [OPTION...]: one fill, kept whole
	name=$1; bin=$2; pred=$3; shift 3
	[ -f "$S/$bin" ] || { echo "no $S/$bin: run stage-p1132.sh and copy"; exit 1; }
	echo "== $name ($bin)"
	mark "$name"
	sudo -n timeout 120 "$T" probe --temps 32 --coords --pixels "$@" "$S/$bin" > "$W/$name.out" 2> "$W/$name.err" </dev/null
	rc=$?
	cat "$W/$name.err" >> "$W/$name.out.chk"; cat "$W/$name.out" >> "$W/$name.out.chk"
	echo "  rc $rc $(grep -E 'failed|FAILED|faulted|hung' "$W/$name.out.chk" | head -1 | cut -c1-100)"
	python3 -c "$PY" "$pred" < "$W/$name.out" | tee "$W/$name.red"
	keep "$name" "$W/$name.out"
	[ -s "$W/$name.err" ] && keep "$name.err" "$W/$name.err"
	if [ "$GATE" = 1 ] && [ "$pred" != "-" ] && ! grep -q "MATCH$" "$W/$name.red"; then
		echo "## abort: the gate case $name does not give its declared image"; exit 1
	fi
	if [ "$EVERY" = 1 ] || grep -qE "failed|faulted|hung" "$W/$name.out.chk" || [ "$rc" -ne 0 ]; then
		reset_gpu; health </dev/null || true
	fi
	rm -f "$W/$name.out" "$W/$name.err" "$W/$name.out.chk" "$W/$name.red"
}

printf 'name\tbin\tset\trisk\toptions\n' > "$KEEP/cases.tsv"
CASES=$(cat <<'TABLE'
rt1-2d	tx-types-risky__0.bin	explore	risky	-	-
rt1-3d-w5	tx-types-risky__1.bin	explore	risky	-	-
rt1-3d-w15	tx-types-risky__2.bin	explore	risky	-	-
rt2-2d	tx-types-risky__3.bin	explore	risky	-	-
rt2-3d-w5	tx-types-risky__4.bin	explore	risky	-	-
rt2-3d-w15	tx-types-risky__5.bin	explore	risky	-	-
rt4-2d	tx-types-risky__6.bin	explore	risky	-	-
rt4-3d-w5	tx-types-risky__7.bin	explore	risky	-	-
rt4-3d-w15	tx-types-risky__8.bin	explore	risky	-	-
rt5-2d	tx-types-risky__9.bin	explore	risky	-	-
rt5-3d-w5	tx-types-risky__10.bin	explore	risky	-	-
rt5-3d-w15	tx-types-risky__11.bin	explore	risky	-	-
rt7-2d	tx-types-risky__12.bin	explore	risky	-	-
rt7-3d-w5	tx-types-risky__13.bin	explore	risky	-	-
rt7-3d-w15	tx-types-risky__14.bin	explore	risky	-	-
TABLE
)
while IFS=$'\t' read -r name bin st risk pred opts; do
	[ "$opts" = "-" ] && opts=""
	opts=${opts//@S@/$S}
	printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$bin" "$st" "$risk" "$opts" >> "$KEEP/cases.tsv"
	job "$name" "$bin" "$pred" $opts
done < <(echo "$CASES")
health </dev/null || true

echo "## end"
