; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The E428 probe's fill shader, at the code heap's base (sgxfive-test probe, the fill's default
; place): the colour 0x0000BA5E. The probe's placed program (place_use.s) is started in its place; the
; pixels say which of the two ran.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0x0000BA5E
; run {RUN}
