; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_helpers_len.s -- a triangle's pixel shader (slot pixel) whose only write is a plain mov
; of o0 after the case's padding (PAD, nops), to measure how many uncovered helper pixels'
phas #0, #0, pixel, end, parallel
{PAD}
mov.end o0, #0xFF00FF00
