; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_rate.s -- a triangle's pixel shader (slot pixel) whose phas takes the rate ({RATE}: pixel,
; sample or selective), then the case's OP (e.g. setm #k) and o0 = 0xFF000000 | g25 << 16 |
; each pixel's four samples sit over 2x2 pixels, so per-sample runs show as samples that differ.
phas #0, #0, {RATE}, end, parallel
{OP}
mov.skipinv r1, #8
shl.skipinv r2, g24, r1
or.skipinv r2, r2, g23
mov.skipinv r1, #16
shl.skipinv r3, g25, r1
or.skipinv r2, r2, r3
mov.skipinv r1, #0xFF000000
or.skipinv r2, r2, r1
mov.skipinv.end o0, r2
