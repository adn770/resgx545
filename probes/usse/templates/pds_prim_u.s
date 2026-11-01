; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pds_prim_u.s -- the triangle's primary pixel PDS program (slot pixpds) as pds_prim.s, with
; its doutu's U1 ORed with MASK and U2 set to U2: which task-word bits change how the pixel
; shader runs (the per-sample rate, say). Dwords 0 and 1 (U0, U1) are the host's.
        .word 0         ; dword 0 = ds0[0]: U0 (patched)
        .word 0         ; dword 1 = ds0[1]: U1 (patched)
        .word {U2}      ; dword 2 = ds1[0]: U2
        .word {MASK}    ; dword 3 = ds1[1]: ORed into U1
        or ds0[1], ds0[1], ds1[1]
        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        halt
