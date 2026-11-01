#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# 11.32 tx-t3 (Q078,Q078,Q115): T3's unexplained bits and its low byte in smp
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
KEEP=${KEEP:-$HOME/p1132-dumps/tx-t3}
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
s64x32-ctl	tx-t3bits__0.bin	control	safe	ca07c5b21037e0b6e0955790ec54e9ef669c17a1d3f3d19a14e81c8d27fea3a4	-
s64x32-t3b0	tx-t3bits__1.bin	fit	safe	-	-
s64x32-t3b1	tx-t3bits__2.bin	fit	safe	-	-
s64x32-t3b2	tx-t3bits__3.bin	fit	safe	-	-
s64x32-t3b3	tx-t3bits__4.bin	fit	safe	-	-
s64x32-t3b4	tx-t3bits__5.bin	fit	safe	-	-
s64x32-t3b5	tx-t3bits__6.bin	fit	safe	-	-
s64x32-t3b6	tx-t3bits__7.bin	fit	safe	-	-
s64x32-t3b7	tx-t3bits__8.bin	fit	safe	-	-
s64x32-t3b8	tx-t3bits__9.bin	fit	safe	-	-
s64x32-t3b9	tx-t3bits__10.bin	fit	safe	-	-
s64x32-t3b10	tx-t3bits__11.bin	fit	safe	-	-
s64x32-t3b11	tx-t3bits__12.bin	fit	safe	-	-
s64x32-t3b12	tx-t3bits__13.bin	fit	safe	-	-
s64x32-t3b14	tx-t3bits__14.bin	fit	safe	-	-
s64x32-t3b18	tx-t3bits__15.bin	fit	safe	-	-
s64x32-t3b20	tx-t3bits__16.bin	fit	safe	-	-
s64x32-t3b21	tx-t3bits__17.bin	fit	safe	-	-
s64x32-t3b22	tx-t3bits__18.bin	fit	safe	-	-
s64x32-t3b27	tx-t3bits__19.bin	fit	safe	-	-
s64x32-t3b28	tx-t3bits__20.bin	fit	safe	-	-
s64x32-t0b27	tx-t3bits__21.bin	fit	safe	-	-
s64x32-t0b30	tx-t3bits__22.bin	fit	safe	-	-
s64x16-ctl	tx-t3bits__23.bin	control	safe	6dea3847b409dcf5f891daa65eb33386502e64482b986108b5002856804dc87d	-
s64x16-t3b10	tx-t3bits__24.bin	heldout	safe	-	-
s64x16-t3b14	tx-t3bits__25.bin	heldout	safe	-	-
s64x16-t3b18	tx-t3bits__26.bin	heldout	safe	-	-
s64x16-t3b27	tx-t3bits__27.bin	heldout	safe	-	-
s64x16-t3b28	tx-t3bits__28.bin	heldout	safe	-	-
s32x32-t3b14	tx-t3bits__29.bin	heldout	safe	-	-
s32x32-t3b18	tx-t3bits__30.bin	heldout	safe	-	-
s32x32-t3b27	tx-t3bits__31.bin	heldout	safe	-	-
s32x32-t3b28	tx-t3bits__32.bin	heldout	safe	-	-
tw32-ctl	tx-t3bits__33.bin	control	safe	72cea6a2f232c45b6f4ae5f38e08e20873924a4a6b7f71cf4d44b02ccf6c106b	-
tw32-t3b0	tx-t3bits__34.bin	heldout	safe	-	-
tw32-t3b4	tx-t3bits__35.bin	heldout	safe	-	-
tw32-t3b10	tx-t3bits__36.bin	heldout	safe	-	-
tw32-t3b14	tx-t3bits__37.bin	heldout	safe	-	-
tw32-t3b18	tx-t3bits__38.bin	heldout	safe	-	-
tw32-t3b27	tx-t3bits__39.bin	heldout	safe	-	-
tw32-t3b28	tx-t3bits__40.bin	heldout	safe	-	-
sv-01	tx-t3vals__0.bin	fit	safe	-	-
sv-02	tx-t3vals__1.bin	fit	safe	-	-
sv-03	tx-t3vals__2.bin	fit	safe	-	-
sv-04	tx-t3vals__3.bin	fit	safe	-	-
sv-05	tx-t3vals__4.bin	fit	safe	-	-
sv-06	tx-t3vals__5.bin	fit	safe	-	-
sv-07	tx-t3vals__6.bin	fit	safe	-	-
sv-08	tx-t3vals__7.bin	fit	safe	-	-
sv-09	tx-t3vals__8.bin	fit	safe	-	-
sv-0a	tx-t3vals__9.bin	fit	safe	-	-
sv-0b	tx-t3vals__10.bin	fit	safe	-	-
sv-0c	tx-t3vals__11.bin	fit	safe	-	-
sv-0d	tx-t3vals__12.bin	fit	safe	-	-
sv-0e	tx-t3vals__13.bin	fit	safe	-	-
sv-0f	tx-t3vals__14.bin	fit	safe	-	-
sv-10	tx-t3vals__15.bin	fit	safe	-	-
sv-20	tx-t3vals__16.bin	fit	safe	-	-
sv-30	tx-t3vals__17.bin	fit	safe	-	-
sv-40	tx-t3vals__18.bin	fit	safe	-	-
sv-50	tx-t3vals__19.bin	fit	safe	-	-
sv-60	tx-t3vals__20.bin	fit	safe	-	-
sv-70	tx-t3vals__21.bin	fit	safe	-	-
sv-80	tx-t3vals__22.bin	fit	safe	-	-
sv-90	tx-t3vals__23.bin	fit	safe	-	-
sv-a0	tx-t3vals__24.bin	fit	safe	-	-
sv-b0	tx-t3vals__25.bin	fit	safe	-	-
sv-c0	tx-t3vals__26.bin	fit	safe	-	-
sv-d0	tx-t3vals__27.bin	fit	safe	-	-
sv-e0	tx-t3vals__28.bin	fit	safe	-	-
sv-f0	tx-t3vals__29.bin	fit	safe	-	-
sc-8b	tx-t3vals__30.bin	fit	safe	-	-
sc-c3	tx-t3vals__31.bin	fit	safe	-	-
sc-ed	tx-t3vals__32.bin	fit	safe	-	-
sc-d8	tx-t3vals__33.bin	fit	safe	-	-
sc-2e	tx-t3vals__34.bin	fit	safe	-	-
sc-ff	tx-t3vals__35.bin	fit	safe	-	-
sc-1a	tx-t3vals__36.bin	fit	safe	-	-
sc-56	tx-t3vals__37.bin	fit	safe	-	-
sc-96	tx-t3vals__38.bin	fit	safe	-	-
sc-a0	tx-t3vals__39.bin	fit	safe	-	-
sc-5b	tx-t3vals__40.bin	fit	safe	-	-
sc-c6	tx-t3vals__41.bin	fit	safe	-	-
sc-65	tx-t3vals__42.bin	fit	safe	-	-
sc-e6	tx-t3vals__43.bin	fit	safe	-	-
sc-e1	tx-t3vals__44.bin	fit	safe	-	-
sc-e4	tx-t3vals__45.bin	fit	safe	-	-
tv-m0-11	tx-t3vals__46.bin	heldout	safe	-	-
tv-m0-2f	tx-t3vals__47.bin	heldout	safe	-	-
tv-m0-f1	tx-t3vals__48.bin	heldout	safe	-	-
tv-m0-8f	tx-t3vals__49.bin	heldout	safe	-	-
tv-m0-79	tx-t3vals__50.bin	heldout	safe	-	-
tv-m0-a5	tx-t3vals__51.bin	heldout	safe	-	-
tv-m0-3c	tx-t3vals__52.bin	heldout	safe	-	-
tv-m0-c3	tx-t3vals__53.bin	heldout	safe	-	-
tv-m0-08	tx-t3vals__54.bin	heldout	safe	-	-
tv-m0-80	tx-t3vals__55.bin	heldout	safe	-	-
tv-m0-ff	tx-t3vals__56.bin	heldout	safe	-	-
tv-m0-01	tx-t3vals__57.bin	heldout	safe	-	-
tv-m1-11	tx-t3vals__58.bin	heldout	safe	-	-
tv-m1-8f	tx-t3vals__59.bin	heldout	safe	-	-
tv-m1-79	tx-t3vals__60.bin	heldout	safe	-	-
tv-m1-f1	tx-t3vals__61.bin	heldout	safe	-	-
tv-m1-3c	tx-t3vals__62.bin	heldout	safe	-	-
tv-m1-c3	tx-t3vals__63.bin	heldout	safe	-	-
tv-m2-11	tx-t3vals__64.bin	heldout	safe	-	-
tv-m2-8f	tx-t3vals__65.bin	heldout	safe	-	-
tv-m2-79	tx-t3vals__66.bin	heldout	safe	-	-
tv-m2-f1	tx-t3vals__67.bin	heldout	safe	-	-
tv-m2-3c	tx-t3vals__68.bin	heldout	safe	-	-
tv-m2-c3	tx-t3vals__69.bin	heldout	safe	-	-
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
