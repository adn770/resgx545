; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with its depth as a coordinate set (--slot vtxuse=vtx_z.bin,
; --vtx-coords 2): as asm/tri/use_vtx.s, and o4, o5 = the vertex's z and w, so
; the set carries each copy's depth. One instruction more: the second phase at #8.
        phas #8, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa2                     ; o4, o5 = z, w
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
