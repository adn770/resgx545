; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The layered background's raw-coordinate primary (Q190, round 9 L-RAW; probe --tri bgpds:12
; --bg-layer, with a pix_pa0.s or pix_pa1.s background shader as the bgpixel slot): the copy's
; pds_prim_1src.s with DOUTI word 0 = 0x40400801, coordinate set 1 with two components and the
; fetch bit, so the iterator hands the shader the set's u in pa0 and v in pa1 instead of a
; texel (a fetch is issued all the same: DOUTU1 0x02000004 waits for it, as every program that
; reads a coordinate set does, doc/specs/3d.md section 12.2). The texture is a 16 x 16 RGBA8888
; one in the probe's scratch buffer; data dwords 0 and 1 are the shader's U0 and U1, patched.
; The word is measured on a triangle's vertex coordinate set (probes/usse/templates/
; pds_iter_xy.s, the same data and code: E709, E878, E905), not yet on the layered background's
; coordinate set: the first rows of the session are the check.

        .word 0          ; dword 0  = ds0[0]: U0 of the pixel shader (patched)
        .word 0          ; dword 1  = ds0[1]: U1 (patched: 4; not used)
        .word 0          ; dword 2  = ds1[0]: U2 = 0
        .word 0x02000004 ; dword 3  = ds1[1]: U1, waiting for the fetch
        .word 0x40400801 ; dword 4  = ds0[2]: DOUTI word 0
        .word 0          ; dword 5  = ds0[3]: DOUTI word 1
        .word 0x5CAF0000 ; dword 6  = ds1[2]: T2, the scratch buffer (patched)
        .word 0x00800800 ; dword 7  = ds1[3]: T3
        .word 0x07fe0000 ; dword 8  = ds0[4]: T0, nearest, repeat
        .word 0x0d00f00f ; dword 9  = ds0[5]: T1, RGBA8888, POT, 16x16
        .word 0          ; dword 10 = ds1[4]: unused
        .word 0          ; dword 11 = ds1[5]: unused

        movs doutu, ds0[0], ds1[1], ds1[0], ds0[0]
        movs douti, ds0[2], ds0[3], ds0[2], ds0[2]
        movs doutt, ds0[4], ds0[5], ds1[2], ds1[3]
        halt
