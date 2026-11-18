; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; crumb.s -- emit.s with three breadcrumbs in tim (round 37, N3b step B).
;
; The same data rows, control word, address rule and kernel fills as emit.s (U0, V0, V2), and the
; same douta, douta, doutu; three movs tim mark how far the program ran. tim is EVENT_TIMER
; (0x0acc), which the host reads back; a movs tim keeps its first word's bits 24-0 and, with
; bit 24 clear, the value stays put until a GPU reset (doc/specs/pds_isa.md,
; doc/isa/content/pds/probe/inputs.md). No marker has bit 24 set, so none is a running count:
; the EDM tick stops at T1 by design, until the next reset.
; T1 = 0x000 (the program started), T2 = 0x200 (past both douta), T3 = 0x005a3305 (past the
; doutu). 2 data rows (8 dwords; the banks interleave by pairs of dwords, doc/specs/hw_spec.md
; section 2).

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1, no flag
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]: douta control, attribute 0; T1's value
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]: douta control, attribute 2; T2's value
        .word 0x005a3305 ; dword 7 = ds1[3]: T3's value

        movs tim, ds1[1], ds1[1], ds1[1], ds1[1]        ; T1: tim <- 0x000
        movs douta, ds0[2], ds1[1], ds0[2], ds0[2]      ; V0 to attribute 0
        movs douta, ds0[3], ds1[2], ds0[3], ds0[3]      ; V2 to attribute 2
        movs tim, ds1[2], ds1[2], ds1[2], ds1[2]        ; T2: tim <- 0x200
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]      ; start entry 1 of the blob
        movs tim, ds1[3], ds1[3], ds1[3], ds1[3]        ; T3: tim <- 0x005a3305
        halt
