; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The triangle's vertex shader for the clipping probes: x and y scaled by {S} and w = {A} x + {B}
; from the vertex's own x (-0.75, 0.75, -0.375 at the three vertices), z kept. With A = -2 and
; B = 1 the second vertex has w -0.5 (behind the eye) and the triangle crosses w = 0; with S
; large it reaches far outside the viewport (the guard band). Temporaries r1-r3.
        phas #14, #0, pixel, vcull, parallel           ; the second phase at instruction 14
        nop.nosched
        and.skipinv.testtanz.chan0 !r0, p0, #0x00000000, #0
        p0 ldad.skipinv.fetch4 pa0, [pa0,+#0], drc0
        wdf drc0
        mov.skipinv.repeat4 o0, pa0                     ; o0-o3 = x, y, z, w
        mov.skipinv r1, #{S}
        mov.skipinv r3, #0x00000000
        fmad.skipinv o0, pa0, r1, r3                    ; x * S
        fmad.skipinv o1, pa1, r1, r3                    ; y * S
        mov.skipinv r1, #{A}
        mov.skipinv r2, #{B}
        fmad.skipinv o3, pa0, r1, r2                    ; w = A x + B
        emitvcbvtx.end.twopart #0, #0
        phas #0, #0, pixel, end, parallel
        emitmtevtx.end.twopart.freep #0, #0, #0
