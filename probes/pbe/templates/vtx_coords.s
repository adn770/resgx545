; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with a texture coordinate set (--slot vtxuse=vtx_coords.bin,
; --vtx-coords 2): as asm/tri/use_vtx.s, and o4, o5 = the vertex's clip-space x and y, so
; the set varies across the triangle. One instruction more: the second phase at #8.
        phas #8, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
