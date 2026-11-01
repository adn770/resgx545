; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_wait.s -- use_vtx.s (slot vtxuse) with its first phas's wait and mode the case ({OP}:
; "vcull, parallel" as drawn, "none, parallel", "vcull, perinstance", ...): does the MTE emit
; need the vcull wait. The host relocates the next phase.

        ; Phase 0: wait for the attribute DMA, copy the position, emit to the VCB.
        phas #7, #0, pixel, {OP}
        nop.nosched
        ; A load that never runs (p0 is false: 0 & 0 is zero) followed by a wait on the
        ; data fence: the task does not read pa0-pa3 before the PDS DMA has landed.
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        emitvcbvtx.end.twopart #0, #0
        ; Phase 1 (instruction 7): emit the vertex to the MTE and end.
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
