; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; An iteration without a fetch for the punch-through probes: doutu with
; U1 0x01000004 (DOUTU1.WAIT_ITER), DOUTI0 0x20000800 (source 1, DOUTI0.LAST_ITER), so pa0
; holds the coordinate set's x (the copy's z with vtx_z.s).

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x01000004 ; dword 3  = ds1[1]: U1, waiting for the iteration
        .word 0x20000800 ; dword 4  = ds0[2]: DOUTI word 0
        .word 0          ; dword 5  = ds0[3]: DOUTI word 1
        .word 0          ; dword 6  = ds1[2]: unused
        .word 0          ; dword 7  = ds1[3]: unused
        .word 0          ; dword 8  = ds0[4]: unused
        .word 0          ; dword 9  = ds0[5]: unused
        .word 0          ; dword 10 = ds1[4]: unused
        .word 0          ; dword 11 = ds1[5]: unused

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        halt
