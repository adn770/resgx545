; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template for shared-memory updates from a fill's pixel instances: r29 the scratch
; buffer (patched), r3 = 1, the update under test OP (it leaves the value it stored in r2),
; and that value as the pixel, so the pixels show what each instance saw.
phas #0, #0, pixel, end, parallel
mov.skipinv r29, #0x5CAF0000
mov.skipinv r3, #1
{OP}
mov.skipinv.end o0, r2
