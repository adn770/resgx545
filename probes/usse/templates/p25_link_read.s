; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; the link of a br.savelink to the next instruction in a placed program, as o0
phas #0, #0, pixel, end, parallel
br.savelink #1
mov r10, pclink
mov.skipinv.end o0, r10
