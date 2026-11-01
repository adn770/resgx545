; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (a global register as a store's source, per pixel): r1 = 0x5CAF0000 + 4 x
; (the instance's place in the fill: g18 x 512 + g24 x 32 + g23, below 16384); the store of SRC there, then
; the load of it back into r10 as the pixel, so that each pixel shows what its own store read.
phas #0, #0, pixel, end, parallel
shl r1, g18, #9
shl r2, g24, #5
or r1, r1, r2
or r1, r1, g23
and r1, r1, #0x00003FFF
shl r1, r1, #2
mov.skipinv r2, #0x5CAF0000
or r1, r1, r2
stad [r1,+#0], {SRC}
idf drc0, bif
wdf drc0
ldad r10, [r1,+#0], drc0
wdf drc0
mov.skipinv.end o0, r10
