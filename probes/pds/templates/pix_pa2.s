; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A pixel shader for the iteration probes (--slot pixel=pix_pa2.bin): the colour is primary
; attribute 2 (asm/transfer/use_copy.s).
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, pa2
