; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; emit.s -- the one PDS program a firmware task of ours may emit (round 33, N3).
;
; The kernel keeps it as a constant (sgx_own_pds.h, written by tools/fwtask/gen_verify.py) in a
; page of its own, read-only for the EDM, and fills four dwords at the arm: U0 (the doutu word of
; the task's entry 1: TRC 8, CBASE 15, index 0x4000 + 1), V0 and V2 (TA3DCtl dwords 0 and 2 as
; the loader built them: the values sa0 and sa2 hold, PDS #11's doutd, E002, E003). The douta
; targets are PDS #14's, attributes 0 and 2 (E146); the values are the ones those secondary
; attributes already hold, so a write that lands there changes nothing the firmware reads.
; Written from doc/specs/pds_isa.md (movs ports, the douta control, doutu U0-U2) and
; doc/specs/fw_format.md section 4 (PDS_CTL, ADDR_SHR4). 2 data rows (8 dwords; the banks
; interleave by pairs of dwords, doc/specs/hw_spec.md section 2).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2
        .word 0         ; dword 7 = ds1[3]: unused

        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        halt
