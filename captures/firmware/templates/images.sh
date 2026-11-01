# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Cut sgx545_ukernel.fw from libsrv_init.so; keep its code images as stored in the file
# (images/, unpatched: what the disassemblers read) and as loaded at the harness's base layout
# (loaded_base/).
set -eu
LIBS=${RESGX545_CDV_LIBS:?the usr/lib/ directory of your Cedarview package}
[ -f fwcutter.py ] || {
    echo "images.sh: fwcutter.py is not in the work directory ($PWD)" >&2
    exit 1
}
python3 fwcutter.py cut "$LIBS/libsrv_init.so.1.7.862890" -o "$OUT/sgx545_ukernel.fw"
python3 fwcutter.py info "$OUT/sgx545_ukernel.fw" > "$OUT/info.txt"
python3 - "$OUT/sgx545_ukernel.fw" "$OUT/images" <<'PY'
import pathlib, sys
import facts, fwformat
fw = fwformat.unpack(pathlib.Path(sys.argv[1]).read_bytes())
out = pathlib.Path(sys.argv[2])
out.mkdir(exist_ok=True)
for i, img in sorted(fw.images.items()):
    (out / f"{i:02d}_{facts.BUFFER_NAMES[i]}.bin").write_bytes(img)
PY
python3 fwload.py "$OUT/sgx545_ukernel.fw" layout_base.json -o "$OUT/loaded_base" \
    > "$OUT/load.txt"
echo "cut, $(ls "$OUT/images" | wc -l | tr -d " ") stored images, loaded at the base layout"
