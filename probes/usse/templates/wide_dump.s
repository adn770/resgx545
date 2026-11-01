; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (wide, 48 temporaries): r1-r16 hold n * 0x01010101 (sources), r20-r39
; 0xD1D2D300 + k (markers), r46 the address of scratch dword 64 (whose dwords keep their fill,
; 0xD0000000 | index), then OP; r20-r39 and r1-r16 stored to scratch dwords 0-35 and register
; OUT as the pixel. For the repeat counts and the load fetch counts.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x01010101
mov.skipinv r2, #0x02020202
mov.skipinv r3, #0x03030303
mov.skipinv r4, #0x04040404
mov.skipinv r5, #0x05050505
mov.skipinv r6, #0x06060606
mov.skipinv r7, #0x07070707
mov.skipinv r8, #0x08080808
mov.skipinv r9, #0x09090909
mov.skipinv r10, #0x0A0A0A0A
mov.skipinv r11, #0x0B0B0B0B
mov.skipinv r12, #0x0C0C0C0C
mov.skipinv r13, #0x0D0D0D0D
mov.skipinv r14, #0x0E0E0E0E
mov.skipinv r15, #0x0F0F0F0F
mov.skipinv r16, #0x10101010
mov.skipinv r20, #0xD1D2D300
mov.skipinv r21, #0xD1D2D301
mov.skipinv r22, #0xD1D2D302
mov.skipinv r23, #0xD1D2D303
mov.skipinv r24, #0xD1D2D304
mov.skipinv r25, #0xD1D2D305
mov.skipinv r26, #0xD1D2D306
mov.skipinv r27, #0xD1D2D307
mov.skipinv r28, #0xD1D2D308
mov.skipinv r29, #0xD1D2D309
mov.skipinv r30, #0xD1D2D30A
mov.skipinv r31, #0xD1D2D30B
mov.skipinv r32, #0xD1D2D30C
mov.skipinv r33, #0xD1D2D30D
mov.skipinv r34, #0xD1D2D30E
mov.skipinv r35, #0xD1D2D30F
mov.skipinv r36, #0xD1D2D310
mov.skipinv r37, #0xD1D2D311
mov.skipinv r38, #0xD1D2D312
mov.skipinv r39, #0xD1D2D313
mov.skipinv r46, #0x5CAF0100
{OP}
mov.skipinv r47, #0x5CAF0000
stad [r47,+#0], r20
stad [r47,+#1], r21
stad [r47,+#2], r22
stad [r47,+#3], r23
stad [r47,+#4], r24
stad [r47,+#5], r25
stad [r47,+#6], r26
stad [r47,+#7], r27
stad [r47,+#8], r28
stad [r47,+#9], r29
stad [r47,+#10], r30
stad [r47,+#11], r31
stad [r47,+#12], r32
stad [r47,+#13], r33
stad [r47,+#14], r34
stad [r47,+#15], r35
stad [r47,+#16], r36
stad [r47,+#17], r37
stad [r47,+#18], r38
stad [r47,+#19], r39
stad [r47,+#20], r1
stad [r47,+#21], r2
stad [r47,+#22], r3
stad [r47,+#23], r4
stad [r47,+#24], r5
stad [r47,+#25], r6
stad [r47,+#26], r7
stad [r47,+#27], r8
stad [r47,+#28], r9
stad [r47,+#29], r10
stad [r47,+#30], r11
stad [r47,+#31], r12
stad [r47,+#32], r13
stad [r47,+#33], r14
stad [r47,+#34], r15
stad [r47,+#35], r16
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
