+++
id = "Q276"
question = "does a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gate the write `p1 or.skipinv o4` at all (E709: the o4 writes and their 120 pairs are the same for k = 0, 1, 2, 3 and for no guard), and which instances run when it does"
unit = "pds"
kind = "hw"
value = "high"
phase = 11
evidence = ["E709", "E570", "E406", "E742", "E759", "E772", "E808"]
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

Post hoc 2026-11-10 (S1b, E759; repeat only, no held-out row). The order control c-u passed the
frozen criterion (tag-2 fraction at least 0.98) in 3 of 3 runs (0.990, 0.992 and 0.996), the first
write surviving at 5, 4 and 2 sources, (16,27) and (17,27) in all three. S1's post hoc readings
repeated in their numbers: g25 == 7 no tag 2 (0 of 486 landings), g25 == 0 a quarter, all at (even,
even) sources (0.253), g25 == 3 a quarter, all at (odd, odd) sources (0.248), g23 0.237; the frozen
HQ (g25 = the lane in the 2 x 2 quad) is consistent in 3 rows, as a repeat. A frozen test with a row
held out against that reading has not run.

Note 2026-11-10 (R1-pixgeo, E772; the frozen verdict is cannot tell, the question stays open). The
frozen test with held-out rows ran (41 jobs) and scored nothing: its global control c-e709 (E709's
configuration unchanged) gave 10 tag-5 pairs against the frozen 17 to 29, which voids the stage by
its own rule, although the order controls (0.990, 0.994) and the premise of the direct reads (1.000)
passed. Read after the run, so not a result [infer over the stage's data]: g25 is a lane id of the
2 x 2 quad (the direct read of g25 equals (x & 1) | (y & 1) << 1 in 1062 of 1062 pixels; k = 1 wrote
only at (odd x, even y), k = 2 only at (even, odd), k = 5 and 7 never, a replicate the same), g23
carries x mod 32 (the direct read, 1062 of 1062; the masks gave x bits 0, 3, 4 and nothing for bit 5
and the y bit), and the o4 write is tag 5 and never tag 5' at k = 0, 3, 7 and unpredicated, that is,
not gated. That answers the first half of the question as "not gated" and the second as "the lane
whose id equals k writes o1" on post hoc readings only; the stage's tag-5 pair counts ran from 10 to
42 over its 18 configurations, so E709's 17 to 29 was too narrow a control. Open: a frozen rerun
with the same rows and a control range from the stage's own counts.

Narrowed 2026-11-10 (R3-pixel, E808; not retired). The frozen rerun with controls scoped to their
group held E772's post hoc readings, frozen as a model, in all 29 rows it scored: g25 is the
instance's lane in its 2x2 quad, g23 = x mod 32 and g24 = y mod 16 (held out, at three triangles),
and a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gates the o1 write per instance (the
lane whose id equals k writes). The o4 clause is not settled: every o4 word was tag 5 in both write
orders, also where 5' was the later write, so the swapped-order control failed and its three rows
are cannot tell, and tag 5 alone in the original order (k = 0, 3 and 7) cannot tell a predicate that
is ignored from a write that lands whatever the order (E772's 'not gated' does not follow). Open:
whether the predicate gates `p1 or.skipinv o4`, and which of two o4 writes lands, and why.
