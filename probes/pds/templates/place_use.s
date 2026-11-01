; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The USE program the E428 probe places high in the code heap and starts in place of the fill
; shader (place_base.s): the colour 0x00000061.
phas #0, #0, pixel, end, parallel
mov.skipinv.end o0, #0x00000061
