; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; land.s -- where an emitted douta lands (round 40, N3e row L, the user's decision C (a)).
;
; crumb3's layout: 3 data rows, as PDS #14 has, so the kernel's control word is (3 << 23) | 0x100
; = 0x01800100, #14's own. Row r holds ds0[2r], ds0[2r+1], ds1[2r], ds1[2r+1] (doc/specs/pds_isa.md,
; the data segment). crumb3's two douta, its doutu and its halt keep their words and operands; its
; three tim lines and T3's dword are gone, so nothing here stops the EDM tick. The two douta write
; markers that are constants of the image, not kernel fills: Ma to secondary attribute 24, Mb to
; attribute 26 (douta control bits 19:8 name the attribute, pds_isa.md section 3). Row D0
; (r40-d0-survey) read sa24 to sa31 zero and unchanged across an emit, and no firmware instruction
; reads sa20, sa21 or sa23 to sa31 (doc/specs/edm_dataflow.md). The kernel fills U0 only (dwords 4
; and 5 are Ma and Mb, not V0 and V2: SGX_OWN_PDS_LAND_FILLV 0).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0x1800    ; dword 3 = ds1[1]: douta control, attribute 24
        .word 0x5a5a3a18 ; dword 4 = ds0[2]: Ma
        .word 0x5a5a3a1a ; dword 5 = ds0[3]: Mb
        .word 0x1a00    ; dword 6 = ds1[2]: douta control, attribute 26
        .word 0         ; dword 7 = ds1[3]: unused (crumb3's T3)
        .word 0         ; dword 8 = ds0[4]: the third row, unused
        .word 0         ; dword 9 = ds0[5]
        .word 0         ; dword 10 = ds1[4]
        .word 0         ; dword 11 = ds1[5]

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; Ma to attribute 24
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; Mb to attribute 26
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
