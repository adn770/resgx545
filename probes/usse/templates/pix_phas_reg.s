; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; pix_phas_reg.s -- a triangle's pixel shader (slot pixel) trying phas's register form at the
; start of phase 1 (a task's program must start with a phas: without one the job hangs).
; Phase 0 (an immediate phas to instruction 8, renumbered by the host) calls the next
; instruction, so pclink holds instruction 2's absolute index; r5 = that + 9, instruction 11's
; (phase 2); r8 = 3, the same as an offset from instruction 8; r7 = CTRL, the immediate form's
; high fields (temps / 4 in 7:0, wait 10:8, rate 12:11, mode 13). Phase 1 runs PHAS, writes o0
; red and ends; phase 2 writes it blue. Blue pixels: the register form started phase 2. CALL
; and LINK are the call and the pclink move; T1 ends phase 1: nop.end when PHAS announces a
; phase 2, the last phase's phas.end when it does not (a phase never closed hangs the job).
phas #8, #8, pixel, none, parallel
{CALL}
{LINK}
mov.skipinv r6, #9
iadd32.testtaz.chan0 r5, p3, r6, r5
mov.skipinv r7, #{CTRL}
mov.skipinv r8, #3
nop.end
{PHAS}
mov.skipinv o0, #0xFFFF0000
{T1}
mov.skipinv o0, #0xFF0000FF
phas.end #0, #0, pixel, end, parallel
