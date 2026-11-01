; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_bar2.s -- a two-phase pixel shader (slot pixel) asking whether phase 1 waits for
; the other instances' phase 0 ({OP}: phas's parallel or perinstance): in phase 0 the quads
; 4096 times and store 0x0BADF00D to scratch dword 1; the other quads go straight on. Phase 1
; (instruction 13) reads dword 1 as the pixel: a fast quad that reads its fill (0xd0000001)
; did not wait for the slow quads of its task. The host relocates the first phas's next phase.
phas #13, #8, pixel, {OP}
mov.skipinv r4, #0x5CAF0004
mov.skipinv r3, #2
and.skipinv.testtaz.chan0 !c0, p0, g24, r3
p0 br #0x00000008
mov.skipinv r5, #0x00001000
isub16.testtanz.chan0 r5, p1, r5, #1
p1 br -#0x00000001
mov.skipinv r6, #0x0BADF00D
stad.skipinv [r4,+#0], r6
idf drc0, bif
wdf drc0
nop.end
mov.skipinv r4, #0x5CAF0004
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
