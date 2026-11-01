; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_helpers.s -- a triangle's pixel shader (slot pixel) recording which instances run: with
; no .skipinv anywhere, each instance stores 0xA0000000 | (g18 & 15) << 8 | g25 to scratch
; dword (g18 & 15) * 512 + g24 * 32 + g23 (its tile's number and its place in the 32x16
; is a helper instance that ran, whether or not its o0 lands.
phas #0, #0, pixel, end, parallel
mov r4, #0x5CAF0000
mov r3, #15
and r2, g18, r3
shl r1, g24, #5
or r1, r1, g23
shl r5, r2, #9
or r1, r1, r5
shl r1, r1, #2
iadd32.testtaz.chan0 r4, p3, r1, r4
shl r5, r2, #8
or r5, r5, g25
or r5, r5, #0xA0000000
stad [r4,+#0], r5
idf drc0, bif
wdf drc0
mov.end o0, {OUT}
