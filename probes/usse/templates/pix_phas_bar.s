; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_bar.s -- a two-phase pixel shader (slot pixel) asking whether phase 1 waits for
; every instance's phase 0 (phas's parallel against perinstance, {OP}): phase 0 adds 1 to
; scratch dword 0 under lock #0; phase 1 (instruction 12) reads it back as the pixel. With a
; barrier no instance reads less than its task's instance count; without one the first
; instances read small values. The host relocates the first phas's next phase.
phas #12, #8, pixel, {OP}
mov.skipinv r4, #0x5CAF0000
mov.skipinv r3, #1
lock #0
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
iadd32.skipinv.testtaz.chan0 r2, p0, r3, r2
stad.skipinv [r4,+#0], r2
idf drc0, bif
wdf drc0
release #0
nop.end
mov.skipinv r4, #0x5CAF0000
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
