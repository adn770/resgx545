; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; landp.s -- whether 0x005d2000 is mapped where land's stop reads it (round 46, N3k §3.2, the
; user's decision A (a)).
;
; landv.s with dword 9 (ds0[5]) Mb -> Q0 0x005d2000 and dword 10 (ds1[4]) 0x1a00 -> 0x100 (the
; douta control of attribute 1 for attribute 26's) and nothing else: 3 data rows, as PDS #14 has
; (control word 0x01800100, #14's own), no tim, so the EDM tick keeps running. Row r holds
; ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md, the data segment). The kernel's
; V0 and V2 to attributes 0 and 2 (its fills at dwords 4 and 5, as in landv: V0 is a page of the
; kernel data heap, LV, V and LM ran with it in sa0), Ma to attribute 24, then Q0 to attribute 1
; from the third row; landv's doutu and halt. Every other landv dword and instruction keeps its
; value and operands. The kernel fills U0, V0 and V2 (SGX_OWN_PDS_LANDP_FILLV 1).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2
        .word 0x1800    ; dword 7 = ds1[3]: douta control, attribute 24
        .word 0x5a5a3a18 ; dword 8 = ds0[4]: Ma
        .word 0x005d2000 ; dword 9 = ds0[5]: Q0, the word to attribute 1
        .word 0x100     ; dword 10 = ds1[4]: douta control, attribute 1
        .word 0         ; dword 11 = ds1[5]: unused

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs douta, ds0[4], ds1[3], ds0[4], ds0[4]      ; Ma to attribute 24
        movs douta, ds0[5], ds1[4], ds0[5], ds0[5]      ; Q0 to attribute 1
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
