; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A textured primary with two iterating douti before the fetch (Q093; --tri pixpds, with
; --vtx-coords 4, blk 16 = 4 and vtx_color.s): DOUTI {A}, 0 and DOUTI {A2}, 0 iterate into the
; primary attributes (the vertex colour, source 32, one dword, then a coordinate set), then
; DOUTI {B}, 0 is the fetch's coordinates and a doutt reads the 16x16 RGBA8888 texture at the
; scratch buffer (dword i = 0xD0000000 | i). The shader's U1 is {U}: bit 24 waits for the
; iterations, bit 25 for the fetch.

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word {U}        ; dword 3  = ds1[1]: U1
        .word {A}        ; dword 4  = ds0[2]: first DOUTI word 0
        .word 0          ; dword 5  = ds0[3]: first DOUTI word 1
        .word 0x5CAF0000 ; dword 6  = ds1[2]: T2, the scratch buffer (patched)
        .word 0x00800800 ; dword 7  = ds1[3]: T3
        .word 0x07fe0000 ; dword 8  = ds0[4]: T0, nearest, repeat
        .word 0x0d00f00f ; dword 9  = ds0[5]: T1, RGBA8888, POT, 16x16
        .word {B}        ; dword 10 = ds1[4]: fetch DOUTI word 0
        .word 0          ; dword 11 = ds1[5]: fetch DOUTI word 1
        .word {A2}       ; dword 12 = ds0[6]: second DOUTI word 0
        .word 0          ; dword 13 = ds0[7]: second DOUTI word 1
        .word 0          ; dword 14 = ds1[6]: unused
        .word 0          ; dword 15 = ds1[7]: unused

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        movs douti, ds0[6], ds0[7], ds0[6], ds0[6]
        movs douti, ds1[4], ds1[5], ds1[4], ds1[4]
        movs doutt, ds0[4], ds0[5], ds1[2], ds1[3]
        halt
