; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_douta.s -- a vertex PDS program that passes its inputs on with douta (tri-vtx-douta,
; slot vtxpds, with vtx_dump_sa.s as the vtxuse helper): asm/tri/pds_vtx.s, and before its
; (if0) doutu, per vertex v (ir0):
;   sa[v]     = 0x7E570000 | ir0
;   sa[4 + v] = 0x7E570000 | ir1    (Rogue: the instance ID, 0 here)
;   sa3, sa7  = 0x7E57FFFF          (every vertex writes them)
; so the vertex task's sa0-sa7 say whether douta from a vertex program reaches its task
; PDS runs came before the task started, and what ir1 holds.
;
; Data segment, 12 dwords: the default's 8 (the host patches dwords 0, 1, 2 and 4) and a
; row of constants. Rows interleave the banks by pairs of dwords.
        .word 0          ; dword 0  = ds0[0]: vertex buffer address (patched)
        .word 0          ; dword 1  = ds0[1]: doutd word (patched)
        .word 0          ; dword 2  = ds1[0]: stride (patched)
        .word 0          ; dword 3  = ds1[1]: DOUTU U2 = 0
        .word 0          ; dword 4  = ds0[2]: DOUTU U0 (patched)
        .word 0          ; dword 5  = ds0[3]: DOUTU U1 = 0
        .word 0x7E570000 ; dword 6  = ds1[2]: the marker
        .word 0x00000004 ; dword 7  = ds1[3]: 4, sa4's number
        .word 0x7E57FFFF ; dword 8  = ds0[4]: the constant for sa3 and sa7
        .word 0          ; dword 9  = ds0[5]: unused
        .word 0x00000300 ; dword 10 = ds1[4]: douta control word of sa3 (k << 8)
        .word 0x00000700 ; dword 11 = ds1[5]: douta control word of sa7

        mul ds1[50], ir0.l, ds1[0].l
        movsa doutd, ds0[0], ds0[1], ds1[50], ds1[50]
        or ds0[49], ir0, ds1[2]                 ; 0x7E570000 | ir0
        or ds0[50], ir1, ds1[2]                 ; 0x7E570000 | ir1
        shl ds1[51], ir0, 8                     ; control word of sa[ir0]
        add ds0[53], ir0, ds1[3]
        shl ds1[52], ds0[53], 8                 ; control word of sa[4 + ir0]
        movs douta, ds0[49], ds1[51], ds0[49], ds0[49]
        movs douta, ds0[50], ds1[52], ds0[50], ds0[50]
        movs douta, ds0[4], ds1[4], ds0[4], ds0[4]
        movs douta, ds0[4], ds1[5], ds0[4], ds0[4]
        (if0) movs doutu, ds0[2], ds0[3], ds1[1], ds1[1]
        halt
