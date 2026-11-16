+++
id = "Q024"
question = "does CR_PDS_REG_0A78 change the render time of a sub-millisecond load of many small triangles (64x64), when no value moves a 256x256 triangle or 500 triangles at 1024x768 by 1 percent (E1124, E1129)?"
unit = "pds"
kind = "hw"
value = "low"
phase = 7
evidence = ["E141", "E045", "E396", "E1114", "E1124", "E1125", "E1128", "E1129"]
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

Narrowed in round 32 (E1128, E1129, frozen verdicts; the user's decision of 2026-11-16: the load
of E1129 answers its clause, Q024 narrows). Two loads are answered: no value of 0x00-0x3f moves
the render time by 1 percent on two shuffled passes, on the 256x256 triangle (E1124) and on 500
triangles (1500 vertices) at 1024x768, ten renders a job, about 22 ms a render (E1129: 64 of 64
decided, the farthest 0x1d at 0.48 percent; E141's 0x01 and 0x20 read -0.11 and -0.05, +0.39 and
-0.17 percent). [infer] At 1024x768 each of the 500 triangles covers about a quarter of the
target, so that load is many large overlapping triangles.

Open: whether a sub-millisecond load of many small triangles (the same 500 triangles at 64x64,
about 0.73 ms a render) shows a difference under 1 percent. It cannot be timed to 1 percent
today: a safe calibration (E1128) found the eight job medians spread 4.42, 3.28 and 3.50 percent
(interquartile range) at 10, 20 and 40 renders a job, after E1125's 8.27 percent at six, so more
renders a job do not shrink the spread, which lies between jobs [infer]; the frozen bound (three
times that spread) would be about 10 percent.

To settle it: a way to time a short render to a percent first (a timing of the 64x64 load over
many more jobs, or more small triangles in one render), checked by the same safe calibration
(references spread at most 0.8 percent) before any flagged row, then the 64 values on two passes
with 0x2c controls and E1124's reading and control rule.
