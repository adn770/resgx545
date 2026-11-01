#!/bin/bash
# stage-p1131.sh [DIR]: assemble the programs of p1131-progs.toml (the main files and the helper
# slots' files) into DIR (default ./stage-bins) with the landed usse-asm and pds-asm, and, with
# SGX_TARGET_HOST set, copy them to the laptop's ~/sgxprobes-stage (the scripts' SGXFIVE_PROBE_BINS),
# together with the scripts. Reads ~/src/resgx545, writes nothing there. No laptop is needed for
# the build.
set -eu
export PYTHONDONTWRITEBYTECODE=1
P=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$P/stage-bins}
mkdir -p "$OUT"
python3 -B - "$P/p1131-progs.toml" "$OUT" <<'PY'
import pathlib, sys
sys.path.insert(0, str(pathlib.Path.home() / "src/resgx545/tools/usse-asm"))
import probe
table = probe.load(pathlib.Path(sys.argv[1]))
src = pathlib.Path(sys.argv[1]).parent / "templates"
out = pathlib.Path(sys.argv[2])
for p in table:
    probe.build(p, out, src)
probe.build_helpers(table, out, src)
print("staged:", " ".join(sorted(f.name for f in out.glob("*.bin"))))
PY
if [ -n "${SGX_TARGET_HOST:-}" ]; then
	ssh ${SGX_TARGET_SSH_OPTS:-} "$SGX_TARGET_HOST" 'mkdir -p sgxprobes-stage p1131'
	scp -q ${SGX_TARGET_SSH_OPTS:-} "$OUT"/*.bin "$SGX_TARGET_HOST:sgxprobes-stage/"
	scp -q ${SGX_TARGET_SSH_OPTS:-} "$P"/*.sh "$SGX_TARGET_HOST:p1131/"
	echo "copied to $SGX_TARGET_HOST (bins to sgxprobes-stage, scripts to p1131)"
fi
