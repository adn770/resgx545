; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; emitpds probe, the PDS program (phase 11.24, sgxfive-test probe --pds 8 --use emit_*.s --low
; 0x10000): the fill's PDS secondary, which an emitpds of the fill's shader names again. Every
; run stores {SRC} to scratch dword 0 (the scratch is mapped at 0x10000: a store of one dword
; completes, E144) and starts the secondary task as the fill's own program
; does (pds_dump.s). The first run, the fill's, leaves its ir0 there; a run the emit starts
; leaves the s2 the emit passed, if s2 becomes ir0 (E146, [infer]).
        .word 0, 0, 0, 0                        ; row 0: U0, U1, U2 (sgxfive-test), unused
        .word {A}, 0, 0, 0                      ; row 1: a constant
        mov32 ds1[48], {SRC}
        store 0x00010000, ds1[48]
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        halt
