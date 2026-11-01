+++
id = "E140"
claim = "With CR_PDS_REG_0ABC bits 4:1 at 0 a fill, a geometry-only render and a whole render each hang (the job times out and the context is lost), and a render of 256x256 triangles takes 67297 to 68131 us at twelve values of the bits, 1 to 8, 10, 12 and 15; we read the field as one count of PDS task slots shared by every data master; this reading is an inference"
unit = "pds"
method = "inference from the hand-run script probes/pds/templates/task-limits.sh (0abc_per_data_master and kick_time) on the laptop, linux fork with the debug option on: register 0x0abc written to 0 through kreg before a fill, then 'tri -n 2 --geometry 1 --keep-going', then 'tri -n 1', restored to 0xe and a fill run after each; and a 256x256 triangle render, six renders, the mean of the last five, with 0x0abc at 0x02 to 0x3e; one run; the reading is ours"
tiers = ["infer", "HW"]
date = "2026-11-01"
data = ["pds-task-limits"]
terms = ["CR_PDS_REG_0ABC", "CR_PDS_REG_0ABC.BITS4_1"]
+++

**What runs.** The firmware leaves 0x0abc at 0xe (bits 4:1 = 7). The script writes 0 to it and runs
three jobs, one after the other, each with the register at 0 for the whole job: a fill (a transfer,
which uses no geometry), a geometry-only render (two kicks, no 3D part) and a whole render. After
each it restores 0xe and runs a fill to check the target.

**Results.**

- All three jobs fail with "job hung, context lost (Connection timed out)": the fill leaves all
  2048 pixels at the sentinel 0xdeadbeef, and the two renders leave all 4096.
- After each restore to 0xe, the fill completes with 0 of 2048 pixels wrong.
- E045 finds the same hang for the triangle at every value of the register whose bits 4:1 are all
  zero (0, 1, 0x20, 0x21), and the other 60 values complete.
- The render time at 0x0abc = 0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c, 0x0e, 0x10, 0x14, 0x18, 0x1e and
  0x3e (bits 4:1 at 1 to 8, 10, 12, 15 and 15) is 67297 to 68131 us (mean of five renders each, all
  ending ok); 0x02 (bits 4:1 = 1) gives 67759 us and the unwritten 0xe gives 67297 us, and the
  largest value, 68131 us, is at 0x14.

**Reading.** The three kinds of job use different parts of the hardware and all hang at the same
value, so the field is not specific to one of them. It is therefore read as a number of PDS task
slots that every kind of job needs, 0 leaving none. This is an inference: a hang at 0 shows only
that every kind of job needs the field to be nonzero.

**Not shown.** That the field counts slots. That the renders of the time series are bound by PDS
tasks is not measured, so equal times at 1 and at 7 do not test a limit; a load bound by tasks,
timed at 1 against 7, would. One run, one sample per value, and the spread of 67297 to 68131 us is
not separated into noise and any dependence on the value. Whether the geometry-only render and the
whole render hang for the same reason is not shown. A hang recovers the GPU, which runs the init
script again.
