; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Primary pixel program that shows one condition per pixel (probe --tri, slot pixpds, with
; pix_pa0.s and vtx_coords.s): it starts the shader with U1 = {U} (the iteration wait), then
; issues one iteration with DOUTI0 bit 29 (the last). By default the word is {A} (a source
; of the coordinate set); OP may replace it, under the condition the case tests, by {C} (source
; 0, the pixel's x + 0.5). So each pixel's pa0 tells whether the condition held in the program
; that served it. {M} is a mask OP may test against (ds1[2]); ds1[3] is 0.
        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word {U}        ; dword 3  = ds1[1]: U1
        .word {A}        ; dword 4  = ds0[2]: DOUTI word 0, the default
        .word 0          ; dword 5  = ds0[3]: DOUTI word 1
        .word {M}        ; dword 6  = ds1[2]: the mask
        .word 0          ; dword 7  = ds1[3]: 0
        .word {C}        ; dword 8  = ds0[4]: DOUTI word 0 where the condition holds
        .word 0          ; dword 9  = ds0[5]: 0
        .word 0          ; dword 10 = ds1[4]: 0
        .word 0          ; dword 11 = ds1[5]: 0

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        mov32 ds0[48], ds0[2]
        mov32 ds0[49], ds0[3]
        {OP}
        movs douti, ds0[48], ds0[49], ds0[48], ds0[48]
        halt
