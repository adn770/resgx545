; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_rate_sample.s -- pix_rate.s fixed at the sample rate with no OP, a helper for the
; task-word probes (gen_taskrate.py): o0 = 0xFF000000 | g25 << 16 | g24 << 8 | g23, the
; instance's place, so at 4x per-sample runs show as a pixel's samples that differ.
phas #0, #0, sample, end, parallel
nop
mov.skipinv r1, #8
shl.skipinv r2, g24, r1
or.skipinv r2, r2, g23
mov.skipinv r1, #16
shl.skipinv r3, g25, r1
or.skipinv r2, r2, r3
mov.skipinv r1, #0xFF000000
or.skipinv r2, r2, r1
mov.skipinv.end o0, r2
