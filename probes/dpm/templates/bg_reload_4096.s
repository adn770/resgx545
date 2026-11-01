; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The background object's pixel shader of the partial-reload script (Q038; probe --tri bgpixel,
; with the bgpds program pds_bg_pos.s, which iterates the pixel's position into pa0, pa1): the colour
; is the render target's own texel at the pixel, a strided 4096x4096 ARGB8888 texture (the copy's
; words) whose address is the target's (TARGET_IMM), fetched by smp2dreplace at the coordinates
; (x + 0.5) / 4096 and (y + 0.5) / 4096, nearest, LOD 0.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x39800000
mov.skipinv r3, #0x39800000
mov.skipinv r2, #0x00000000
fmad.skipinv r24, pa0, r1, r2
fmad.skipinv r25, pa1, r3, r2
mov r20, #0x03FE0E00
mov r21, #0xCCFFFFFF
mov r22, #0x5CB00000
mov r23, #0xA0800000
mov r26, #0x00000000
smp2dreplace r10, r24, r20, r26, drc0
wdf drc0
mov.skipinv.end o0, r10
