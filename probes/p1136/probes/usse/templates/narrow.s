; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (phase 11.37, prepared): narrow memory forms in a client fill.  Scratch dwords 16
; and 17 are preset with A and C by two stad (every instance stores the same value), r28 is the
; region base (BASE, optionally plus a few bytes), r5 the narrow store's source (B), r10-r17 preset markers; the
; instruction(s) OP; then r10-r17 are dumped to scratch dwords 0-7 and r10 is the pixel.  The host
; sees dwords 16 and 17 after the job, so a narrow store shows exactly the bytes it changed.
phas #0, #0, pixel, end, parallel
mov.skipinv r29, #0x5CAF0000
mov.skipinv r28, #{BASE}
mov.skipinv r4, #{A}
mov.skipinv r6, #{C}
mov.skipinv r5, #{B}
mov.skipinv r10, #0xA0A1A2A3
mov.skipinv r11, #0xA4A5A6A7
mov.skipinv r12, #0xA8A9AAAB
mov.skipinv r13, #0xACADAEAF
mov.skipinv r14, #0xB0B1B2B3
mov.skipinv r15, #0xB4B5B6B7
mov.skipinv r16, #0xB8B9BABB
mov.skipinv r17, #0xBCBDBEBF
stad [r29,+#16], r4
stad [r29,+#17], r6
idf drc0, bif
wdf drc0
{OP}
wdf drc0
stad [r29,+#0], r10
stad [r29,+#1], r11
stad [r29,+#2], r12
stad [r29,+#3], r13
stad [r29,+#4], r14
stad [r29,+#5], r15
stad [r29,+#6], r16
stad [r29,+#7], r17
idf drc0, bif
wdf drc0
mov.skipinv.end o0, r10
