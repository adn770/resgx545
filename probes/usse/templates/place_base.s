; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The fill shader at the code heap's base (the placed program is started in its place):
; the colour 0x0000BA5E, as probes/pds/templates/place_base.s of the E428 probe.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0x0000BA5E
; run {RUN}
