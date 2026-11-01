; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The eight-level mip probes (tex_words.py): the scratch buffer (--scratch-pages 24)
; holds a 128x128 twiddled chain of eight levels from its start, dword i being
; 0xD0000000 | i as the host fills it, so the texel read names its level; read by
; smp2dreplace with T0 {T0} in r20 and the LOD {LOD} (an IEEE single) in r26; the
; result in r10 is the pixel, r10-r17 are stored over the chain's start after it.
phas #0, #0, pixel, end, parallel
mov.skipinv r10, #0xA0A1A2A3
mov.skipinv r11, #0xA4A5A6A7
mov.skipinv r12, #0xA8A9AAAB
mov.skipinv r13, #0xACADAEAF
mov.skipinv r14, #0xB0B1B2B3
mov.skipinv r15, #0xB4B5B6B7
mov.skipinv r16, #0xB8B9BABB
mov.skipinv r17, #0xBCBDBEBF
mov r20, #{T0}
mov r21, #0x0C07F07F
mov r22, #0x5CAF0000
mov r23, #0x00800800
mov r24, #0x3E600000
mov r25, #0x3F280000
mov r26, #{LOD}
smp2dreplace r10, r24, r20, r26, drc0
wdf drc0
mov.skipinv r29, #0x5CAF0000
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
