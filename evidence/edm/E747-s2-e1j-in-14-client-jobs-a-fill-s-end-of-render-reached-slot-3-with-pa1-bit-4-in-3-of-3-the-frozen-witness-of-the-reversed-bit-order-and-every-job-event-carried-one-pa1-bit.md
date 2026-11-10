+++
id = "E747"
claim = "A firmware task of ours that logs every non-tick pass of the four PDS #13 slots (ring_e1, window 1) saw in 14 client jobs (fill x3, copy x3, 64x64 triangle x3, 256x256 triangles -n 3 x3, 1024x768 partial render -n 2 x2) 138 event entries, each with pa0 = 0 and exactly one bit set in pa1 bits 23:0: (slot, bit) (0, 8) 68, (3, 4) 26, (3, 22) 20, (1, 9) 16, (2, 21) 4 and (2, 10) 4; the frozen witness of the bit order, the fill's end of render, arrived in slot 3 with pa1 bit 4 in 3 of 3 fills (the reversed order of E155: pa1 bit = 22 minus the status bit, status bit 18 PIXELBE_END_RENDER, against pa1 bit 18 in slot 0 for the same-position reading of E146), the frozen bit sets of the reversed order explained 132 of the 138 entries and those of the same-position order 88, every entry's slot equals PDS #13's dispatch of its own words (138 of 138, the instrument control) and pa2 is in EVENT_TIMER's format and range on all 138 (held out); bit 19 never appeared (not in the 2 partial renders that overflowed the parameter buffer either) and bit 8 only in slot 0 with pa0 = 0; the arrival order per kind was the same in every replicate (3 of 3, 3 of 3, 3 of 3, 3 of 3, 2 of 2)"
unit = "edm"
method = "S2 stage e1j of the question-closing pass (14 jobs, 5 kinds: fill x3, copy x3, tri 64x64 x3, tri --width 256 --height 256 -n 3 x3, tri --width 1024 --height 768 -n 2 --keep-overflow --keep-going x2 with debugfs render_pb_pages written 0x30, read back, marked in the kernel log and put back to 0x422 after each job), paths relative to edm/closing-s2/ of the dataset, run 1794265145-18601, on the laptop (direct cable), 2026-11-09 23:59, after the e1c gate (E746) was open: one arm of ring_e1 (as E746), window 1 (a plain tick is not logged), the window opened before the client tool (~/sgxfive-test-s1, sha256 d776afbc...714e) ran and closed 20 ms after it returned, the page read twice; kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware; frozen before the run (FROZEN.sha256, PREDICTIONS.sha256): for each kind the pa1 bit sets that E547's sampled status timelines and E548's interrupt matrix give under the reversed order (H1: status bit s appears as pa1 bit 22 - s) and under the same-position order (H2: pa1 bit s), the fill's witness bit (4 against 18), and E146's dispatch rule as the instrument control; scored by the frozen score/score_s2.py e1j; the order per kind, the one-bit rule and the count byte were read after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["edm-closing-s2:out/e1j/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_STATUS", "CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_EVENT_STATUS.TA_FINISHED", "CR_EVENT_KICK"]
+++
**What ran.** Q033 asks which order the status bits have in the word the hardware hands the EDM,
and which events set its bits 8 and 19. E538's stubs could not say (E746). With every pass
logged, each client job leaves its events in arrival order, with the CR_TIMER stamp of each.

**Frozen verdict.** `e1j: Q033 H1 (reversed, E155) on the fill (fill jobs ['H1', 'H1', 'H1']);
explained H1 132/138 H2 88/138; dispatch 138/138; pa2 EVENT_TIMER 138/138`; no ring filled; every
job rc 0 (fills and copies ok, triangles `renders ok`, the two partial jobs `tri: 0 of 2 renders
ok, 2 overflowed` as the recipe wants); the knob proof (render_pb_pages read back 0x30 and put back
0x422, marked each time) is in the kernel log (out/score-e1j.txt). The decision rests on the
fill alone: the fill's one end-of-render event is a different bit under the two readings (4 or 18)
and slot 3 or slot 0; the other kinds' sets overlap and only count as 'explained'.

**Results [HW].** The 138 entries, by (slot, pa1 bit, pa0): (0, 8, 0) 68, (3, 4, 0) 26, (3, 22, 0)
20, (1, 9, 0) 16, (2, 21, 0) 4, (2, 10, 0) 4; pa0 was 0 on every one and no entry carried bit 19.
Arrival order by CR_TIMER, identical in every replicate of a kind:

| kind | order (slot:bit) |
|---|---|
| fill, copy | 0:8, then 3:4 about 0.9 k units later (0.88 to 0.98 k), then 0:8 (+287 k to +403 k) |
| tri 64x64 | 0:8, 1:9 (+1.9 k), 3:4 (+3.5 k), 3:22 (+0.14 k after the 3:4), then 0:8 x5 |
| tri 256x256 -n 3 | (0:8, 1:9, 3:4, 3:22) once per render, three times, then 0:8 x5 |
| partial -n 2 | (0:8, 2:21, 2:10, 3:4, 3:22, 1:9, 3:4, 3:22) per render, twice, then 0:8 x5 |

Times are from the first entry of the job, in CR_TIMER units (25000 to a tick).
Slot 2 appeared only in the partial renders (the overflow path). Every pa2 was in range (bits
31:24 = 0x01, bits 23:0 under 400000). The count byte pa1 bits 31:24 ran 2 to 69 over the stage;
inside each job it rose by one after each (0, 8) entry and after nothing else (124 successive
pairs, no exception), and it carried from the last entry of a job to the first of the next (13
of 13 boundaries); every (0, 8) entry therefore behaves as E746's kick entry.

Six entries lie outside the frozen reversed sets: the copy's (3, 4) (3 jobs) and the 64x64
triangle's (1, 9) (3 jobs), bits whose status bits E547's samples had not listed for those kinds;
under the same-position sets they lie outside too, together with every (3, 4), (3, 22) and (2, 21)
entry.

**Post hoc [infer; read after the run, not held out].** Under the reversed order the names are:
pa1 bit 4 PIXELBE_END_RENDER (status 18), pa1 bit 9 TA_FINISHED (13), pa1 bits 22, 21 and 10
status bits 0, 1 and 12; pa1 bit 8 is the host's kick of the kernel's command buffer (a
GETMISCINFO with no job is that one entry, E746), so a client job logs one (0, 8) entry for each
command of the kernel's buffer that it causes, and the count byte counts them. The six entries
outside the sets are then an end of render in a copy and a TA finish in a small triangle that the
1 to 5 us sampling of E547 did not catch, not a third map. The PDS hands the EDM one status bit at
a time: two bits that rise together reach it as two passes about 140 units (5.6 us) apart (3:4,
then 3:22).

**Not shown.** The status-register side of each entry (no register was read), which status bit
pa1 bit 8 is (it is a kick of the buffer, not a status read), what the bits that E547 saw and that
never appeared here (26, 14, 31) do (the EDM does not see them, or they reach no slot), whether a
bit is a pulse or a level, and the event that sets bit 19 (the out-of-memory case of this partial
render did not).
