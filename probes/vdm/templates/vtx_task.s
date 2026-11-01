; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_task.s -- a vertex shader (slot vtxuse) that records how the vertices fall into tasks
; (VDM_TASK0 bits 31:28): vtx_dump.s for the 126 vertices of 42 copies
; (vertices = 126). Every vertex's x is distinct, and the slot ((x >> 10) ^ (y >> 20)) & 0xfff
; is too, for these vertices. Every valid instance stores to its slot's 16 bytes (scratch
; byte 16 x slot):
;   dword 0     its x
;   dwords 1-3  i4, i8, i12: i0 (x) of the instances one, two and three places on in its
;               quad, or the sentinel 0x3F800000 where no valid instance is
; Quads never span tasks, so a task boundary shows as a quad short of vertices.
; As use_vtx.s the first instruction is the phas whose next phase the host relocates.
; Temporaries r0-r8: run with --temps 16.
        ; Phase 0: wait for the attribute DMA, as use_vtx.s.
        phas #27, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov i0, #0x3F800000
        mov.skipinv i0, pa0
        mov.skipinv r4, i4
        mov.skipinv r5, i8
        mov.skipinv r6, i12
        ; r1 = the slot's register offset, (16 << 16) | slot
        shr.skipinv r1, pa0, #10
        shr.skipinv r2, pa1, #20
        xor.skipinv r1, r1, r2
        and.skipinv r1, r1, #0x0FFF
        or.skipinv r1, r1, #0x00100000
        mov.skipinv r8, #0x5CAF0000
        stad.skipinv [r8,+r1], pa0                      ; dword 0: x
        mov.skipinv r8, #0x5CAF0004
        stad.skipinv [r8,+r1], r4                       ; dword 1: one instance on
        mov.skipinv r8, #0x5CAF0008
        stad.skipinv [r8,+r1], r5                       ; dword 2: two on
        mov.skipinv r8, #0x5CAF000C
        stad.skipinv [r8,+r1], r6                       ; dword 3: three on
        idf drc0, bif
        wdf drc0
        emitvcbvtx.end.twopart #0, #0
        ; Phase 1: emit the vertex to the MTE and end.
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
