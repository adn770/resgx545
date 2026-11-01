; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (repeats with every pointer register valid, phase 11.24 follow-up): r1 = results
; base (scratch dword 0), r2-r33 = 0xA5000000 | n (the sources), r40-r55 = the store pointers
; (r40+i = dword 2048 + 64 i of the scratch, a line of 16 dwords apart), r56-r71 = the load
; pointers (r56+i = dword 1024 + 64 i, whose dword d holds 0xD0000000 | d), r80 = 0xB1B1B1B1 (a
; marker stored 32 dwords past a pointer's end), then PRE, OP and POST, the fences, r80 as pixel.
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
mov.skipinv r40, #0x5CAF2000
mov.skipinv r41, #0x5CAF2100
mov.skipinv r42, #0x5CAF2200
mov.skipinv r43, #0x5CAF2300
mov.skipinv r44, #0x5CAF2400
mov.skipinv r45, #0x5CAF2500
mov.skipinv r46, #0x5CAF2600
mov.skipinv r47, #0x5CAF2700
mov.skipinv r48, #0x5CAF2800
mov.skipinv r49, #0x5CAF2900
mov.skipinv r50, #0x5CAF2A00
mov.skipinv r51, #0x5CAF2B00
mov.skipinv r52, #0x5CAF2C00
mov.skipinv r53, #0x5CAF2D00
mov.skipinv r54, #0x5CAF2E00
mov.skipinv r55, #0x5CAF2F00
mov.skipinv r56, #0x5CAF1000
mov.skipinv r57, #0x5CAF1100
mov.skipinv r58, #0x5CAF1200
mov.skipinv r59, #0x5CAF1300
mov.skipinv r60, #0x5CAF1400
mov.skipinv r61, #0x5CAF1500
mov.skipinv r62, #0x5CAF1600
mov.skipinv r63, #0x5CAF1700
mov.skipinv r64, #0x5CAF1800
mov.skipinv r65, #0x5CAF1900
mov.skipinv r66, #0x5CAF1A00
mov.skipinv r67, #0x5CAF1B00
mov.skipinv r68, #0x5CAF1C00
mov.skipinv r69, #0x5CAF1D00
mov.skipinv r70, #0x5CAF1E00
mov.skipinv r71, #0x5CAF1F00
mov.skipinv r80, #0xB1B1B1B1
{PRE}
{OP}
{POST}
idf drc0, bif
wdf drc0
mov.skipinv.end o0, r80
