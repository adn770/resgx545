; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; fill_one_phase.s -- fill_phas_bar.s's code in one phase (its control): the quads with g39 4,
; 8 and 12 spin and store the marker to their 4x4 block's slot, the quad with g39 0 goes
; straight on, and every pixel then reads the slot, with no phase boundary between.
phas #0, #0, pixel, end, parallel
shr.skipinv r1, g24, #2
shl.skipinv r1, r1, #3
shr.skipinv r2, g23, #2
or.skipinv r1, r1, r2
mov.skipinv r2, #63
and.skipinv r2, g18, r2
shl.skipinv r2, r2, #5
or.skipinv r1, r1, r2
shl.skipinv r1, r1, #2
mov.skipinv r4, #0x5CAF0000
iadd32.skipinv.testtaz.chan0 r4, p3, r1, r4
mov.skipinv r3, #12
and.skipinv.testtaz.chan0 !c0, p0, g39, r3
p0 br #0x00000008
mov.skipinv r5, #0x1000
isub16.testtanz.chan0 r5, p1, r5, #1
p1 br -#0x00000001
mov.skipinv r6, #0x0BADF00D
stad.skipinv [r4,+#0], r6
idf drc0, bif
wdf drc0
nop
shr.skipinv r1, g24, #2
shl.skipinv r1, r1, #3
shr.skipinv r2, g23, #2
or.skipinv r1, r1, r2
mov.skipinv r2, #63
and.skipinv r2, g18, r2
shl.skipinv r2, r2, #5
or.skipinv r1, r1, r2
shl.skipinv r1, r1, #2
mov.skipinv r4, #0x5CAF0000
iadd32.skipinv.testtaz.chan0 r4, p3, r1, r4
ldad.skipinv r2, [r4,+#0], drc0
wdf drc0
mov.skipinv.end o0, r2
