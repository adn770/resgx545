; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (data fences, phase 11.24): FIRST is the first instruction after phas (a
; fence with nothing outstanding), r1 = results base (scratch dwords 0-127), r2 = a sentinel
; that is the pixel, SETUP presets the bases and markers, OP issues the loads and the waits,
; POST stores the registers under test to dwords 0.., END closes the fences (or does not).
; Loads read scratch dwords 1024 and up (dword d holds 0xD0000000 | d), 16 dwords apart.
phas #0, #0, pixel, end, parallel
{FIRST}
mov.skipinv r1, #0x5CAF0000
mov.skipinv r2, #0xC0DE0001
{SETUP}
{OP}
{POST}
{END}
mov.skipinv.end o0, r2
