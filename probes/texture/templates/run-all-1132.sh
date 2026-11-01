#!/bin/bash
# run-all-1132.sh: the 11.32 batch on the laptop in the order of plan.md section 8 (the gate first, the
# safe scripts, then the two risky ones last, one job at a time with a health check after each), each with
# its own log. Run it on the laptop after stage-p1132.sh has put the programs in ~/sgxprobes-stage-1132;
# the tool is ~/sgxfive-test-1126. It stops after the first script that stopped itself (the gate, three
# failed recoveries): read dmesg before another run. Never writes a clock-gate register: no script here
# writes a register.
set -u
cd "$(dirname "$0")"
OUT=${OUT:-$HOME/p1132-out}
mkdir -p "$OUT"
for s in tx-gate tx-twiddle tx-shapes tx-fields tx-lod tx-border tx-t3 tx-types tx-formats tx-douti4 tx-t3-risky tx-types-risky; do
	echo "#### $s $(date +%T)"
	bash "./$s.sh" > "$OUT/$s.out" 2>&1
	rc=$?
	echo "rc $rc, $(grep -c '^== ' "$OUT/$s.out") jobs, $(grep -c 'kept ' "$OUT/$s.out") kept, $(grep -c 'MISMATCH' "$OUT/$s.out") declared mismatches"
	grep -E "^## abort|^  health|^## journalctl" "$OUT/$s.out" | head -4
	[ "$rc" -ne 0 ] && { echo "stopped after $s"; break; }
done
