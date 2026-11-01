; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; instruction 2, so only a jump back to 2 ends there (o0 = 0x0C0C0C0C); the program sets p0
; false, runs OP (instruction 5) and falls through to o0 = 0x0B0B0B0B; a jump to instruction
; 10 (5 on from OP) ends with o0 = 0x0D0D0D0D. Nothing depends on the temporaries a task
; starts with.
phas #0, #0, pixel, end, parallel
br #0x00000002
mov.skipinv.end o0, #0x0C0C0C0C
mov.skipinv r33, #1
or.testtaz.chan0 !c0, p0, r33, r33
{OP}
mov.skipinv r21, #0x0B0B0B0B
mov.skipinv.end o0, r21
nop
nop
mov.skipinv.end o0, #0x0D0D0D0D
