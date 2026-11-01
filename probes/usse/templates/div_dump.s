; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (integer division over a register run): r1-r9 hold the inputs A-I,
; r10-r29 0xA0A1A200 + k; then OP; r10-r29 stored to scratch dwords 0-19 and r1-r9 to
; dwords 20-28, and register OUT as the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #{A}
mov.skipinv r2, #{B}
mov.skipinv r3, #{C}
mov.skipinv r4, #{D}
mov.skipinv r5, #{E}
mov.skipinv r6, #{F}
mov.skipinv r7, #{G}
mov.skipinv r8, #{H}
mov.skipinv r9, #{I}
mov.skipinv r10, #0xA0A1A20A
mov.skipinv r11, #0xA0A1A20B
mov.skipinv r12, #0xA0A1A20C
mov.skipinv r13, #0xA0A1A20D
mov.skipinv r14, #0xA0A1A20E
mov.skipinv r15, #0xA0A1A20F
mov.skipinv r16, #0xA0A1A210
mov.skipinv r17, #0xA0A1A211
mov.skipinv r18, #0xA0A1A212
mov.skipinv r19, #0xA0A1A213
mov.skipinv r20, #0xA0A1A214
mov.skipinv r21, #0xA0A1A215
mov.skipinv r22, #0xA0A1A216
mov.skipinv r23, #0xA0A1A217
mov.skipinv r24, #0xA0A1A218
mov.skipinv r25, #0xA0A1A219
mov.skipinv r26, #0xA0A1A21A
mov.skipinv r27, #0xA0A1A21B
mov.skipinv r28, #0xA0A1A21C
mov.skipinv r29, #0xA0A1A21D
{OP}
mov.skipinv r30, #0x5CAF0000
stad [r30,+#0], r10
stad [r30,+#1], r11
stad [r30,+#2], r12
stad [r30,+#3], r13
stad [r30,+#4], r14
stad [r30,+#5], r15
stad [r30,+#6], r16
stad [r30,+#7], r17
stad [r30,+#8], r18
stad [r30,+#9], r19
stad [r30,+#10], r20
stad [r30,+#11], r21
stad [r30,+#12], r22
stad [r30,+#13], r23
stad [r30,+#14], r24
stad [r30,+#15], r25
stad [r30,+#16], r26
stad [r30,+#17], r27
stad [r30,+#18], r28
stad [r30,+#19], r29
stad [r30,+#20], r1
stad [r30,+#21], r2
stad [r30,+#22], r3
stad [r30,+#23], r4
stad [r30,+#24], r5
stad [r30,+#25], r6
stad [r30,+#26], r7
stad [r30,+#27], r8
stad [r30,+#28], r9
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
