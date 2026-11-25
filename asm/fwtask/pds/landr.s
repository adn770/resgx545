; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; landr.s -- which of two words known unmapped in sa0 and sa1 land's stop faults at (round 46, N3k
; §3.2, the user's decision A (a)).
;
; landq.s with dword 8 (ds0[4], the word to attribute 0) 0x005d2000 -> 0x04400000 and nothing
; else: 3 data rows, as PDS #14 has (control word 0x01800100, #14's own), no tim, so the EDM tick
; keeps running. Row r holds ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md, the
; data segment): the third row is ds0[4] = L4 0x04400000, ds0[5] = M1 0x005d1000 (mark.s's
; attribute-1 marker), ds1[4] = the douta control of attribute 0, ds1[5] = that of attribute 1.
; Both name pages the BIF faulted at before (L4's page in LV, E1183; M1's in V, LM and Q, E1185,
; E1198, E1233), below 0x10000000, where no REV1 heap lies (doc/specs/boot_sequence.md section
; 4); L4's page 0x4400 above M1's 0x5d1. Every landq dword and instruction keeps its value and
; operands. The kernel fills U0 only, as for land and landq (dwords 4 and 5 are Ma and Mb:
; SGX_OWN_PDS_LANDR_FILLV 0).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0x1800    ; dword 3 = ds1[1]: douta control, attribute 24
        .word 0x5a5a3a18 ; dword 4 = ds0[2]: Ma
        .word 0x5a5a3a1a ; dword 5 = ds0[3]: Mb
        .word 0x1a00    ; dword 6 = ds1[2]: douta control, attribute 26
        .word 0         ; dword 7 = ds1[3]: unused (crumb3's T3)
        .word 0x04400000 ; dword 8 = ds0[4]: L4, the word to attribute 0
        .word 0x005d1000 ; dword 9 = ds0[5]: M1, the word to attribute 1
        .word 0         ; dword 10 = ds1[4]: douta control, attribute 0
        .word 0x100     ; dword 11 = ds1[5]: douta control, attribute 1

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; Ma to attribute 24
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; Mb to attribute 26
        movs douta, ds0[4], ds1[4], ds0[4], ds0[4]      ; L4 to attribute 0
        movs douta, ds0[5], ds1[5], ds0[5], ds0[5]      ; M1 to attribute 1
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
