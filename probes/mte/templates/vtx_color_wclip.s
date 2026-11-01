; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_color.s on a clipped triangle: w = -2 x + 1 from the vertex's own x (vtx_wclip.s with
; A = -2, B = 1), so the second vertex has w -0.5 and the MTE clips the triangle at w = 0;
; o4, o5 = the vertex's x and y, o6 = 0.25, o7 = 1.0, the vertex colour
; (slot vtxuse, --vtx-coords 4). Temporaries r1-r2. The second phase at #13.
        phas #13, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv r1, #0xC0000000                     ; -2.0
        mov.skipinv r2, #0x3F800000                     ; 1.0
        fmad.skipinv o3, pa0, r1, r2                    ; w = -2 x + 1
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv o6, #0x3E800000                     ; 0.25
        mov.skipinv o7, #0x3F800000                     ; 1.0
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
