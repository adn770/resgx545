; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (hazards): r1-r8 hold the inputs A-H, r10 0xA0A1A2A3; the writer WR,
; then GAP (nops or other instructions), then READ (which reads the writer's result into r11);
; r10 and r11 stored to scratch dwords 0-1 and r11 as the pixel, so instances that disagree
; show as a mixed pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #{A}
mov.skipinv r2, #{B}
mov.skipinv r3, #{C}
mov.skipinv r4, #{D}
mov.skipinv r5, #{E}
mov.skipinv r6, #{F}
mov.skipinv r7, #{G}
mov.skipinv r8, #{H}
mov.skipinv r10, #0xA0A1A2A3
mov.skipinv r11, #0xA4A5A6A7
{WR}
{GAP}
{READ}
mov.skipinv r29, #0x5CAF0000
stad [r29,+#0], r10
stad [r29,+#1], r11
idf drc0, bif
wdf drc0
mov.skipinv.end o0, r11
