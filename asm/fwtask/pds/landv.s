; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; landv.s -- land with V0 and V2 (round 42, N3g row LV, the user's decision D (a)).
;
; 3 data rows, as PDS #14 has, so the kernel's control word is (3 << 23) | 0x100 = 0x01800100,
; #14's own. Row r holds ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md, the data
; segment). crumb3's two douta (V0 to attribute 0, V2 to attribute 2, the kernel's fills at dwords
; 4 and 5 as in crumb3), then land's two douta of its markers, Ma to secondary attribute 24 and Mb
; to 26, now from the third row with their controls at ds1[3] and ds1[4]; land's doutu and halt,
; no tim, so nothing here stops the EDM tick. Against land only V0 and V2 to attributes 0 and 2
; are added. The kernel fills U0, V0 and V2 (SGX_OWN_PDS_LANDV_FILLV 1).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2
        .word 0x1800    ; dword 7 = ds1[3]: douta control, attribute 24
        .word 0x5a5a3a18 ; dword 8 = ds0[4]: Ma
        .word 0x5a5a3a1a ; dword 9 = ds0[5]: Mb
        .word 0x1a00    ; dword 10 = ds1[4]: douta control, attribute 26
        .word 0         ; dword 11 = ds1[5]: unused

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs douta, ds0[4], ds1[3], ds0[4], ds0[4]      ; Ma to attribute 24
        movs douta, ds0[5], ds1[4], ds0[5], ds0[5]      ; Mb to attribute 26
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
