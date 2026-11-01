; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's primary pixel PDS program for the texture probes (--tri pixpds:12, with
; --vtx-coords 2 and vtx_coords.s): starts the pixel shader with U1 = 0x02000004 (it waits
; for the fetch, DOUTU1.WAIT_FETCH), has the iterator issue DOUTI {A}, 0 and gives the texture
; unit its T words and the texture at the scratch buffer, whose dword i is 0xD0000000 | i:
; each texel names its own address.

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x02000004 ; dword 3  = ds1[1]: U1, waiting for the fetch
        .word {A}        ; dword 4  = ds0[2]: DOUTI word 0
        .word 0          ; dword 5  = ds0[3]: DOUTI word 1
        .word 0x5CAF0000 ; dword 6  = ds1[2]: T2, the scratch buffer (patched)
        .word 0x00800800 ; dword 7  = ds1[3]: T3
        .word 0x07fe0000 ; dword 8  = ds0[4]: T0, nearest, repeat
        .word 0x0d00f00f ; dword 9  = ds0[5]: T1, RGBA8888, POT, 16x16
        .word 0          ; dword 10 = ds1[4]: unused
        .word 0          ; dword 11 = ds1[5]: unused

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        movs doutt, ds0[4], ds0[5], ds1[2], ds1[3]
        halt
