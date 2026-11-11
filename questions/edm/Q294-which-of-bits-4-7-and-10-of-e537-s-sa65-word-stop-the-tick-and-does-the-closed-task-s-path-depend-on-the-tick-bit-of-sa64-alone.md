+++
id = "Q294"
question = "which of bits 4, 7 and 10 of the sa65 word of E537 (0xb009c5dc, without bit 8) stop the tick through the closed task (E814: that word stopped it without E537's marks; E812: the count byte 0xb0 and bits 2, 3, 6, 14 to 16, 19 and 23 alone keep it), and does the closed task's path depend on the tick bit of sa64 alone (E812: sa64 = pa0 & ~2 on 50 passes keeps the tick, leaves pclink at 6 and does not advance dword 12; no sa64 word other than 0, 2 and pa0 & ~2 has run)"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E537", "E792", "E812", "E814"]
terms = ["Event Data Master (EDM)"]
+++
Split on 2026-11-11 from Q152 (round 4, decision R4-3, events decision 4), whose line is now the
phase end of a tick pass. What is known: E537's writer left sa65 = 0xb009c5dc and the tick stopped.
E814 removed bit 8 from the word and the tick still stopped, with neither of E537's marks (read
offset write + 1, dword 14 0xad002600), and kept bit 8 alone (0x02000100), which stopped it with
both, so the CCB reader, the handler and a once-only stop are refuted (H-CCB, H-HANDLER, H-ONCE).
E812 left single words in sa65 without bit 8 (the count byte 0xb0, bits 2, 3, 6, 14, 15, 16, 19 and
23) and the tick was kept in 13 of 13 jobs, so what is left of E537's word is bits 4, 7 and 10 (and
their combinations with the others), none tried alone. For the second clause, E812's 50 passes with
the tick bit of sa64 clear kept the tick, left pclink at 6 and did not advance HostCtl dword 12
(2 of 2; E792: pclink 6 follows a non-tick word in sa64), the only sa64 words run are 0, 2 and
pa0 & ~2.

Not planned, and why: a row per bit (reset and arm each, up to three stops, after a reading of what
each handler does with no job in flight, E154's method) measures the closed code's reaction to an
event that did not happen, which the simulator refuses anyway and our own firmware never sends. It
stays low and open for a time when the closed handlers are read for another reason. To settle it:
single-bit and pair rows of sa65 over bits 4, 7 and 10 with a reset and an arm before each, and
sa64 words with the tick bit clear and other bits set, one stop at most a stage.
