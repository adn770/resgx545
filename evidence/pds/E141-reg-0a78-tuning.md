+++
id = "E141"
claim = "CR_PDS_REG_0A78 (6 bits, 0x2c as the firmware leaves it) changes no image at any of its 64 values (E045); the render time of 256x256 triangles at seven of its values is 67288 to 67658 us at five of them, and 69038 and 70977 us at 0x20 and 0x01; we read it as a PDS tuning value with no effect on the image, and its effect on time is not settled; this reading is an inference"
unit = "pds"
method = "inference from E045 (all 64 values of the register against a triangle job) and from the hand-run script probes/pds/templates/task-limits.sh (kick_time) on the laptop, linux fork with the debug option on: a 256x256 triangle render, six renders, the mean of the last five, with 0x0a78 written through kreg to 0x00, 0x01, 0x08, 0x10, 0x20, 0x2c and 0x3f and restored to 0x2c; one run; the reading is ours"
tiers = ["infer", "HW"]
date = "2026-11-01"
data = ["pds-task-limits", "platform-untouched-registers"]
terms = ["CR_PDS_REG_0A78"]
+++

**What runs.** The register is written between renders; each value is timed as the mean of the last
five of six 256x256 triangle renders, each of which ends ok.

**Results.**

| 0x0a78 | mean render time (us) |
|---|---|
| 0x00 | 67658 |
| 0x01 | 70977 |
| 0x08 | 67561 |
| 0x10 | 67566 |
| 0x20 | 69038 |
| 0x2c (the firmware's value) | 67288 |
| 0x3f | 67319 |

- Five values lie within 67288 to 67658 us, a spread of 0.5 percent.
- 0x20 is 2.6 percent and 0x01 is 5.5 percent above the 0x2c value.
- In the series of 0x0abc values of the same script and render (E140) the twelve means lie within
  67297 to 68131 us, a spread of 1.2 percent. The 0x20 and 0x01 values of this series are above the
  low end by more than that spread.
- E045 finds all 64 values of 0x0a78 complete a 64x64 triangle with the baseline image.

**Reading.** A register whose 64 values all leave the image alone, and which the firmware sets to
0x2c at start, is read as a tuning value of the PDS. The reading rests on the image result alone.

**Not shown.** That the register has no effect on time: one value is 5.5 percent slower in one run
and the other 2.6 percent, and a second run would tell whether they repeat or are noise. Only seven
of the 64 values were timed, one sample each. Nothing here separates the register's effect on a
load that stresses the PDS more than a small triangle does.
