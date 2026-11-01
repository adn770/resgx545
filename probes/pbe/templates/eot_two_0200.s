; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; An end-of-tile program that emits the tile twice (SIDEBAND.BIT9): first
; with sideband 0x0200 and without .end or .freep, then as eot_plain.s, whose last emitpix2 gets
; the probe's sideband. Instructions 1-4 are the four movs the host patches with
; PBE words 0-3 (registers r0-r3). Temporaries r0-r3.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
emitpix1 #0 /* incp */, r0, r1
emitpix2 #0 /* incp */, r2, r3, r0, #0x0200
emitpix1.freep #0 /* incp */, r0, r1
emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
