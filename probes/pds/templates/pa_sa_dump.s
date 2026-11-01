; SPDX-License-Identifier: MIT
; SPDX-FileCopyrightText: 2026 Josep Torra
; A USE task for the PDS probes (slot pixel): stores pa0-pa15 to scratch dwords 0-15 and
; sa0-sa31 to dwords 16-47, then marks the pixel. For a PDS write whose bank is not known
; (douta from a primary program, Q020): both banks read back by the task it starts.
phas #0, #0, pixel, end, parallel
mov.skipinv r29, #0x5CAF0000
stad [r29,+#0], pa0
stad [r29,+#1], pa1
stad [r29,+#2], pa2
stad [r29,+#3], pa3
stad [r29,+#4], pa4
stad [r29,+#5], pa5
stad [r29,+#6], pa6
stad [r29,+#7], pa7
stad [r29,+#8], pa8
stad [r29,+#9], pa9
stad [r29,+#10], pa10
stad [r29,+#11], pa11
stad [r29,+#12], pa12
stad [r29,+#13], pa13
stad [r29,+#14], pa14
stad [r29,+#15], pa15
stad [r29,+#16], sa0
stad [r29,+#17], sa1
stad [r29,+#18], sa2
stad [r29,+#19], sa3
stad [r29,+#20], sa4
stad [r29,+#21], sa5
stad [r29,+#22], sa6
stad [r29,+#23], sa7
stad [r29,+#24], sa8
stad [r29,+#25], sa9
stad [r29,+#26], sa10
stad [r29,+#27], sa11
stad [r29,+#28], sa12
stad [r29,+#29], sa13
stad [r29,+#30], sa14
stad [r29,+#31], sa15
stad [r29,+#32], sa16
stad [r29,+#33], sa17
stad [r29,+#34], sa18
stad [r29,+#35], sa19
stad [r29,+#36], sa20
stad [r29,+#37], sa21
stad [r29,+#38], sa22
stad [r29,+#39], sa23
stad [r29,+#40], sa24
stad [r29,+#41], sa25
stad [r29,+#42], sa26
stad [r29,+#43], sa27
stad [r29,+#44], sa28
stad [r29,+#45], sa29
stad [r29,+#46], sa30
stad [r29,+#47], sa31
idf drc0, bif
wdf drc0
mov.skipinv.end o0, #0x0DA7A000
