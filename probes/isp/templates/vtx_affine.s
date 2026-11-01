; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader with an affine map of its clip-space x and y (slot vtxuse):
; as asm/tri/use_vtx.s, then x' = {A} x + {B} y + {C} and y' = {D} x + {E} y + {F}, so that
; the library's triangle lands on any other (isp_words.py affine_params). Temporaries r1-r5;
; the second phase at #17.
        phas #17, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv r1, #{A}
        mov.skipinv r2, #{C}
        fmad.skipinv r4, pa0, r1, r2                    ; A x + C
        mov.skipinv r1, #{D}
        mov.skipinv r2, #{F}
        fmad.skipinv r5, pa0, r1, r2                    ; D x + F
        mov.skipinv r1, #{B}
        fmad.skipinv o0, pa1, r1, r4                    ; x' = B y + A x + C
        mov.skipinv r1, #{E}
        fmad.skipinv o1, pa1, r1, r5                    ; y' = E y + D x + F
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
