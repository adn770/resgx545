; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; emitpds probe addend 0x2000 (phase 11.27, the 11.24 base with this addend): r2 control word, r3 s1 (the PDS secondary's
; address >> 4, patched), r4/r5 s2, p0 set on the one instance whose pa0 (a copy: its texel) is 0; reads scratch dword 0 before the emit (r6, dword 8)
; and sixteen times after it (dwords 16-31); no loop, nothing unbounded.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x5CAF0000
mov.skipinv r2, #0x01002000
mov.skipinv r3, #0x5CB00000
mov.skipinv r4, #0xe17d0001
mov.skipinv r5, #0xE17D0002
ldad.bypassl1 r6, [r1,+#0], drc0
wdf drc0
mov.skipinv r7, pa0
xor.testtaz.chan0 !c0, p0, r7, #0
!p0 br #2
emitpds.tasks.taske #0, r2, r3, r4, #0x0
ldad.bypassl1 r16, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r17, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r18, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r19, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r20, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r21, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r22, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r23, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r24, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r25, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r26, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r27, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r28, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r29, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r30, [r1,+#0], drc0
wdf drc0
ldad.bypassl1 r31, [r1,+#0], drc0
wdf drc0
stad [r1,+#8], r6
stad [r1,+#16], r16
stad [r1,+#17], r17
stad [r1,+#18], r18
stad [r1,+#19], r19
stad [r1,+#20], r20
stad [r1,+#21], r21
stad [r1,+#22], r22
stad [r1,+#23], r23
stad [r1,+#24], r24
stad [r1,+#25], r25
stad [r1,+#26], r26
stad [r1,+#27], r27
stad [r1,+#28], r28
stad [r1,+#29], r29
stad [r1,+#30], r30
stad [r1,+#31], r31
idf drc0, bif
wdf drc0
mov.skipinv.end o0, #0x0DA7A000
