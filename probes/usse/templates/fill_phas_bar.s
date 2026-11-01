; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; fill_phas_bar.s -- a two-phase fill shader (the fill's code starts at the code base, so phas
; names its local index) asking whether phase 1 waits for other quads' phase 0 ({MODE}:
; parallel or perinstance): every pixel takes the scratch slot of its 4x4-pixel block
; quad with g39 0 goes straight on;
; reads it as the pixel. A fast quad reading the slot's fill
; (0xD0000000 | slot) did not wait for its block's slow quads.
phas #23, #8, pixel, none, {MODE}
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
nop.end
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
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
