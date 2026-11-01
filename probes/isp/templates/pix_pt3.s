; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_pt2.s without the pcoeff (an ablation): the pt phase loads
; r1 0xee00 and r2 0xe001 and ends with the case's visibility test (OP, one instruction); the
; colour phase writes pa0. The host renumbers the first phas's next phase (#4).
phas #4, #0, pixel, pt, parallel
mov.skipinv r1, #0x0000EE00
mov.skipinv r2, #0x0000E001
{OP}
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
