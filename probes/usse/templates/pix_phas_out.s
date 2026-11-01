; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_out.s -- a two-phase pixel shader (slot pixel) asking whether phas's instance mode
; ({OP}: parallel or perinstance) decides which instances .skipinv skips: phase 1
; (instruction 6) writes o0 with {W} (mov.skipinv, which skips uncovered instances, or a plain
; mov) only; pixels beyond the triangle's 1062 are helper instances that wrote. The host
; relocates the first phas's next phase.
phas #6, #8, pixel, {OP}
nop
nop
nop
nop
nop.end
{W} o0, #0xFF00FF00
phas.end #0, #0, pixel, end, parallel
