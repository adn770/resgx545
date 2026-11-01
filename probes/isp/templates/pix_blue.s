; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_blue.s -- a plain opaque pixel shader writing blue: the second object of the stencil
; read-back scenes (gen_ptread.py), so its pixels tell where the first object wrote stencil.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0xFF0000FF
