; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; The fixed USE program of every PDS probe (sgxfive-test probe --pds --use), the fill's
; shader: the PDS probe, the fill's secondary program, wrote its results to sa0-sa15 with
; douta; store them to scratch dwords 0-15 and mark the pixel.
phas #0, #0, pixel, end, parallel
mov.skipinv r29, #0x5CAF0000
stad [r29,+#0], sa0
stad [r29,+#1], sa1
stad [r29,+#2], sa2
stad [r29,+#3], sa3
stad [r29,+#4], sa4
stad [r29,+#5], sa5
stad [r29,+#6], sa6
stad [r29,+#7], sa7
stad [r29,+#8], sa8
stad [r29,+#9], sa9
stad [r29,+#10], sa10
stad [r29,+#11], sa11
stad [r29,+#12], sa12
stad [r29,+#13], sa13
stad [r29,+#14], sa14
stad [r29,+#15], sa15
idf drc0, bif
wdf drc0
mov.skipinv.end o0, #0x0DA7A000
