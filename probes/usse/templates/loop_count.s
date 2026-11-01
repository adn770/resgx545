; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A loop of known length: ITER iterations of eight instructions (instructions 3 to 10: six
; nops, the counter's decrement with a test of the result, the branch back to instruction 3),
; so 8 x ITER instructions run, then o0 = the counter (0).
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #{ITER}
mov.skipinv r2, #0xFFFFFFFF
nop
nop
nop
nop
nop
nop
iadd32.skipinv.testtanz.chan0 r1, p0, r1, r2
p0 ba #0x00000003
mov.skipinv.end o0, r1
