; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with two coordinate outputs (slot vtxuse, --vtx-coords 2) holding the
; case's A and B as floats in o4 and o5: which of them a point reads as its size (Q117). The second
; phase at #8.
        phas #8, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv o4, #{A}                            ; o4 = A
        mov.skipinv o5, #{B}                            ; o5 = B
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
