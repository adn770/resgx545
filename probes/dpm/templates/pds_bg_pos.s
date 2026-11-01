; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The background object's primary pixel PDS program of the partial-reload script (Q038;
; probe --tri bgpds:12): pds_iter_nofetch.s with DOUTI0 0x20400000 (source 0, two components,
; the completion bit: the pixel's x + 0.5 and y + 0.5 in pa0 and pa1) and U1 0x01000004 (bit 24
; waits for the iteration); data dwords 0 and 1 are the background shader's U0 and U1, patched.

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x01000004 ; dword 3  = ds1[1]: U1
        .word 0x20400000 ; dword 4  = ds0[2]: DOUTI word 0
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
