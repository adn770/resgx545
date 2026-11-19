; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; crumb3.s -- crumb.s with a third data row (round 38, N3c row R4, the firmware's #14 mirror).
;
; crumb.s's 8 data dwords plus four zero dwords: 3 data rows, as PDS #14 has (E146; the
; firmware's control word for it is PDS_CTL #14 with addend 0x100, doc/specs/fw_format.md
; section 4), so the kernel's control word for this image is (3 << 23) | 0x100 = 0x01800100.
; Row r holds ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md, the data segment):
; the third row is ds0[4], ds0[5], ds1[4], ds1[5], which no instruction names, and every operand
; of crumb.s keeps its dword. The 7 instructions are crumb.s's: T1 = 0x000, the two douta,
; T2 = 0x200, the doutu, T3 = 0x005a3305, halt.

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0; T1's value
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2; T2's value
        .word 0x005a3305 ; dword 7 = ds1[3]: T3's value
        .word 0         ; dword 8 = ds0[4]: the third row, unused
        .word 0         ; dword 9 = ds0[5]
        .word 0         ; dword 10 = ds1[4]
        .word 0         ; dword 11 = ds1[5]

        movs tim, ds1[1], ds1[1], ds1[1], ds1[1]        ; T1: tim <- 0x000
        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs tim, ds1[2], ds1[2], ds1[2], ds1[2]        ; T2: tim <- 0x200
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        movs tim, ds1[3], ds1[3], ds1[3], ds1[3]        ; T3: tim <- 0x005a3305
        halt
