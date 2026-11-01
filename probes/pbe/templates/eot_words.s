; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The end-of-tile program of the PBE word probes (--tri eot): use_eot.s with one PBE word
; changed before the emits. Instructions 1-4 are the four movs the host patches with PBE
; words 0-3 (registers r0-r3), the last is the emitpix2 that gets the sideband; between them
; {R} = {R} & {AND} | {OR} through r4 and r5. Temporaries r0-r5.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r4, #{AND}
and.skipinv {R}, {R}, r4
mov.skipinv r5, #{OR}
or.skipinv {R}, {R}, r5
emitpix1.freep #0 /* incp */, r0, r1
emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
