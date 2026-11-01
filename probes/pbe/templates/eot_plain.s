; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The end-of-tile program of the triangle probes that vary the sideband (--slot
; eot=eot_plain.bin --sideband V): use_eot.s as it is. Instructions 1-4 are the four movs
; the host patches with PBE words 0-3 (registers r0-r3) and the last instruction is the
; emitpix2 that gets the sideband. Temporaries r0-r3.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
emitpix1.freep #0 /* incp */, r0, r1
emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
