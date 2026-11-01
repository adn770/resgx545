; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with a vertex colour in o4-o7 as vtx_color.s, and after it a
; two-dword coordinate set in o8, o9 = the vertex's clip-space x and y (--vtx-coords 6: a set
; of four, then a set of two). The second phase at #11.
        phas #11, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv o6, #0x3E800000                     ; 0.25
        mov.skipinv o7, #0x3F800000                     ; 1.0
        mov.skipinv.repeat2 o8, pa0                     ; o8, o9 = x, y
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
