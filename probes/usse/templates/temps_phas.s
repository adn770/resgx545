; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; Probe template (the temporaries a phase asks for, phase 11.24): a two-phase fill whose first
; phase (the temporaries the run gives it, --temps) does nothing and whose first phas asks for
; T temporaries for phase 1; phase 1 writes HI with a marker, reads it back and stores it. As
; in the phase probes, phas #2 is the local index of phase 1.
phas #2, #{T}, pixel, none, parallel
nop.end
mov.skipinv r1, #0x5CAF0000
mov.skipinv r{HI}, #{MARK}
mov.skipinv r2, r{HI}
stad [r1,+#0], r2
idf drc0, bif
wdf drc0
mov.skipinv o0, r2
phas.end #0, #0, pixel, end, parallel
