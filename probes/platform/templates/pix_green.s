; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A plain pixel shader writing green (slot pixel): the triangle probes of the HWPerf jobs that differ
; in the number of triangles.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0xFF00FF00
; run {RUN}
