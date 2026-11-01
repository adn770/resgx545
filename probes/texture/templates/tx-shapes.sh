#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# 11.32 tx-shapes (Q104): the levels of a non-square chain: offsets, sizes, count, per LOD
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
KEEP=${KEEP:-$HOME/p1132-dumps/tx-shapes}
GATE=0
EVERY=0
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
shp-32x16-l0	tx-shapes__0.bin	fit	safe	-	-
shp-32x16-l1	tx-shapes__1.bin	fit	safe	-	-
shp-32x16-l2	tx-shapes__2.bin	fit	safe	-	-
shp-32x16-l3	tx-shapes__3.bin	fit	safe	-	-
shp-32x16-l4	tx-shapes__4.bin	fit	safe	-	-
shp-32x16-l5	tx-shapes__5.bin	fit	safe	-	-
shp-32x16-l6	tx-shapes__6.bin	fit	safe	-	-
shp-32x16-l7	tx-shapes__7.bin	fit	safe	-	-
shp-32x32-l0	tx-shapes__8.bin	control	safe	72cea6a2f232c45b6f4ae5f38e08e20873924a4a6b7f71cf4d44b02ccf6c106b	-
shp-32x32-l1	tx-shapes__9.bin	control	safe	39bc87e4bed1c8487a6b6d9b0e56fd3eadc331d2c24d54ee13110cb32cb2d59b	-
shp-32x32-l2	tx-shapes__10.bin	control	safe	26405730d9f92bd914c90d44674cd02984caded0d6b307865a6b24a39bf0987f	-
shp-32x32-l3	tx-shapes__11.bin	control	safe	c33b9b90e94f19cbdaf451c9c661104ccb206515c4814bd4ad8d2b38c53cdb59	-
shp-32x32-l4	tx-shapes__12.bin	control	safe	f21c33714e7c2f80eec100bea04fc31946e8313f15090c3d98e5b9c9b5a09c2f	-
shp-32x32-l5	tx-shapes__13.bin	control	safe	50664534cb381b23b3dd385cae692afe6a87cec61a576d6cb288d7d3442384f1	-
shp-32x32-l6	tx-shapes__14.bin	control	safe	50664534cb381b23b3dd385cae692afe6a87cec61a576d6cb288d7d3442384f1	-
shp-128x16-l0-x0	tx-shapes__15.bin	heldout	safe	-	-
shp-128x16-l0-x64	tx-shapes__16.bin	heldout	safe	-	-
shp-128x16-l1-x0	tx-shapes__17.bin	heldout	safe	-	-
shp-128x16-l1-x64	tx-shapes__18.bin	heldout	safe	-	-
shp-128x16-l2-x0	tx-shapes__19.bin	heldout	safe	-	-
shp-128x16-l2-x64	tx-shapes__20.bin	heldout	safe	-	-
shp-128x16-l3-x0	tx-shapes__21.bin	heldout	safe	-	-
shp-128x16-l3-x64	tx-shapes__22.bin	heldout	safe	-	-
shp-128x16-l4-x0	tx-shapes__23.bin	heldout	safe	-	-
shp-128x16-l4-x64	tx-shapes__24.bin	heldout	safe	-	-
shp-128x16-l5-x0	tx-shapes__25.bin	heldout	safe	-	-
shp-128x16-l5-x64	tx-shapes__26.bin	heldout	safe	-	-
shp-128x16-l6-x0	tx-shapes__27.bin	heldout	safe	-	-
shp-128x16-l6-x64	tx-shapes__28.bin	heldout	safe	-	-
shp-128x16-l7-x0	tx-shapes__29.bin	heldout	safe	-	-
shp-128x16-l7-x64	tx-shapes__30.bin	heldout	safe	-	-
shp-128x16-l8-x0	tx-shapes__31.bin	heldout	safe	-	-
shp-128x16-l8-x64	tx-shapes__32.bin	heldout	safe	-	-
shp-16x32-l0	tx-shapes__33.bin	heldout	safe	-	-
shp-16x32-l1	tx-shapes__34.bin	heldout	safe	-	-
shp-16x32-l2	tx-shapes__35.bin	heldout	safe	-	-
shp-16x32-l3	tx-shapes__36.bin	heldout	safe	-	-
shp-16x32-l4	tx-shapes__37.bin	heldout	safe	-	-
shp-16x32-l5	tx-shapes__38.bin	heldout	safe	-	-
shp-16x32-l6	tx-shapes__39.bin	heldout	safe	-	-
shp-64x4-l0	tx-shapes__40.bin	heldout	safe	-	-
shp-64x4-l1	tx-shapes__41.bin	heldout	safe	-	-
shp-64x4-l2	tx-shapes__42.bin	heldout	safe	-	-
shp-64x4-l3	tx-shapes__43.bin	heldout	safe	-	-
shp-64x4-l4	tx-shapes__44.bin	heldout	safe	-	-
shp-64x4-l5	tx-shapes__45.bin	heldout	safe	-	-
shp-64x4-l6	tx-shapes__46.bin	heldout	safe	-	-
shp-64x4-l7	tx-shapes__47.bin	heldout	safe	-	-
shp-8x64-l0-y0	tx-shapes__48.bin	heldout	safe	-	-
shp-8x64-l0-y32	tx-shapes__49.bin	heldout	safe	-	-
shp-8x64-l1-y0	tx-shapes__50.bin	heldout	safe	-	-
shp-8x64-l1-y32	tx-shapes__51.bin	heldout	safe	-	-
shp-8x64-l2-y0	tx-shapes__52.bin	heldout	safe	-	-
shp-8x64-l2-y32	tx-shapes__53.bin	heldout	safe	-	-
shp-8x64-l3-y0	tx-shapes__54.bin	heldout	safe	-	-
shp-8x64-l3-y32	tx-shapes__55.bin	heldout	safe	-	-
shp-8x64-l4-y0	tx-shapes__56.bin	heldout	safe	-	-
shp-8x64-l4-y32	tx-shapes__57.bin	heldout	safe	-	-
shp-8x64-l5-y0	tx-shapes__58.bin	heldout	safe	-	-
shp-8x64-l5-y32	tx-shapes__59.bin	heldout	safe	-	-
shp-8x64-l6-y0	tx-shapes__60.bin	heldout	safe	-	-
shp-8x64-l6-y32	tx-shapes__61.bin	heldout	safe	-	-
shp-8x64-l7-y0	tx-shapes__62.bin	heldout	safe	-	-
shp-8x64-l7-y32	tx-shapes__63.bin	heldout	safe	-	-
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
