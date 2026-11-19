; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; halt.s -- the program floor (round 38, N3c row R5): emit.s's data rows and nothing but halt.
;
; The same 2 data rows as emit.s (the kernel fills U0, V0 and V2 at the arm as for emit.s; no
; instruction reads them), the same control word (2 rows, addend 0x100) and address rule, and
; one instruction: halt. No douta, no doutu, no tim: if the EDM still stops after this emit, the
; stop needs no instruction of the emitted program. The task's entry 1 is never started, so the
; job never reports done.

        .word 0         ; dword 0 = ds0[0]: U0 (the kernel's)
        .word 0         ; dword 1 = ds0[1]: U1
        .word 0         ; dword 2 = ds1[0]: U2
        .word 0         ; dword 3 = ds1[1]
        .word 0         ; dword 4 = ds0[2]: V0 (the kernel's)
        .word 0         ; dword 5 = ds0[3]: V2 (the kernel's)
        .word 0x200     ; dword 6 = ds1[2]
        .word 0         ; dword 7 = ds1[3]

        halt
