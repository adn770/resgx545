; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with its clip-space depth set from its x (slot vtxuse,
; --vtx-coords 2): as asm/tri/use_vtx.s, o4, o5 = clip x and y, and z = {A} x + {B}, so a
; flat or sloped depth reaches past the clip volume. Temporaries r1-r2; the second phase at
; #11.
        phas #11, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv.repeat2 o4, pa0                     ; o4, o5 = x, y
        mov.skipinv r1, #{A}
        mov.skipinv r2, #{B}
        fmad.skipinv o2, pa0, r1, r2                    ; z = A x + B
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
