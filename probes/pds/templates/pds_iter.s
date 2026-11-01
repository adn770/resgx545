; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's primary pixel PDS program for the iteration probes (sgxfive-test probe --tri
; pixpds:8): as asm/transfer/pds_prim.s it starts the pixel shader (the pixel slot's, e.g.
; pix_pa.s), then has the iterator write the DOUTI pair {A}, 0 into the task's primary
; attributes, as pds_prim_1src.s does for the copy without its texture fetch. The host patches
; data dwords 0 and 1 with the shader's U0 and U1 (sgxfive_tri_probe.h, pixpds).

        .word 0          ; dword 0 = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1 = ds0[1]: U1 (patched: 4)
        .word 0          ; dword 2 = ds1[0]: U2 = 0
        .word 0          ; dword 3 = ds1[1]: unused
        .word {A}        ; dword 4 = ds0[2]: DOUTI word 0
        .word 0          ; dword 5 = ds0[3]: DOUTI word 1
        .word 0          ; dword 6 = ds1[2]: unused
        .word 0          ; dword 7 = ds1[3]: unused

        movs doutu, ds0[0], ds0[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        halt
