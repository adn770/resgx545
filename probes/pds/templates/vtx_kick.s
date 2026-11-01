; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; vtx_kick.s -- the vertex PDS program of the kick probes (tri-vtx.toml, slot vtxpds):
; asm/tri/pds_vtx.s with its (if0) doutu replaced by KICK, the shader start under the
; predicate a probe puts to the test. The VDM runs it per vertex of the triangle's index
; list (0, 1, 2), ir0 the vertex index; it DMAs the vertex into pa0-pa3 as the default
; does, then KICK starts the vertex shader (vtx_dump.s, the vtxuse helper) or not. KICK is
; "movs doutu, ds0[2], ds0[3], ds1[1], ds1[1]" under some predicate, maybe more than once.
;
; Data segment, 8 dwords, the default's layout: the host patches dwords 0, 1, 2 and 4 (the
; vertex buffer, the doutd word, the stride, the shader's U0); U1 (dword 5) and U2 (dword 3)
; stay 0.
        .word 0          ; dword 0 = ds0[0]: vertex buffer address (patched)
        .word 0          ; dword 1 = ds0[1]: doutd word (patched)
        .word 0          ; dword 2 = ds1[0]: stride (patched)
        .word 0          ; dword 3 = ds1[1]: DOUTU U2 = 0
        .word 0          ; dword 4 = ds0[2]: DOUTU U0 (patched)
        .word 0          ; dword 5 = ds0[3]: DOUTU U1 = 0
        .word 0          ; dword 6 = ds1[2]: unused
        .word 0          ; dword 7 = ds1[3]: unused

        mul ds1[50], ir0.l, ds1[0].l
        movsa doutd, ds0[0], ds0[1], ds1[50], ds1[50]
{KICK}
        halt
