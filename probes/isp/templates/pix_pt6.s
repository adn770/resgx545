; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_pt2.s with pcoeff's third source from the case: the pt
; phase loads r2 0xe001 (the feedback's control word) and the case's value into r1, runs
; pcoeff pa2, pa3, r1 and ends with atst8 ... fb; the colour phase writes pa0. OP is one mov
; into r1. The host renumbers the first phas's next phase (#5). Run with pds_iter_pt.s.
phas #5, #0, pixel, pt, parallel
mov.skipinv r2, #0x0000E001
{OP}
pcoeff pa2, pa3, r1
atst8.end r3, !p0, pa0, r2, r2, fb
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
