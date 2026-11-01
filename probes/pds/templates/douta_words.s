; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Program template of the douta probes: sixteen douta (ds[2..17]), each with its value V0-V15
; and its control word C0-C15 given by the case's inputs. Word k of the program writes its value
; to the secondary attribute named by bits 19-8 of its control word, so a case chooses which
; attributes get a value (a word that should not write one repeats another word's value and
; attribute: the last write to an attribute wins), then starts the USE task with the U0 and U1
; the host patches into data dwords 0 and 1 (sgxfive-test probe --pds 36 --use sa_dump.bin, or
; --tri pixpds:36). The values sit in the ds0 half of rows 1-8 and the control words in the ds1
; half, since one movs reads at most one pair from each bank. sa_dump.s, the USE task, stores
; sa0-sa15 to scratch dwords 0-15.
        .word 0, 0, 0, 0                  ; row 0: U0, U1 (host), 0 (doutu's third word), unused
        .word {V0}, {V1}, {C0}, {C1}      ; row 1: values 0,1, controls
        .word {V2}, {V3}, {C2}, {C3}      ; row 2: values 2,3, controls
        .word {V4}, {V5}, {C4}, {C5}      ; row 3: values 4,5, controls
        .word {V6}, {V7}, {C6}, {C7}      ; row 4: values 6,7, controls
        .word {V8}, {V9}, {C8}, {C9}      ; row 5: values 8,9, controls
        .word {V10}, {V11}, {C10}, {C11}  ; row 6: values 10,11, controls
        .word {V12}, {V13}, {C12}, {C13}  ; row 7: values 12,13, controls
        .word {V14}, {V15}, {C14}, {C15}  ; row 8: values 14,15, controls

        movs douta, ds0[2], ds1[2], ds0[2], ds0[2]
        movs douta, ds0[3], ds1[3], ds0[3], ds0[3]
        movs douta, ds0[4], ds1[4], ds0[4], ds0[4]
        movs douta, ds0[5], ds1[5], ds0[5], ds0[5]
        movs douta, ds0[6], ds1[6], ds0[6], ds0[6]
        movs douta, ds0[7], ds1[7], ds0[7], ds0[7]
        movs douta, ds0[8], ds1[8], ds0[8], ds0[8]
        movs douta, ds0[9], ds1[9], ds0[9], ds0[9]
        movs douta, ds0[10], ds1[10], ds0[10], ds0[10]
        movs douta, ds0[11], ds1[11], ds0[11], ds0[11]
        movs douta, ds0[12], ds1[12], ds0[12], ds0[12]
        movs douta, ds0[13], ds1[13], ds0[13], ds0[13]
        movs douta, ds0[14], ds1[14], ds0[14], ds0[14]
        movs douta, ds0[15], ds1[15], ds0[15], ds0[15]
        movs douta, ds0[16], ds1[16], ds0[16], ds0[16]
        movs douta, ds0[17], ds1[17], ds0[17], ds0[17]
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        halt
