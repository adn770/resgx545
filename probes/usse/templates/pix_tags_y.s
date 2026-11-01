; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A one-phase pixel shader for the output-room probes (slot pixel): o0 to o7 each hold the
; pixel's own y (primary attribute 1, a float whose low 16 bits are clear) with the
; register's number plus one in the low bits, so a pixel's value names the register that
; reached it and the position it was written from.
        phas #0, #0, pixel, end, parallel
        or.skipinv o0, pa1, #1
        or.skipinv o1, pa1, #2
        or.skipinv o2, pa1, #3
        or.skipinv o3, pa1, #4
        or.skipinv o4, pa1, #5
        or.skipinv o5, pa1, #6
        or.skipinv o6, pa1, #7
        or.skipinv.end o7, pa1, #8
