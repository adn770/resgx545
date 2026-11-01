; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_pt2.s for a two-instruction OP: the pt phase loads r1
; 0xee00 and r2 0xe001, hands source 34's values to the ISP with pcoeff pa2, pa3, then ends
; with the case's two instructions (OP, the last the feedback); the colour phase writes pa0.
; The host renumbers the first phas's next phase (#6). Run with pds_iter_pt.s.
phas #6, #0, pixel, pt, parallel
mov.skipinv r1, #0x0000EE00
mov.skipinv r2, #0x0000E001
pcoeff pa2, pa3, r1
{OP}
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
