; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with one coordinate output (slot vtxuse, --vtx-coords 1) holding 16 * C + 20
; (C the vertex's clip x or y, pa0 or pa1): a size that differs per vertex, if a point reads its own vertex's
; row (Q117). Temporaries r1-r3. The second phase at #11.
        phas #11, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv r1, #0x41800000                     ; 16
        mov.skipinv r2, #0x41A00000                     ; 20
        fmad.skipinv r3, {C}, r1, r2                    ; 16 * C + 20
        mov.skipinv o4, r3                              ; o4 = the size
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
