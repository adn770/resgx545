; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with two coordinate sets of two components (slot vtxuse,
; --vtx-coords 4, COORDSIZE 0x12): as asm/tri/use_vtx.s, and o4, o5 = clip x and y, o6, o7 =
; x and y again. Two instructions more: the second phase at #9.
        phas #9, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv.repeat2 o6, pa0                     ; o6, o7 = x, y
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
