; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A one-phase pixel shader for the output-room probes (slot pixel): o0 to o7 each hold the
; pixel's own x (primary attribute 0, a float whose low 16 bits are clear) with the
; register's number plus one in the low bits, so a pixel's value names the register that
; reached it and the position it was written from.
        phas #0, #0, pixel, end, parallel
        or.skipinv o0, pa0, #1
        or.skipinv o1, pa0, #2
        or.skipinv o2, pa0, #3
        or.skipinv o3, pa0, #4
        or.skipinv o4, pa0, #5
        or.skipinv o5, pa0, #6
        or.skipinv o6, pa0, #7
        or.skipinv.end o7, pa0, #8
