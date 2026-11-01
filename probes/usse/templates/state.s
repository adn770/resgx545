; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (state kept between jobs, phase 11.24): BODY is the whole program between the
; phas and the pixel, OUT the register that is the pixel. A writer case sets state and ends
; with its own colour; the reader case that follows it reads the state first of all.
phas #0, #0, pixel, end, parallel
{BODY}
mov.skipinv.end o0, {OUT}
