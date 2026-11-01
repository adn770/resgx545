; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_task.s -- a two-phase pixel shader (slot pixel) asking whether phase 1 waits for its
; whole task's phase 0 ({OP}: parallel or perinstance): phase 0 adds 1 under lock #0 (one
; reads that dword back. The pixel is (g21 & 1023) << 16 | count: with a barrier every pixel of
; a task reads the same, final count. The host relocates the first phas's next phase.
phas #16, #8, pixel, {OP}
mov.skipinv r3, #1023
and.skipinv r5, g21, r3
shl.skipinv r6, r5, #2
mov.skipinv r4, #0x5CAF0000
iadd32.skipinv.testtaz.chan0 r4, p3, r6, r4
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
mov.skipinv r3, #1023
and.skipinv r5, g21, r3
shl.skipinv r6, r5, #2
mov.skipinv r4, #0x5CAF0000
iadd32.skipinv.testtaz.chan0 r4, p3, r6, r4
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
shl.skipinv r6, r5, #16
mov.skipinv r3, #0xFFFF
and.skipinv r2, r2, r3
or.skipinv r2, r2, r6
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
