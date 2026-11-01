; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_dump_sa.s -- vtx_dump.s with sa0-sa7 too (dwords 8-15 of the slot): what a vertex PDS
; program's douta wrote into the vertex task's secondary attributes, if anything
; (tri-vtx-douta). Everything else as vtx_dump.s, whose comment has the slot layout.
; Temporaries r0-r8: run with --temps 16.
        ; Phase 0: wait for the attribute DMA, as use_vtx.s.
        phas #53, #0, pixel, vcull, parallel
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
        mov.skipinv r8, #0x5CAF0020
        stad.skipinv [r8,+r1], sa0                      ; dword 8: sa0
        mov.skipinv r8, #0x5CAF0024
        stad.skipinv [r8,+r1], sa1                      ; dword 9: sa1
        mov.skipinv r8, #0x5CAF0028
        stad.skipinv [r8,+r1], sa2                      ; dword 10: sa2
        mov.skipinv r8, #0x5CAF002C
        stad.skipinv [r8,+r1], sa3                      ; dword 11: sa3
        mov.skipinv r8, #0x5CAF0030
        stad.skipinv [r8,+r1], sa4                      ; dword 12: sa4
        mov.skipinv r8, #0x5CAF0034
        stad.skipinv [r8,+r1], sa5                      ; dword 13: sa5
        mov.skipinv r8, #0x5CAF0038
        stad.skipinv [r8,+r1], sa6                      ; dword 14: sa6
        mov.skipinv r8, #0x5CAF003C
        stad.skipinv [r8,+r1], sa7                      ; dword 15: sa7
        idf drc0, bif
        wdf drc0
        emitvcbvtx.end.twopart #0, #0
        ; Phase 1: emit the vertex to the MTE and end.
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
