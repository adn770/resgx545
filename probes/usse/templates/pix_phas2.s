; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas2.s -- a two-phase pixel shader (slot pixel) for phas's wait and instance mode:
; the first phas takes the case's wait and mode ({OP},
; e.g. "none, perinstance"); phase 0 leaves 0x00A5A500 in r5 and ends; phase 1 (instruction 6)
; adds 1 to scratch dword 0 without a lock, loads r5 into r6, and writes the value it stored
; ({OUT}: r2, or r6 to see whether a temporary survives the phase) as the pixel. Lost updates
; give repeated pixel values; instances run one at a time give every value once. The host
; relocates the first phas's next phase from the pixel code base.
phas #6, #8, pixel, {OP}
mov.skipinv r5, #0x00A5A500
mov.skipinv r6, #0x00C3C300
nop
nop
nop.end
mov.skipinv r4, #0x5CAF0000
mov.skipinv r3, #1
mov.skipinv r6, r5
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
iadd32.skipinv.testtaz.chan0 r2, p0, r3, r2
stad.skipinv [r4,+#0], r2
idf drc0, bif
wdf drc0
mov.skipinv o0, {OUT}
phas.end #0, #0, pixel, end, parallel
