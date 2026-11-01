; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pds_iter_pt.s with DOUTU1.BIT2 clear (U1 0x01000000)
; for probes that replace the pixel shader (slot pixpds): doutu first with U1 0x01000000
; (DOUTU1.WAIT_ITER), then two iterations: source 1, two components (pa0, pa1; the copy's z
; with vtx_z.s in pa0), and source 34, three components, smooth and perspective as the
; DOUTI0 0x27811000, with DOUTI0.LAST_ITER (pa2-pa4).

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x01000000 ; dword 3  = ds1[1]: U1, waiting for the iterations, bit 2 clear
        .word 0x00400800 ; dword 4  = ds0[2]: DOUTI word 0, source 1, two components
        .word 0          ; dword 5  = ds0[3]: DOUTI word 1
        .word 0x27811000 ; dword 6  = ds1[2]: DOUTI word 0, source 34, LAST_ITER
        .word 0          ; dword 7  = ds1[3]: DOUTI word 1
        .word 0          ; dword 8  = ds0[4]: unused
        .word 0          ; dword 9  = ds0[5]: unused
        .word 0          ; dword 10 = ds1[4]: unused
        .word 0          ; dword 11 = ds1[5]: unused

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        movs douti, ds1[2], ds1[3], ds1[2], ds1[2]
        halt
