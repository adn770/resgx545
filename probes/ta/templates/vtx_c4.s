; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with 4 coordinate output dwords (slot vtxuse, --vtx-coords 4):
; o4, o5 = the vertex's clip-space x and y, o6 on constants 0x3F400000, 0x3F600000. The second phase at #10. Written by gen/gen_templates.py in the form of
; probes/ta/templates/vtx_coord4.s.
        phas #10, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv o6, #0x3F400000
        mov.skipinv o7, #0x3F600000
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
