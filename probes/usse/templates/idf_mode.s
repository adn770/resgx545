; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (data fences): r1 = 0x5CAF0000 + 4 x (the instance's place in the fill: g18
; x 512 + g24 x 32 + g23, kept below 16384), the store of A there, idf with mode MODE and its wdf, the load of
; the same dword back into r10 (with LD's cache mode), and r10 as the pixel.
phas #0, #0, pixel, end, parallel
shl r1, g18, #9
shl r2, g24, #5
or r1, r1, r2
or r1, r1, g23
and r1, r1, #0x00003FFF
shl r1, r1, #2
mov.skipinv r2, #0x5CAF0000
or r1, r1, r2
mov.skipinv r3, #{A}
stad [r1,+#0], r3
idf drc0, {MODE}
wdf drc0
ldad{LD} r10, [r1,+#0], drc0
wdf drc0
mov.skipinv.end o0, r10
