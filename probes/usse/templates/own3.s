; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (per-instance stores, phase 11.27): run with --coords (pa0 = (y << 16) | x) and
; --pixels. n = y * 64 + x is the instance number of the 64 x 32 fill. r5 = V1 = 0x5107E000 + n,
; r13 = V2 = 0x5207E000 + n, r40 = this instance's dword of region A (scratch byte offset 0x8000
; + 4 n), r41 = region B (0xA000 + 4 n), r42 = the dword of instance n ^ 1 (the x neighbour) and
; r43 that of n ^ 64 (the y neighbour), r44 n ^ 2, r45 n ^ 128, r46 n ^ 32 and r47 n ^ 1023 (the base's bit 12 is set, so the mask stays below it) (other quads) in region A, r10 = 0xC0DE0001 = the pixel unless a load
; replaces it. SEL (a test of pa0 and a branch over OP and POST) is empty in the all-instance
; probes. Scratch dword d starts as 0xD0000000 | d.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x5CAF0000
mov.skipinv r7, pa0
and r8, r7, #0x3f
shr r9, r7, #16
shl r9, r9, #6
ima32.u r12, r8, #1, r9
mov.skipinv r6, #0x5107E000
ima32.u r5, r12, #1, r6
mov.skipinv r6, #0x5207E000
ima32.u r13, r12, #1, r6
shl r8, r12, #2
mov.skipinv r40, #0x5CAF8000
ima32.u r40, r40, #1, r8
mov.skipinv r41, #0x5CAFA000
ima32.u r41, r41, #1, r8
xor r42, r40, #4
xor r43, r40, #0x100
xor r44, r40, #8
xor r45, r40, #0x200
xor r46, r40, #0x80
xor r47, r40, #0xFFC
mov.skipinv r10, #0xC0DE0001
{OP}
{POST}
{END}
mov.skipinv.end o0, r10
