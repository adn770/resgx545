; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; use_sec.s -- the USE secondary program of a transfer (template USE_SEC, id 1).
;
; The PDS secondary program (pds_sec.s) kicks this once; a transfer has no
; per-tile secondary work ([infer]), so it only ends (doc/specs/fw_format.md §9.2).

        phas #0, #0, pixel, end, parallel       ; the phase marker, as in use_fill.s
        nop.end                                 ; nothing to do: end the program
