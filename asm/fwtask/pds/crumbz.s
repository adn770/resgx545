; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; crumbz.s -- crumb3.s without its two douta (round 45, N3j §9.0, the user's decision E (c)).
;
; crumb3's 12 data dwords word for word (3 data rows, as PDS #14 has, so the kernel's control
; word is (3 << 23) | 0x100 = 0x01800100, #14's own) and the kernel fills U0, V0 and V2 as for
; crumb3 (SGX_OWN_PDS_CRUMBZ_FILLV 1), so the data rows on the page are crumb3's; nothing reads
; V0 and V2 here. The program is crumb3's without the douta of V0 to attribute 0 and V2 to
; attribute 2: T1, T2, the doutu, T3 and halt, every operand unchanged (ds1[1] and ds1[2] stay
; T1's and T2's values). It writes no attribute, so an after-read blob reads sa0-sa2 as the bank
; held them before the emit, and its three tim lines stop the EDM tick as crumb3's do.

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: T1's value (crumb3's douta control of attribute 0)
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's), unread
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's), unread
        .word 0x200     ; dword 6 = ds1[2]: T2's value (crumb3's douta control of attribute 2)
        .word 0x005a3305 ; dword 7 = ds1[3]: T3's value
        .word 0         ; dword 8 = ds0[4]: the third row, unused
        .word 0         ; dword 9 = ds0[5]
        .word 0         ; dword 10 = ds1[4]
        .word 0         ; dword 11 = ds1[5]

        movs tim, ds1[1], ds1[1], ds1[1], ds1[1]        ; T1: tim <- 0x000
        movs tim, ds1[2], ds1[2], ds1[2], ds1[2]        ; T2: tim <- 0x200
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        movs tim, ds1[3], ds1[3], ds1[3], ds1[3]        ; T3: tim <- 0x005a3305
        halt
