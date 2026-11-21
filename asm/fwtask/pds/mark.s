; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; mark.s -- where sa13 comes from under sideband bit 10 (round 42, N3g row M, the user's decision
; B (a)).
;
; crumb3.s (3 data rows, as PDS #14 has, so the kernel's control word is (3 << 23) | 0x100 =
; 0x01800100, #14's own) with its unused third row holding two markers and their douta controls,
; and two douta more. Row r holds ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md,
; the data segment): the third row is ds0[4] = M13, ds0[5] = M1, ds1[4] = the douta control of
; attribute 13, ds1[5] = that of attribute 1 (douta control bits 19:8 name the attribute,
; pds_isa.md section 3). Every crumb3 dword and instruction keeps its value and operands; the two
; marker douta follow crumb3's two douta, before T2. The markers name pages below 0x10000000,
; where no REV1 heap lies (doc/specs/boot_sequence.md section 4), 0x5d for "ours", page 0x5d3 for
; attribute 13 and 0x5d1 for attribute 1; no kept page of rounds 40-41 holds either (N3g §0.1).
; The kernel fills U0, V0 and V2 as for crumb3 (SGX_OWN_PDS_MARK_FILLV 1).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0; T1's value
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2; T2's value
        .word 0x005a3305 ; dword 7 = ds1[3]: T3's value
        .word 0x005d3000 ; dword 8 = ds0[4]: M13, the marker to attribute 13
        .word 0x005d1000 ; dword 9 = ds0[5]: M1, the marker to attribute 1
        .word 0xd00     ; dword 10 = ds1[4]: douta control, attribute 13
        .word 0x100     ; dword 11 = ds1[5]: douta control, attribute 1

        movs tim, ds1[1], ds1[1], ds1[1], ds1[1]        ; T1: tim <- 0x000
        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs douta, ds0[4], ds1[4], ds0[4], ds0[4]      ; M13 to attribute 13
        movs douta, ds0[5], ds1[5], ds0[5], ds0[5]      ; M1 to attribute 1
        movs tim, ds1[2], ds1[2], ds1[2], ds1[2]        ; T2: tim <- 0x200
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        movs tim, ds1[3], ds1[3], ds1[3], ds1[3]        ; T3: tim <- 0x005a3305
        halt
