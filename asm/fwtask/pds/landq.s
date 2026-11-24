; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; landq.s -- which of two unmapped words in sa0 and sa1 land's stop faults at (round 45, N3j
; §9.0 and §9.5, the user's decision E (c)).
;
; land.s (3 data rows, as PDS #14 has, so the kernel's control word is (3 << 23) | 0x100 =
; 0x01800100, #14's own; no tim, so the EDM tick keeps running) with its unused third row holding
; two words and their douta controls, and two douta more after land's two. Row r holds ds0[2r],
; ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md, the data segment): the third row is
; ds0[4] = Q0 0x005d2000, ds0[5] = M1 0x005d1000 (mark.s's attribute-1 marker), ds1[4] = the douta
; control of attribute 0, ds1[5] = that of attribute 1 (douta control bits 19:8 name the
; attribute, pds_isa.md section 3). Both name pages below 0x10000000, where no REV1 heap lies
; (doc/specs/boot_sequence.md section 4), Q0's page 0x5d2 above M1's 0x5d1. Every land dword and
; instruction keeps its value and operands; the two douta follow land's two, before the doutu.
; The kernel fills U0 only, as for land (dwords 4 and 5 are Ma and Mb: SGX_OWN_PDS_LANDQ_FILLV 0).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0x1800    ; dword 3 = ds1[1]: douta control, attribute 24
        .word 0x5a5a3a18 ; dword 4 = ds0[2]: Ma
        .word 0x5a5a3a1a ; dword 5 = ds0[3]: Mb
        .word 0x1a00    ; dword 6 = ds1[2]: douta control, attribute 26
        .word 0         ; dword 7 = ds1[3]: unused (crumb3's T3)
        .word 0x005d2000 ; dword 8 = ds0[4]: Q0, the word to attribute 0
        .word 0x005d1000 ; dword 9 = ds0[5]: M1, the word to attribute 1
        .word 0         ; dword 10 = ds1[4]: douta control, attribute 0
        .word 0x100     ; dword 11 = ds1[5]: douta control, attribute 1

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; Ma to attribute 24
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; Mb to attribute 26
        movs douta, ds0[4], ds1[4], ds0[4], ds0[4]      ; Q0 to attribute 0
        movs douta, ds0[5], ds1[5], ds0[5], ds0[5]      ; M1 to attribute 1
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
