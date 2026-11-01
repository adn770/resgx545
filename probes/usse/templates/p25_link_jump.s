; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; a lapc to the link + 8 computed at run time: o0 = the link on landing, 0xFA11 on falling through
phas #0, #0, pixel, end, parallel
br.savelink #1
mov r10, pclink
mov r6, #8
ima32.u r5, r10, #1, r6
mov pclink, r5
nop
lapc
mov.skipinv.end o0, #0xFA11
nop
mov.skipinv.end o0, r10
