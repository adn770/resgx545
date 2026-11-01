; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (48 temporaries) for a dword the host writes while the job runs (--late
; 128:64=0x12345678): r46 the address of scratch dword 64 (its fill 0xD0000040 in r42), r47
; that of dword 128 (the ready dword). WARM loads dword 64 or not, READY stores r3 (1) to
; dword 128 for the host to see, then RELOAD (into r22) runs N times; r41 counts the reloads
; that still read the fill. The pixel is that count, plus 0x10000000 when the last reload
; read the host's value.
phas #0, #0, pixel, end, parallel
mov.skipinv r46, #0x5CAF0100
mov.skipinv r47, #0x5CAF0200
mov.skipinv r42, #0xD0000040
mov.skipinv r43, #0x12345678
mov.skipinv r39, #0x10000000
mov.skipinv r3, #1
mov.skipinv r41, #0
mov.skipinv r45, #0
mov.skipinv r44, #0x00000010
mov.skipinv r22, #0
{WARM}
{READY}
mov.skipinv r40, #{N}
{RELOAD}
xor.testtaz.chan0 !c0, p2, r22, r42
p2 iadd32.testtaz.chan0 r41, p3, r3, r41
isub16.testtanz.chan0 r40, p0, r40, #1
p0 br -#{BACK}
xor.testtaz.chan0 !c0, p2, r22, r43
p2 iadd32.testtaz.chan0 r41, p3, r41, r39
mov.skipinv.end o0, r41
