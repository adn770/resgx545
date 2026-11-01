; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; An integer loop of known length: ITER iterations of eight instructions (instructions 4
; to 11: six integer multiply-adds, the counter's decrement with a test of the result, the
; branch back to instruction 4), then o0 = the counter (0).
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #{ITER}
mov.skipinv r2, #0xFFFFFFFF
mov.skipinv r3, #0x00000003
imae.u r4, r3.low, r3.low, r3, u32
imae.u r5, r3.low, r3.low, r3, u32
imae.u r6, r3.low, r3.low, r3, u32
imae.u r7, r3.low, r3.low, r3, u32
imae.u r8, r3.low, r3.low, r3, u32
imae.u r9, r3.low, r3.low, r3, u32
iadd32.skipinv.testtanz.chan0 r1, p0, r1, r2
p0 ba #0x00000004
mov.skipinv.end o0, r1
