; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template: the case's setup PRE, then sixteen source operands S0-S15 stored as they are
; (any bank stad takes, c and g included) to scratch dwords 0-15 (expected as a list), and
; register OUT as the pixel.
phas #0, #0, pixel, end, parallel
{PRE}
mov.skipinv r29, #0x5CAF0000
stad [r29,+#0], {S0}
stad [r29,+#1], {S1}
stad [r29,+#2], {S2}
stad [r29,+#3], {S3}
stad [r29,+#4], {S4}
stad [r29,+#5], {S5}
stad [r29,+#6], {S6}
stad [r29,+#7], {S7}
stad [r29,+#8], {S8}
stad [r29,+#9], {S9}
stad [r29,+#10], {S10}
stad [r29,+#11], {S11}
stad [r29,+#12], {S12}
stad [r29,+#13], {S13}
stad [r29,+#14], {S14}
stad [r29,+#15], {S15}
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
