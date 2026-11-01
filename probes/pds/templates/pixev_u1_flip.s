; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Pixel-event program with a field of the end-of-tile task's U1 flipped (sgxfive-test probe
; --tri pixev:60): the triangle's pixel-event program, asm/transfer/pds_pixevent.s, with the
; tile_x field (U1 bits 11:3) XORed with XMASK and the tile_y field (U1 bits 21:12) with
; YMASK before the end-of-tile task starts. The default end-of-tile program writes the tile's
; pixels where its U1 says, so the pixels of a render of several tiles show which tile each
; event's task went to. A mask of 0 leaves the field alone.
;
; The data segment is pds_pixevent.s's, dword for dword (the host patches dwords 0-5 and 12
; as it does the default's), with row 13 the tile masks and row 15 the two flip masks: ds0[30]
; and ds1[30] hold XMASK, ds0[31] and ds1[31] YMASK.

        .word 0          ; dword 0  = ds0[0]: PTOFF task U0 (patched)
        .word 0          ; dword 1  = ds0[1]: PTOFF task U1 (patched: 0)
        .word 0          ; dword 2  = ds1[0]: unused (patched: 0)
        .word 0          ; dword 3  = ds1[1]: EOT task U0 (patched)
        .word 0          ; dword 4  = ds0[2]: EOR task U0 (patched)
        .word 0          ; dword 5  = ds0[3]: EOR task U1 (patched: 0x00c00000)
        .word 0x00000008 ; dword 6  = ds1[2]: ir1 bit 3, PTOFF
        .word 0x00000002 ; dword 7  = ds1[3]: ir1 bit 1, end of tile
        .word 0x00000100 ; dword 8  = ds0[4]: ir1 bit 8, end of render instead
        .word 0x00000FF8 ; dword 9  = ds0[5]: tile_x mask, U1 [11:3]
        .word 0x00000004 ; dword 10 = ds1[4]: ir1 bit 2, end of render
        .word 0          ; dword 11 = ds1[5]: unused
        .word 0          ; dword 12 = ds0[6]: EOT task U1 base (patched: 0x00800000)
        .word 0x003FF000 ; dword 13 = ds0[7]: tile_y mask, U1 [21:12]
        .word 0          ; dword 14 = ds1[6]: unused
        .word 0          ; dword 15 = ds1[7]: unused
        .word 0x00400000 ; dword 16 = ds0[8]: ENDOFRENDER, U1 bit 22
        .word 0          ; dword 17 = ds0[9]: unused
        .word 0          ; dword 18 = ds1[8]: unused
        .word 0          ; dword 19 = ds1[9]: unused
        .word 0x7E570000, 0x7E570001, 0x000, 0x100      ; rows 5-12: markers, controls
        .word 0x7E570002, 0x7E570003, 0x200, 0x300
        .word 0x7E570004, 0x7E570005, 0x400, 0x500
        .word 0x7E570006, 0x7E570007, 0x600, 0x700
        .word 0x7E570008, 0x7E570009, 0x800, 0x900
        .word 0x7E57000A, 0x7E57000B, 0xA00, 0xB00
        .word 0x7E57000C, 0x7E57000D, 0xC00, 0xD00
        .word 0x7E57000E, 0x7E57000F, 0xE00, 0xF00
        .word 0x000003FF, 0, 0x00400000, 0x00000003     ; row 13: masks
        .word 0, 0, 0, 0                                ; row 14: zeros
        .word {XMASK}, {YMASK}, {XMASK}, {YMASK}        ; row 15: ds0[30], ds0[31], ds1[30], ds1[31]

        ; PTOFF: ir1 bit 3.
        and ds1[48], ir1, ds1[2]
        tstz p0, ds1[48]
        (p0) bra not_ptoff
        movs doutu, ds0[0], ds0[1], ds0[0], ds0[0]
        halt

not_ptoff:
        ; End of tile: ir1 bit 1.
        and ds1[48], ir1, ds1[3]
        tstz p0, ds1[48]
        (p0) bra not_eot
        ; With ir1 bit 8 also set, run the end-of-render task instead.
        not ds1[48], ir1
        and ds1[48], ds0[4], ds1[48]
        tstz p0, ds1[48]
        (p0) bra eor
        ; The tile's slot word in ds0[63].
        shr ds1[63], ir0, 9
        and ds0[63], ds0[26], ds1[63]                   ; tile_y
        shl ds1[63], ds0[63], 2
        and ds0[62], ir0, ds1[27]                       ; tile_x & 3
        or ds0[63], ds0[62], ds1[63]
        or ds0[63], ds0[63], ds1[26]                    ; (64 << 16) | slot

        ; U1 = base | tile_x | tile_y | ENDOFRENDER, as pds_pixevent.s.
        shl ds1[48], ir0, 3
        and ds1[48], ds0[5], ds1[48]
        xor ds1[48], ds0[30], ds1[48]                   ; tile_x ^ XMASK
        or ds0[48], ds0[6], ds1[48]
        shl ds1[48], ir0, 3
        and ds1[48], ds0[7], ds1[48]
        xor ds1[48], ds0[31], ds1[48]                   ; tile_y ^ YMASK
        or ds0[48], ds0[48], ds1[48]
        shl ds1[48], ir1, 20
        and ds1[48], ds0[8], ds1[48]
        or ds0[48], ds0[48], ds1[48]
        movs doutu, ds1[1], ds0[48], ds0[48], ds0[48]
        halt

not_eot:
        ; End of render: ir1 bit 2.
        and ds1[48], ir1, ds1[4]
        tstz p0, ds1[48]
        (p0) bra done
eor:
        movs doutu, ds0[2], ds0[3], ds0[2], ds0[2]
done:
        halt
