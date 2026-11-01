; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_coord4.s with values a half float does not hold: o4 = the vertex's clip-space x, o5 = 0.1,
; o6 = 1/3, o7 = 0.7 (slot vtxuse, --vtx-coords 4), for the coordfmt probes. The second phase
; at #11.
        phas #11, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv o4, pa0                             ; o4 = x
        mov.skipinv o5, #0x3DCCCCCD                     ; 0.1
        mov.skipinv o6, #0x3EAAAAAB                     ; 1/3
        mov.skipinv o7, #0x3F333333                     ; 0.7
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
