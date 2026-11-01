; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A USE program for PDS probes whose result may differ per pixel (sgxfive-test probe
; --pds --use --pixels): the sa0 the PDS program wrote, as the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, sa0
