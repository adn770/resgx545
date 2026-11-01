; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A one-phase pixel shader for the PBE probes that read each pixel's place (slot pixel, with
; pds_iter_xy.s in pixpds: pa0 = x + 0.5, pa1 = y + 0.5 as singles); the case's instructions,
; the last of them ending the task.
phas #0, #0, pixel, end, parallel
{OP}
