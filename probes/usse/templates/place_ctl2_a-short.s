; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; place_ctl2_a-short: placed program of 8 words, no jump
phas #0, #0, pixel, end, parallel
mov.skipinv r10, #0x600D
mov.skipinv r5, #T
mov pclink, r5
nop
nop
mov.skipinv.end o0, #0xFA11
T: mov.skipinv.end o0, r10
