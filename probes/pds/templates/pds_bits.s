; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; PDS encoding-bit probe template (pds_bits.py; sgxfive-test probe --pds 36 --use sa_dump.bin):
; pds_dump.s with two more slots. Inputs A-H in ds0[2]-ds0[9] and I-P in ds1[2]-ds1[9] are
; copied to the temporaries ds0[48]-ds0[55] and ds1[48]-ds1[55]; OP works there; the sixteen
; go to sa0-sa15 with douta; POST runs after those writes (a port write under test lands last)
; and END ends the program (halt, or the halt under test). sa_dump.s stores sa0-sa15 to scratch
; dwords 0-15.
        .word 0, 0, 0, 0                        ; row 0: U0, U1, U2 (sgxfive-test), unused
        .word {A}, {B}, {I}, {J}                ; rows 1-4: the inputs
        .word {C}, {D}, {K}, {L}
        .word {E}, {F}, {M}, {N}
        .word {G}, {H}, {O}, {P}
        .word 0x800, 0x900, 0x000, 0x100        ; rows 5-8: ds0[10+k] attribute 8+k,
        .word 0xA00, 0xB00, 0x200, 0x300        ; ds1[10+k] attribute k
        .word 0xC00, 0xD00, 0x400, 0x500
        .word 0xE00, 0xF00, 0x600, 0x700

        mov32 ds0[48], ds0[2]
        mov32 ds1[48], ds1[2]
        mov32 ds0[49], ds0[3]
        mov32 ds1[49], ds1[3]
        mov32 ds0[50], ds0[4]
        mov32 ds1[50], ds1[4]
        mov32 ds0[51], ds0[5]
        mov32 ds1[51], ds1[5]
        mov32 ds0[52], ds0[6]
        mov32 ds1[52], ds1[6]
        mov32 ds0[53], ds0[7]
        mov32 ds1[53], ds1[7]
        mov32 ds0[54], ds0[8]
        mov32 ds1[54], ds1[8]
        mov32 ds0[55], ds0[9]
        mov32 ds1[55], ds1[9]

        {OP}

        movs douta, ds0[48], ds1[10], ds0[48], ds0[48]
        movs douta, ds0[49], ds1[11], ds0[49], ds0[49]
        movs douta, ds0[50], ds1[12], ds0[50], ds0[50]
        movs douta, ds0[51], ds1[13], ds0[51], ds0[51]
        movs douta, ds0[52], ds1[14], ds0[52], ds0[52]
        movs douta, ds0[53], ds1[15], ds0[53], ds0[53]
        movs douta, ds0[54], ds1[16], ds0[54], ds0[54]
        movs douta, ds0[55], ds1[17], ds0[55], ds0[55]
        movs douta, ds1[48], ds0[10], ds1[48], ds1[48]
        movs douta, ds1[49], ds0[11], ds1[49], ds1[49]
        movs douta, ds1[50], ds0[12], ds1[50], ds1[50]
        movs douta, ds1[51], ds0[13], ds1[51], ds1[51]
        movs douta, ds1[52], ds0[14], ds1[52], ds1[52]
        movs douta, ds1[53], ds0[15], ds1[53], ds1[53]
        movs douta, ds1[54], ds0[16], ds1[54], ds1[54]
        movs douta, ds1[55], ds0[17], ds1[55], ds1[55]
        {POST}
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        {END}
