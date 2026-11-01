; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (repeats of loads and stores, phase 11.24): r1 = results base (scratch dword 0),
; r2-r33 = 0xA5000000 | n (the sources), r40 = the store pointer (dword 64), r41 = the load
; pointer (dword 1024, whose dword d holds 0xD0000000 | d), r42 = 0xB1B1B1B1 (a marker whose
; position shows where the pointer ended), then PRE, OP and POST (which stores the marker 32
; dwords past the pointer under test), the fences, and r42 as the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r1, #0x5CAF0000
mov.skipinv r2, #0xA5000002
mov.skipinv r3, #0xA5000003
mov.skipinv r4, #0xA5000004
mov.skipinv r5, #0xA5000005
mov.skipinv r6, #0xA5000006
mov.skipinv r7, #0xA5000007
mov.skipinv r8, #0xA5000008
mov.skipinv r9, #0xA5000009
mov.skipinv r10, #0xA500000A
mov.skipinv r11, #0xA500000B
mov.skipinv r12, #0xA500000C
mov.skipinv r13, #0xA500000D
mov.skipinv r14, #0xA500000E
mov.skipinv r15, #0xA500000F
mov.skipinv r16, #0xA5000010
mov.skipinv r17, #0xA5000011
mov.skipinv r18, #0xA5000012
mov.skipinv r19, #0xA5000013
mov.skipinv r20, #0xA5000014
mov.skipinv r21, #0xA5000015
mov.skipinv r22, #0xA5000016
mov.skipinv r23, #0xA5000017
mov.skipinv r24, #0xA5000018
mov.skipinv r25, #0xA5000019
mov.skipinv r26, #0xA500001A
mov.skipinv r27, #0xA500001B
mov.skipinv r28, #0xA500001C
mov.skipinv r29, #0xA500001D
mov.skipinv r30, #0xA500001E
mov.skipinv r31, #0xA500001F
mov.skipinv r32, #0xA5000020
mov.skipinv r33, #0xA5000021
mov.skipinv r40, #0x5CAF0100
mov.skipinv r41, #0x5CAF1000
mov.skipinv r42, #0xB1B1B1B1
{PRE}
{OP}
{POST}
idf drc0, bif
wdf drc0
mov.skipinv.end o0, r42
