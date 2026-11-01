; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; use_ptoff.s -- the PTOFF task of a 3D render.
;
; pds_pixevent.s starts it for the PTOFF pixel event (ir1 bit 3). A transfer never
; sees that event and points the PTOFF case at its end-of-tile task; a 3D render
; gives it a task of its own that only signals ptoff and ends ([infer], from the
; instruction's name).

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        ptoff.end
