; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_br.s -- a two-phase pixel shader (slot pixel) asking whether phas's instance mode
; ({OP}: parallel or perinstance) decides how a divergent branch goes: phase 1 (instruction
; instance, p0 (even x) pixels get 4 and the others 7; a quad going where its top-left
; instance goes gives all four 4. TEST is testtaz (p0 on even x) or testtanz (odd x). The host relocates the first phas's next phase.
phas #6, #8, pixel, {OP}
nop
nop
nop
nop
nop.end
mov.skipinv r2, #0
mov.skipinv r1, #1
and.skipinv.{TEST}.chan0 !c0, p0, g25, r1
p0 br #0x00000003
or r2, r2, #1
or r2, r2, #2
or r2, r2, #4
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
