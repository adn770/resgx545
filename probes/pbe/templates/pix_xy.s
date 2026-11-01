; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A pixel shader that names its pixel (--slot pixel, with pds_iter_xy.s): pa0 and pa1 hold
; x + 0.5 and y + 0.5 as singles, whose bits 31:16 differ for every x and y below 256; o0 =
; (pa0 & 0xffff0000) | (pa1 >> 16), so a stored word names the pixel it came from.
phas #0, #0, pixel, end, parallel
and.skipinv r0, pa0, #0xFFFF0000
shr.skipinv r1, pa1, #16
or.skipinv r2, r0, r1
mov.skipinv.end o0, r2
