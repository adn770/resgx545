+++
id = "Q276"
question = "does a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gate the write `p1 or.skipinv o4` at all (E709: the o4 writes and their 120 pairs are the same for k = 0, 1, 2, 3 and for no guard), and which instances run when it does"
unit = "pds"
kind = "hw"
value = "high"
phase = 11
evidence = ["E709", "E570", "E406", "E742"]
terms = ["PDS_SIZE.BITS17_16"]
+++
Q023 asks which lanes write o4 to o7 in the four-output-room setup. E709 guarded o4 by a test of g25
against k and found tag-5 pixels (25 to 48 in each x or y job) and 17 to 29 pairs, all from
even-even source pixels, for every k, as for the unconditional job. The lane-0-only reading (pairs
only for k = 0) was right in 4 of 10 jobs (two configurations, x and y) and wrong in 6; the any-lane
reading cannot be told from 'the predicate does nothing'. The 5 configurations were not repeated,
so the differences in pair counts between them (17 to 29) are not read.

Open: whether `testtaz.chan0` with a predicate destination `!c0, p1` writes p1 per instance, for the
whole task (channel 0 only) or not at all in this encoding, and whether `p1 or.skipinv` is
predicated on it. A guard that cannot hold was not run.

To settle it: the same shader with k = 7 (g25 never equals it) and k = 3 on a job whose output is
read back, a store of p1 into a register (through a `mov` on the predicate), and the o4 write
guarded by g23 bit 4 (a test of a different register), all five with the setup of E709.

Post hoc 2026-11-09 (S1, E742; read after the run, not held out; the frozen verdict was cannot tell,
the control c-u showing the first unpredicated write in 5 of 497 sources). With k = 7 no source
shows the predicated write, with k = 0 a quarter do, all at even x and even y, and with k = 3 a
quarter, all at odd x and odd y, which reads as the predicate gating the write per pixel with g25
taking the pixel's place in its 2 x 2 quad; with g23 a quarter show it (not the half the frozen
prediction said), concentrated where x mod 8 < 4 and y mod 8 < 4. A frozen rerun is needed.
