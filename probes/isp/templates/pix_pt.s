; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A punch-through pixel shader for the triangle probes (slot pixel): the pt phase
; ends with the case's visibility test (an atst8 with its feedback mode), then the phase that
; writes the colour, pa0 (the copy's z with pds_tex_z.s). The host renumbers the first phas's
; next phase (#2) from the pixel code base.
phas #2, #0, pixel, pt, parallel
{OP}
mov.skipinv o0, pa0
phas.end #0, #0, pixel, end, parallel
