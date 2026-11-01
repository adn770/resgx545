; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_pt3.s for a two-instruction OP: the pt phase loads r1
; 0xee00 and r2 0xe001 and ends with the case's two instructions (OP, the last a visibility
; test); the colour phase writes pa0. The host renumbers the first phas's next phase (#5).
phas #5, #0, pixel, pt, parallel
mov.skipinv r1, #0x0000EE00
mov.skipinv r2, #0x0000E001
{OP}
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
