; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with 9 coordinate output dwords (slot vtxuse, --vtx-coords 9):
; o4, o5 = the vertex's clip-space x and y, o6 on constants 0x3F400000, 0x3F600000, 0x3F800000, 0x3F900000, 0x3FA00000, 0x3FB00000, 0x3FC00000. The second phase at #15. Written by gen/gen_templates.py in the form of
; probes/ta/templates/vtx_coord4.s.
        phas #15, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv o6, #0x3F400000
        mov.skipinv o7, #0x3F600000
        mov.skipinv o8, #0x3F800000
        mov.skipinv o9, #0x3F900000
        mov.skipinv o10, #0x3FA00000
        mov.skipinv o11, #0x3FB00000
        mov.skipinv o12, #0x3FC00000
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
