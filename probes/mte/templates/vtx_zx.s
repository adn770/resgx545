; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with a coordinate set and a sloped depth (--slot
; vtxuse=vtx_zx.bin, --vtx-coords 2): as asm/tri/use_vtx.s, o4, o5 = clip x and y, and
; z = clip x (o2 overwritten), so the depth slopes across the triangle. Two instructions
; more: the second phase at #9.
        phas #9, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv o2, pa0                             ; z = x
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
