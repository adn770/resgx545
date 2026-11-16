+++
id = "Q024"
question = "does CR_PDS_REG_0A78 change timing, when two of its values were slower in one timing run?"
unit = "pds"
kind = "hw"
value = "low"
phase = 7
evidence = ["E141", "E045", "E396", "E1114"]
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

Open: a frozen verdict on the 256x256 load (E1114 gives readings: E141's slower 0x01 read
+0.29 and -0.25 percent, 0x20 -0.60 and +0.10); whether a load that stresses the PDS more
than one triangle, many small triangles, shows a difference.

To settle it: a tool change that times a render of many small triangles (a job time on `probe
--tri --vertices N`, or a triangle count for `tri`), then one flagged session on the kit's
`kreg` word with a reading frozen robust to a single slow render (the median of renders 2-6),
the 64 values on both loads with 0x2c controls, restoring 0x2c after each.
