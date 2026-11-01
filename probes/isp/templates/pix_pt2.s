; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A punch-through pixel shader for the triangle probes (slot pixel, with pds_iter_pt.s): the
; pt phase loads 0xe001 into r2 and 0xee00 into r1, hands
; source 34's iterated values to the ISP with pcoeff pa2, pa3, then ends with the case's
; visibility test (OP, one instruction); the colour phase writes pa0. The host renumbers the
; first phas's next phase (#5) from the pixel code base.
phas #5, #0, pixel, pt, parallel
mov.skipinv r1, #0x0000EE00
mov.skipinv r2, #0x0000E001
pcoeff pa2, pa3, r1
{OP}
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
