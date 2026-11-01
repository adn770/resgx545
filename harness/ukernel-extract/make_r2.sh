#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Make sgx545_ukernel.r2, the radare2 annotation script for the SGX545 ukernel, from your own
# copy of the firmware. The script annotates closed code, so this repository does not carry
# it (it is gitignored here); a copy made from the Cedarview build is in
# resgx545-data-private, firmware/r2/ (README.md gives its SHA-256). It joins:
#   1. EDM command-handler labels, from the captured init info (initinfo.py);
#   2. hand-written labels and comments (sgx545_labels.r2);
#   3. a register-name comment on every firmware MMIO access (tools/usse-dis/regtouch.py);
#   4. a flag per touched register in the ESIL register-file window, for emulation with the
#      radare2 fork (tools/usse-dis/r2/README.md, "Emulation").
# usse-dis and regtouch.py arrive with the disassembly unit.
#
#   make_r2.sh [OUT]          OUT defaults to sgx545_ukernel.r2 beside this script
#
# Inputs: $RESGX545_UKERNEL, the cut ukernel image (00_ukernel.bin of the firmware-images
# dataset); $RESGX545_INITINFO, srvinit's boot payload (default: devinitpart2_in.bin of the
# layout_base capture in resgx545-data-private).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT="$HERE/../.."
PY="$ROOT/.venv/bin/python"
DATA="${RESGX545_DATA_PRIVATE:-$ROOT/../resgx545-data-private}"
UKERNEL="${RESGX545_UKERNEL:?set RESGX545_UKERNEL to the cut ukernel image}"
INITINFO="${RESGX545_INITINFO:-$DATA/firmware/layout/layout_base/devinitpart2_in.bin}"
OUT="${1:-$HERE/sgx545_ukernel.r2}"
[ -x "$PY" ] || {
    echo "make_r2.sh: $PY not found; create the virtual environment first" \
        "(python3 -m venv .venv in the repository root)" >&2
    exit 1
}
[ -x "$ROOT/tools/usse-dis/usse-dis" ] || {
    echo "make_r2.sh: $ROOT/tools/usse-dis/usse-dis not built; run make -C tools/usse-dis" >&2
    exit 1
}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
"$PY" "$HERE/initinfo.py" "$INITINFO" --r2 "$TMP/handlers.r2" >/dev/null
"$ROOT/tools/usse-dis/usse-dis" "$UKERNEL" > "$TMP/uk.txt"
(cd "$ROOT" && "$PY" tools/usse-dis/regtouch.py "$TMP/uk.txt" --r2 "$TMP/regs.r2" \
    --r2-flags "$TMP/crflags.r2" >/dev/null)
cat "$TMP/handlers.r2" "$HERE/sgx545_labels.r2" "$TMP/regs.r2" "$TMP/crflags.r2" > "$OUT"
echo "wrote $OUT ($(wc -l < "$OUT") lines)"
