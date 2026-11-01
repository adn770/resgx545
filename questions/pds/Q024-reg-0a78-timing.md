+++
id = "Q024"
question = "does CR_PDS_REG_0A78 change timing, when two of its values were slower in one timing run?"
unit = "pds"
phase = 7
evidence = ["E141", "E045", "E396"]
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

Open: whether 0x01 and 0x20 are slower again on a second run (a real dependence) or were noise or
a one-off disturbance; what the other 57 values do; whether a load that stresses the PDS more than
a small triangle does shows a larger difference.

To settle it: time all 64 values, ten times each in random order, on the 256x256 triangle, and
once more on a render with many small triangles (more PDS tasks); give the mean and spread per
value and restore 0x2c after each.
