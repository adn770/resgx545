#!/bin/bash
# stage-p1132.sh: Mac side. Regenerates the programs, tables, scripts and declarations (gen/gen_p1132.py,
# which assembles with the landed usse-asm and pds-asm, reads the landed tree (~/src/resgx545) and writes nothing there),
# checks that nothing changed in the declared files, and, with SGX_TARGET_HOST set, copies the programs to
# the laptop's ~/sgxprobes-stage-1132 and the scripts to ~/p1132. No laptop is needed for the build.
set -eu
export PYTHONDONTWRITEBYTECODE=1
P=$(cd "$(dirname "$0")" && pwd)
cd "$P"
python3 -B gen/gen_p1132.py | tee out/gen.txt
grep -q "^declared.tsv $(cat out/declared.sha256)" out/gen.txt || { echo "declared.tsv changed since it was hashed"; exit 1; }
grep -q "^predictions-declared.tsv $(cat out/predictions.sha256)" out/gen.txt || { echo "predictions changed since they were hashed"; exit 1; }
for f in tx-*.sh run-all-1132.sh; do bash -n "$f"; done
if [ -n "${SGX_TARGET_HOST:-}" ]; then
	ssh ${SGX_TARGET_SSH_OPTS:-} "$SGX_TARGET_HOST" 'mkdir -p sgxprobes-stage-1132 p1132'
	scp -q ${SGX_TARGET_SSH_OPTS:-} stage-bins/*.bin "$SGX_TARGET_HOST:sgxprobes-stage-1132/"
	scp -q ${SGX_TARGET_SSH_OPTS:-} tx-*.sh run-all-1132.sh "$SGX_TARGET_HOST:p1132/"
	echo "copied to $SGX_TARGET_HOST: programs in sgxprobes-stage-1132, scripts in p1132 (run: bash p1132/run-all-1132.sh)"
fi
