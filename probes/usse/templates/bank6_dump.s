; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (destination bank 6): r0-r25 hold 0xE0E1E200 + k, i0-i2 0x11110000 + k,
; i.l and i.h 0; then OP; r0-r25, i0-i2 and the registers r[il + #0] and r[ih + #0] (so the
; index registers' values show as the number they select) stored to scratch dwords 0-30, and
; register OUT as the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0xE0E1E200
mov.skipinv r1, #0xE0E1E201
mov.skipinv r2, #0xE0E1E202
mov.skipinv r3, #0xE0E1E203
mov.skipinv r4, #0xE0E1E204
mov.skipinv r5, #0xE0E1E205
mov.skipinv r6, #0xE0E1E206
mov.skipinv r7, #0xE0E1E207
mov.skipinv r8, #0xE0E1E208
mov.skipinv r9, #0xE0E1E209
mov.skipinv r10, #0xE0E1E20A
mov.skipinv r11, #0xE0E1E20B
mov.skipinv r12, #0xE0E1E20C
mov.skipinv r13, #0xE0E1E20D
mov.skipinv r14, #0xE0E1E20E
mov.skipinv r15, #0xE0E1E20F
mov.skipinv r16, #0xE0E1E210
mov.skipinv r17, #0xE0E1E211
mov.skipinv r18, #0xE0E1E212
mov.skipinv r19, #0xE0E1E213
mov.skipinv r20, #0xE0E1E214
mov.skipinv r21, #0xE0E1E215
mov.skipinv r22, #0xE0E1E216
mov.skipinv r23, #0xE0E1E217
mov.skipinv r24, #0xE0E1E218
mov.skipinv r25, #0xE0E1E219
mov.skipinv i0, #0x11110000
mov.skipinv i1, #0x11110001
mov.skipinv i2, #0x11110002
mov.skipinv i.l, #0
mov.skipinv i.h, #0
{OP}
mov.skipinv r26, i0
mov.skipinv r27, i1
mov.skipinv r28, i2
mov.skipinv r29, r[il + #0]
mov.skipinv r31, r[ih + #0]
mov.skipinv r30, #0x5CAF0000
stad [r30,+#0], r0
stad [r30,+#1], r1
stad [r30,+#2], r2
stad [r30,+#3], r3
stad [r30,+#4], r4
stad [r30,+#5], r5
stad [r30,+#6], r6
stad [r30,+#7], r7
stad [r30,+#8], r8
stad [r30,+#9], r9
stad [r30,+#10], r10
stad [r30,+#11], r11
stad [r30,+#12], r12
stad [r30,+#13], r13
stad [r30,+#14], r14
stad [r30,+#15], r15
stad [r30,+#16], r16
stad [r30,+#17], r17
stad [r30,+#18], r18
stad [r30,+#19], r19
stad [r30,+#20], r20
stad [r30,+#21], r21
stad [r30,+#22], r22
stad [r30,+#23], r23
stad [r30,+#24], r24
stad [r30,+#25], r25
stad [r30,+#26], r26
stad [r30,+#27], r27
stad [r30,+#28], r28
stad [r30,+#29], r29
stad [r30,+#30], r31
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
