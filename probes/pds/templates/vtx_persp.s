; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader for the perspective probes (slot vtxuse, --vtx-coords 2): w =
; x + 2 from the vertex's own x (1.25, 2.75, 1.625 at the three vertices) and x, y, z
; multiplied by it, so the triangle covers the same pixels as with w 1; o4, o5 = the vertex's
; x and y before the multiply. An affine iteration of o4 then gives each pixel its own x, a
; perspective-correct one (sum l_i x_i / w_i) / (sum l_i / w_i). Temporaries r1-r3.
        phas #16, #0, pixel, vcull, parallel           ; the second phase at instruction 16
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv r1, #0x3F800000                     ; 1
        mov.skipinv r2, #0x40000000                     ; 2
        fmad.skipinv r1, pa0, r1, r2                    ; w = x + 2
        mov.skipinv r3, #0x00000000
        fmad.skipinv o0, pa0, r1, r3                    ; x * w
        fmad.skipinv o1, pa1, r1, r3                    ; y * w
        fmad.skipinv o2, pa2, r1, r3                    ; z * w
        mov.skipinv o3, r1                              ; w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
