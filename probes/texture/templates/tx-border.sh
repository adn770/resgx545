#!/bin/bash
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# 11.32 tx-border (Q050,Q078): the address modes 4 to 7 over coordinates from -1.5 to 2.5
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
KEEP=${KEEP:-$HOME/p1132-dumps/tx-border}
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
bd-u0	tx-border__0.bin	control	safe	b9dd08f3b4c32af01966f70fd89c81f5d9efe4a34d90ceb119f092bfc71ca18a	-
bd-v0	tx-border__1.bin	control	safe	d3b47a1157dc0f38ed152469e993a2d58e57a6bba0c05c2c94f0ec3816c8e7ab	-
bd-uv0	tx-border__2.bin	control	safe	cc11c8779e084d70ec85821d9105766c0b62f4e29cbae1937c059147a749215c	-
bd-u1	tx-border__3.bin	control	safe	3d143b0f4a068007671b31dfc3f9866e571e1ad83b64f1c7f79f6e6e097b3e9f	-
bd-v1	tx-border__4.bin	control	safe	e6fa79a43c0f20e7689b64f0d7bcff368f761c93777bc84f50316084ee88465d	-
bd-uv1	tx-border__5.bin	control	safe	e22bdf9f245d24a263b8223f6b8ad7a75a06659b319beb1c70620f5c9e008501	-
bd-u2	tx-border__6.bin	control	safe	358c67fabecaa0f92a48b9ecd454dd87ae5e6c2d2a0dbfa126be7967e1f42263	-
bd-v2	tx-border__7.bin	control	safe	3154adbd00b335ad6db4cee97a1e9858d4af4f1ce9fab64a4b06342e0f6d12ae	-
bd-uv2	tx-border__8.bin	control	safe	9ef2c7ff4983445d468c14aaab8bd2dc9b482246215cde1e90a0980410141de5	-
bd-u3	tx-border__9.bin	control	safe	f2df62bdbff0f0ff49af0795c648f333d3ccc95e2d232f9c20980f966d34229f	-
bd-v3	tx-border__10.bin	control	safe	36d2164c4fd6aadce30a6334a0ca1ab5e36b992b12c3aa70b07b5171aceb2ebd	-
bd-uv3	tx-border__11.bin	control	safe	6643f896480f478f4113efaa90c79cd29666b3efcfa6faa3186d4f9ae0774997	-
bd-u4	tx-border__12.bin	explore	safe	-	-
bd-v4	tx-border__13.bin	explore	safe	-	-
bd-uv4	tx-border__14.bin	explore	safe	-	-
bd-u5	tx-border__15.bin	explore	safe	-	-
bd-v5	tx-border__16.bin	explore	safe	-	-
bd-uv5	tx-border__17.bin	explore	safe	-	-
bd-u6	tx-border__18.bin	explore	safe	-	-
bd-v6	tx-border__19.bin	explore	safe	-	-
bd-uv6	tx-border__20.bin	explore	safe	-	-
bd-u7	tx-border__21.bin	explore	safe	-	-
bd-v7	tx-border__22.bin	explore	safe	-	-
bd-uv7	tx-border__23.bin	explore	safe	-	-
bd-hb-u4	tx-border__24.bin	heldout	safe	-	-
bd-hb-ns-uv4	tx-border__25.bin	heldout	safe	-	-
bd-hb-u5	tx-border__26.bin	heldout	safe	-	-
bd-hb-ns-uv5	tx-border__27.bin	heldout	safe	-	-
bd-hb-u6	tx-border__28.bin	heldout	safe	-	-
bd-hb-ns-uv6	tx-border__29.bin	heldout	safe	-	-
bd-hb-u7	tx-border__30.bin	heldout	safe	-	-
bd-hb-ns-uv7	tx-border__31.bin	heldout	safe	-	-
bd-st-u0	tx-border__32.bin	heldout	safe	-	-
bd-st-u4	tx-border__33.bin	heldout	safe	-	-
bd-st-u5	tx-border__34.bin	heldout	safe	-	-
bd-st-u6	tx-border__35.bin	heldout	safe	-	-
bd-st-u7	tx-border__36.bin	heldout	safe	-	-
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
