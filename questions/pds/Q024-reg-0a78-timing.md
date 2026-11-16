+++
id = "Q024"
question = "does CR_PDS_REG_0A78 change timing, when two of its values were slower in one timing run?"
unit = "pds"
kind = "hw"
value = "low"
phase = 7
evidence = ["E141", "E045", "E396", "E1114", "E1124", "E1125"]
terms = ["CR_PDS_REG_0A78"]
+++

All 64 values of the register complete a 64x64 triangle with the baseline image (E045), so the
image does not depend on it. Its time was measured at seven values (E141): the mean of the last
five of six 256x256 triangle renders, in microseconds, was 67658 at 0x00, 70977 at 0x01, 67561 at
0x08, 67566 at 0x10, 69038 at 0x20, 67288 at 0x2c (the firmware's value) and 67319 at 0x3f.
Five values lie within 0.5 percent of each other; 0x20 is 2.6 percent and 0x01 5.5 percent above
the 0x2c value. The twelve values of the other register timed the same way (0x0abc) spread 1.2
percent, so these two are above the noise of that series, but this is one run and one sample per
value.

Narrowed in 11.14 (E396): six values (0x00, 0x01, 0x08, 0x20, 0x2c, 0x3f), five runs each in a
shuffled order, give medians within 0.3 percent (67274-67469 us), so E141's slower 0x01 and 0x20
were noise; one 0x01 run had two slow renders. Left narrowed: the other 58 values and a render with
many small triangles were not run.

Narrowed in round 29 (E1114, readings only: its frozen control rule failed on one 0x2c control,
c11, whose job had two slow renders): all 64 values, two shuffled passes each, timed on the
256x256 triangle. 62 values lie within 1 percent of the 0x2c controls on both passes; 0x23 and
0x39 lie outside on one pass each, from one slow render each; no value lies outside on both
passes. [infer] By the median of renders 2-6 (post hoc) every value is within 0.82 percent.
Left narrowed: no frozen verdict yet, and the load with many small triangles was not run (no
timed form in the tools).

Narrowed in round 31 (E1124, a frozen verdict): on the 256x256 triangle, with the reading the
median of renders 2-6 and at most one 0x2c control a stage allowed outside its band (frozen before
the run), no value of 0x00-0x3f lies more than 1 percent from the 0x2c controls on both shuffled
passes (64 of 64 decided; three readings over 1 percent, each on one pass only); E141's 0x01 and
0x20 read +0.34 and -0.22, +0.24 and +0.11 percent. The 256x256 clause is closed. The second load,
500 small triangles in a 64x64 render (t30 `probe --tri --vertices 1500`), could not be read
(E1125): a render takes about 0.72 ms and its references spread 8.3 percent, so the frozen bound
(24.8 percent) passed its 2.5 percent cap; [infer] post hoc every value's medians lie -6.0 to
+11.4 percent of the controls, within that noise.

Open: whether a load of many small triangles, timed to about a percent, shows a difference.

To settle it: one flagged session on the kit's `kreg` word with a many-small-triangles render long
enough to time to a percent (tens of ms, e.g. the 1500 vertices on a larger target, or more
renders a job), chosen by a safe calibration stage frozen to pick the first form whose references
spread under about 0.8 percent, then the 64 values on two passes with 0x2c controls, the reading
and the control rule of E1124.
