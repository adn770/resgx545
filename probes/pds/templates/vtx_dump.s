; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_dump.s -- the vertex shader of the vertex PDS probes (tri-vtx.toml: sgxfive-test probe
; --tri vtxpds:8 --slot vtxuse=vtx_dump.bin): use_vtx.s, with each valid instance storing
; what it got to a slot of 16 dwords picked by its vertex, so that no two vertices share one
; (no atomics). The vertices are the default triangle's, x = -0.75, 0.75, -0.375 for vertex
; 0, 1, 2 (0xBF400000, 0x3F400000, 0xBEC00000): slot (x >> 30 & 2) | (x >> 23 & 1) is 2, 0,
; 3, and slot 1 is the sentinel's (1.0), which no vertex has. Slot s is at scratch byte 64 s:
;   dword 0      0x7E570000 | s
;   dwords 1-4   pa0-pa3, the vertex the PDS DMAed (x, y, z, w)
;   dwords 5-7   i4, i8, i12: i0 of the instance one, two and three places on in the
;                instance put its x and every instance first the sentinel 0x3F800000
; So the slots written say which vertices ran, and dwords 5-7 which ran in the same task
; and in what order: the instances of one task see each other's x, a lone vertex the
; sentinel (or, if mov without .skipinv does not reach invalid instances, a stale value).
;
; As use_vtx.s the first instruction is the phas whose next phase (counted from the
; program's start) the host relocates. Temporaries r0-r8: run with --temps 16.
        ; Phase 0: wait for the attribute DMA, as use_vtx.s.
        phas #37, #0, pixel, vcull, parallel
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        ; i0 = the sentinel 1.0 in every instance, then x in the valid ones: i4, i8, i12
        ; read i0 of the instances one, two and three places on in the quad.
        mov i0, #0x3F800000
        mov.skipinv i0, pa0
        mov.skipinv r4, i4
        mov.skipinv r5, i8
        mov.skipinv r6, i12
        ; The slot: bit 31 and bit 23 of x, (x >> 30 & 2) | (x >> 23 & 1); r1 = 64 bytes x slot
        ; as a register offset (high half 64, low half the slot), r3 the slot's marker.
        shr.skipinv r1, pa0, #30
        and.skipinv r1, r1, #2
        shr.skipinv r2, pa0, #23
        and.skipinv r2, r2, #1
        or.skipinv r1, r1, r2
        or.skipinv r3, r1, #0x7E570000
        or.skipinv r1, r1, #0x00400000
        mov.skipinv r8, #0x5CAF0000
        stad.skipinv [r8,+r1], r3                       ; dword 0: marker
        mov.skipinv r8, #0x5CAF0004
        stad.skipinv [r8,+r1], pa0                      ; dword 1: x
        mov.skipinv r8, #0x5CAF0008
        stad.skipinv [r8,+r1], pa1                      ; dword 2: y
        mov.skipinv r8, #0x5CAF000C
        stad.skipinv [r8,+r1], pa2                      ; dword 3: z
        mov.skipinv r8, #0x5CAF0010
        stad.skipinv [r8,+r1], pa3                      ; dword 4: w
        mov.skipinv r8, #0x5CAF0014
        stad.skipinv [r8,+r1], r4                       ; dword 5: i0 one instance on
        mov.skipinv r8, #0x5CAF0018
        stad.skipinv [r8,+r1], r5                       ; dword 6: i0 two on
        mov.skipinv r8, #0x5CAF001C
        stad.skipinv [r8,+r1], r6                       ; dword 7: i0 three on
        idf drc0, bif
        wdf drc0
        emitvcbvtx.end.twopart #0, #0
        ; Phase 1: emit the vertex to the MTE and end.
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
