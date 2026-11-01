; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; An end-of-tile program for the double-emit probes (--tri eot): instructions 1-4 are the four
; movs the host patches with PBE words 0-3 (r0-r3); then the case's emits (EMITS), the last
; ending the task.
phas #0, #0, pixel, end, parallel
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
mov.skipinv r0, #0x00000000
{EMITS}
