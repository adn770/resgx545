; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A pixel shader for the fetch-size probes (--slot pixel=pix_pa8.bin): the colour is primary
; attribute 8.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, pa8
