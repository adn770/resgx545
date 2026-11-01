; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pclink preset 0x77, p0 br.savelink #1 with p0 = 1, then the link read as o0
phas #0, #0, pixel, end, parallel
mov.skipinv r5, #0x77
mov.skipinv r6, #1
mov pclink, r5
and.testtanz.chan0 !c0, p0, r6, r6
p0 br.savelink #1
mov r10, pclink
mov.skipinv.end o0, r10
