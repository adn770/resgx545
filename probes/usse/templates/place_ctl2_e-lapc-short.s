; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; place_ctl2_e-lapc-short: placed program of 12 words, lapc
phas #0, #0, pixel, end, parallel
mov.skipinv r10, #0x600D
mov.skipinv r5, #T
mov pclink, r5
nop
lapc
mov.skipinv.end o0, #0xFA11
mov.skipinv r10, #4103
mov.skipinv r10, #4104
mov.skipinv r10, #4105
mov.skipinv r10, #4106
T: mov.skipinv.end o0, r10
