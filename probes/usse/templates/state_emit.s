; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; state_emit.s -- use_mtest18.s (slot state) with its emits' part flag the case: {OP} on
; emitvcbst and {M} on emitmtest ("" as drawn, or ".twopart", bit 42 as the vertex emits'
        phas #0, #0, pixel, end, parallel               ; a single phase
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat16 o0, pa0                    ; words 0-15
        mov.skipinv.repeat2 o16, pa16                   ; words 16-17
        emitvcbst{OP} #0, #0
        wop #0
        emitmtest.end{M}.freep #0, #0, #0
