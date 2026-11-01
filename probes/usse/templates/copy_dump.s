; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template: the case's setup PRE and OP, then twenty-nine operands S0-S28 moved to
; r0-r28 and stored to scratch dwords 0-28, and register OUT as the pixel. For a write whose
; destination is not known: banks a store does not take as its source read through a move.
phas #0, #0, pixel, end, parallel
{PRE}
{OP}
mov.skipinv r0, {S0}
mov.skipinv r1, {S1}
mov.skipinv r2, {S2}
mov.skipinv r3, {S3}
mov.skipinv r4, {S4}
mov.skipinv r5, {S5}
mov.skipinv r6, {S6}
mov.skipinv r7, {S7}
mov.skipinv r8, {S8}
mov.skipinv r9, {S9}
mov.skipinv r10, {S10}
mov.skipinv r11, {S11}
mov.skipinv r12, {S12}
mov.skipinv r13, {S13}
mov.skipinv r14, {S14}
mov.skipinv r15, {S15}
mov.skipinv r16, {S16}
mov.skipinv r17, {S17}
mov.skipinv r18, {S18}
mov.skipinv r19, {S19}
mov.skipinv r20, {S20}
mov.skipinv r21, {S21}
mov.skipinv r22, {S22}
mov.skipinv r23, {S23}
mov.skipinv r24, {S24}
mov.skipinv r25, {S25}
mov.skipinv r26, {S26}
mov.skipinv r27, {S27}
mov.skipinv r28, {S28}
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
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
