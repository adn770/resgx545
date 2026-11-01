# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# The registers the microkernel touches directly, from the cut firmware's stored images.
# Needs usse-dis built (tools/usse-dis: make usse-dis) and the GPL DDK's sgx545defs.h.
set -eu
IMAGES=${RESGX545_FW_IMAGES:?the images/ directory of the firmware-images capture}
DIS=${RESGX545_USSE_DIS:?the usse-dis binary}
: "${RESGX545_REGDEFS:?sgx545defs.h of the GPL DDK}"
"$DIS" "$IMAGES/00_ukernel.bin" > ukernel.dis
python3 regtouch.py ukernel.dis > "$OUT/regtouch.txt"
rm -f ukernel.dis
n=$(wc -l < "$OUT/regtouch.txt")
echo "regtouch: $n lines"
