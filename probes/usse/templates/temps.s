; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (temporaries, phase 11.24): r1 = results base, then SET (marker writes), GET
; (stores of the registers read back to dwords 0..), the fences, and OUT as the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x5CAF0000
{SET}
{GET}
idf drc0, bif
wdf drc0
mov.skipinv.end o0, {OUT}
