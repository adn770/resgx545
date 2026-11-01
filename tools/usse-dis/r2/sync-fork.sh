#!/bin/sh
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2026 Josep Torra
# Copy the clean-room cores into the radare2 fork (the argument, else $R2_FORK, else a
# checkout named radare2 beside this repository): the USSE decoder,
# its form table (generated from isa/usse/) and instruction families into libr/arch/p/usse/,
# and the PDS decoder with the PDS forms of tools/usse-asm into libr/arch/p/pds/. The PDS
# encoder runs on the USSE form engine, which the fork builds once, in the usse plugin.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
dis=$here/..
asm=$here/../../usse-asm
r2=${1:-${R2_FORK:-$here/../../../../radare2}}
[ -d "$r2/libr/arch/p/usse" ] || { echo "$r2: not a checkout of the radare2 fork" >&2; exit 1; }
u=$r2/libr/arch/p/usse
p=$r2/libr/arch/p/pds
cp "$dis/usse.c" "$dis/usse.h" "$dis/usse_form.c" "$dis/usse_form.h" "$dis/usse_table.inc" "$u/"
mkdir -p "$u/forms"
cp "$dis"/forms/*.inc "$u/forms/"
cp "$dis/pds.c" "$dis/pds.h" "$dis/pds_table.inc" "$asm/pds_forms.c" "$asm/pds_asm.h" "$p/"
cp "$dis/usse_form.h" "$p/"
