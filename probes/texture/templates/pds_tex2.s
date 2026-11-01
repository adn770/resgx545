; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Two fetches in the triangle's primary pixel PDS program (--tri pixpds:16, with
; --vtx-coords 2 and vtx_coords.s), laid out as a two-texture primary:
; DOUTI {A}, 0 and its fetch with T3 = {T}, then DOUTI {B}, 0 and a second fetch with T3
; 0x00800800. Both are 16x16 RGBA8888: the first at
; the scratch buffer (dword i = 0xD0000000 | i), the second 0x4000 bytes on (0xD0001000 | i).
; The shader starts with U1 = 0x02000004, waiting for the fetches.

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x02000004 ; dword 3  = ds1[1]: U1, waiting for the fetches
        .word {A}        ; dword 4  = ds0[2]: first DOUTI word 0
        .word 0          ; dword 5  = ds0[3]: first DOUTI word 1
        .word 0x5CAF0000 ; dword 6  = ds1[2]: first T2, the scratch buffer (patched)
        .word {T}        ; dword 7  = ds1[3]: first T3
        .word 0x07fe0000 ; dword 8  = ds0[4]: first T0, nearest, repeat
        .word 0x0d00f00f ; dword 9  = ds0[5]: first T1, RGBA8888, POT, 16x16
        .word {B}        ; dword 10 = ds1[4]: second DOUTI word 0
        .word 0          ; dword 11 = ds1[5]: second DOUTI word 1
        .word 0x07fe0000 ; dword 12 = ds0[6]: second T0
        .word 0x0d00f00f ; dword 13 = ds0[7]: second T1
        .word 0x5CAF4000 ; dword 14 = ds1[6]: second T2, scratch + 0x4000 (patched)
        .word 0x00800800 ; dword 15 = ds1[7]: second T3

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        movs doutt, ds0[4], ds0[5], ds1[2], ds1[3]
        movs douti, ds1[4], ds1[5], ds1[4], ds1[4]
        movs doutt, ds0[6], ds0[7], ds1[6], ds1[7]
        halt
