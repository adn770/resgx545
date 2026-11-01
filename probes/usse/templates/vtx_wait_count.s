; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_wait_count.s -- vtx_wait.s (slot vtxuse) counting its phases: phase 0 adds 1 to scratch
; dword 1 and phase 1 to dword 0, each under lock #0, the first phas waiting {OP}: does phase
; 1 run for a triangle the MTE culls, with and without the vcull wait. The host relocates the
; next phase.
        phas #18, #8, pixel, {OP}
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv r4, #0x5CAF0004
        mov.skipinv r3, #1
        lock #0
        ldad.skipinv r2, [r4,+#0], drc0
        wdf drc0
        iadd32.skipinv.testtaz.chan0 r2, p1, r3, r2
        stad.skipinv [r4,+#0], r2
        idf drc0, bif
        wdf drc0
        release #0
        mov.skipinv.repeat4 o0, pa0
        emitvcbvtx.end.twopart #0, #0
        nop
        ; Phase 1 (instruction 18): count, emit to the MTE and end.
        phas #0, #0, pixel, end, parallel
        mov.skipinv r4, #0x5CAF0000
        mov.skipinv r3, #1
        lock #0
        ldad.skipinv r2, [r4,+#0], drc0
        wdf drc0
        iadd32.skipinv.testtaz.chan0 r2, p1, r3, r2
        stad.skipinv [r4,+#0], r2
        idf drc0, bif
        wdf drc0
        release #0
        emitmtevtx.end.twopart.freep #0, #0, #0
