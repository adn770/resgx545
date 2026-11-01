; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader (asm/tri/use_vtx.s) with six instructions OP after the position
; is loaded and before the emits, for fdpc's clip-plane result: OP is always six instructions
; (padded with nops), so the second phase stays at #13.
        phas #13, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
{OP}
        mov.skipinv.repeat4 o0, pa0
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
