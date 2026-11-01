; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The pixel shader of the PBE word probes (--slot pixel): one colour, E030's 0x00ff8040.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0x00FF8040
