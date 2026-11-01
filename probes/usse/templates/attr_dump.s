; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template: the case's setup PRE and OP, then thirty-two source operands S0-S31
; stored as they are to scratch dwords 0-31, and register OUT as the pixel. For a write whose
; destination is not known: the attribute and output banks read back around it.
phas #0, #0, pixel, end, parallel
{PRE}
{OP}
mov.skipinv r30, #0x5CAF0000
stad [r30,+#0], {S0}
stad [r30,+#1], {S1}
stad [r30,+#2], {S2}
stad [r30,+#3], {S3}
stad [r30,+#4], {S4}
stad [r30,+#5], {S5}
stad [r30,+#6], {S6}
stad [r30,+#7], {S7}
stad [r30,+#8], {S8}
stad [r30,+#9], {S9}
stad [r30,+#10], {S10}
stad [r30,+#11], {S11}
stad [r30,+#12], {S12}
stad [r30,+#13], {S13}
stad [r30,+#14], {S14}
stad [r30,+#15], {S15}
stad [r30,+#16], {S16}
stad [r30,+#17], {S17}
stad [r30,+#18], {S18}
stad [r30,+#19], {S19}
stad [r30,+#20], {S20}
stad [r30,+#21], {S21}
stad [r30,+#22], {S22}
stad [r30,+#23], {S23}
stad [r30,+#24], {S24}
stad [r30,+#25], {S25}
stad [r30,+#26], {S26}
stad [r30,+#27], {S27}
stad [r30,+#28], {S28}
stad [r30,+#29], {S29}
stad [r30,+#30], {S30}
stad [r30,+#31], {S31}
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
