; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The end-of-tile program of the triangle probes (sgxfive-test probe --tri ... --slot
; eot=eot_dump.bin): use_eot.s with a dump of the task's secondary attributes, which a
; probe's pixel-event program wrote with douta, to scratch dwords 0-15 (expected as a list,
; as sa_dump.s's). Every tile runs it, so with several tiles the last one's values stay:
; use a one-tile target (32x16) or eot_tile.s.
;
; As use_eot.s, instructions 1-4 are the four movs the host patches with PBE words 0-3
; (registers r0-r3) and the last instruction is the emitpix2 that gets the sideband.
; Temporaries r0-r4: run with --temps 8.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov r4, #0x5CAF0000
stad [r4,+#0], sa0
stad [r4,+#1], sa1
stad [r4,+#2], sa2
stad [r4,+#3], sa3
stad [r4,+#4], sa4
stad [r4,+#5], sa5
stad [r4,+#6], sa6
stad [r4,+#7], sa7
stad [r4,+#8], sa8
stad [r4,+#9], sa9
stad [r4,+#10], sa10
stad [r4,+#11], sa11
stad [r4,+#12], sa12
stad [r4,+#13], sa13
stad [r4,+#14], sa14
stad [r4,+#15], sa15
idf drc0, bif
wdf drc0
emitpix1.freep #0 /* incp */, r0, r1
emitpix2.end.freep #0 /* incp */, r2, r3, r0, #0x00000000
