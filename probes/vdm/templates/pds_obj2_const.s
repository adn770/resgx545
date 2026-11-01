; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The second object's primary pixel PDS program of the state2-consts probes (Q047;
; obj2 pixpds, 8 data dwords): a douta writes the constant 0xFF00FF00 to the secondary attribute
; named by its control word (bits 19-8: sa0 at 0), then the pixel task starts with the
; U0 and U1 the host patches into data dwords 0 and 1. The task's sa_pixel.s shader writes sa0 as the
; colour, so the object's colour is the constant its state block's program loads.
        .word 0, 0, 0, 0                  ; row 0: U0, U1 (host), 0 (doutu's third word), unused
        .word 0xFF00FF00, 0, 0, 0                ; row 1: the value (green), the control word (sa0)

        movs douta, ds0[2], ds1[2], ds0[2], ds0[2]
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        halt
