; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (phase 11.37, prepared): predicated forms.  r1 = P (A), r2 = a marker source (B),
; r11 = the case's marker (C), r10 preset to a fixed marker; OP sets p0 from r1, runs a gap
; (movs, ldad of the scratch fill and its wdf) and the predicated form; r10 is the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r29, #0x5CAF0000
mov.skipinv r1, #{A}
mov.skipinv r2, #{B}
mov.skipinv r11, #{C}
mov.skipinv r10, #0xA0A1A2A3
{OP}
mov.skipinv.end o0, r10
