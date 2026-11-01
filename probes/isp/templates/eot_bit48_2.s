; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; eot_plain.s with bit 48 of its emitpix2 set (the multisample probes: bit 48 is
; not a field our tables decode, so the emits are raw words: emitpix1.freep #0, r0, r1 and
; emitpix2.end.freep #0, r2, r3, r0, #0 as eot_plain.s assembles them). The host patches the
; four movs and the last instruction's sideband as for eot_plain.s.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
.long 0xFB20010000200080                         ; emitpix1.freep #0, r0, r1
.long 0xFB25000000208180                         ; emitpix2.end.freep #0, r2, r3, r0, #0 + bit 48
