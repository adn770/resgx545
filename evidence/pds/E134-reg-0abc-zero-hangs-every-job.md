+++
id = "E134"
claim = "With register 0x0abc written to 0 (it holds 0xe) before the job, a fill, a geometry-only render and a whole render each hang and the context is lost, and each time the register is restored to 0xe a fill passes again; twelve values of 0x0abc from 0x02 to 0x3e, all with bits 4:1 nonzero, leave the time of a 256x256 render within 1.2 percent"
unit = "pds"
method = "hand-run script probes/pds/templates/task-limits.sh of probes/pds/task-limits.toml (functions 0abc_per_data_master and kick_time; the register written through the kernel fork's debugfs kreg file) on the laptop, linux fork with the debug option on: a 64x32 fill, a two-render triangle run with the geometry-only option and a one-render triangle run, each once with 0x0abc at 0x0, then 0xe restored and a fill run as the check; a 256x256 triangle time for 0x0abc at twelve values"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-task-limits"]
terms = ["CR_PDS_REG_0ABC", "CR_PDS_REG_0ABC.BITS4_1"]
+++

**What runs.** The script writes `0x0abc=0x0` through debugfs, reads it back, and runs one kind
of job: a fill (a transfer), then the triangle tool with `-n 2 --geometry 1 --keep-going`
(geometry only, the tile accelerator alone) and then `tri -n 1` (a whole render, tile
accelerator and 3D). After each job it writes `0x0abc=0xe` and runs a fill as a check. A hang
resets the GPU, which runs the init script again. A second part runs a 256x256 triangle (six
renders, the average of the last five) with `0x0abc` at 0x02, 0x04, 0x06, 0x08, 0x0a, 0x0c, 0x0e,
0x10, 0x14, 0x18, 0x1e and 0x3e.

**Results.**

- The register reads back 0 each time, and the fill, the geometry-only run and the whole render all
  fail: "job hung, context lost (Connection timed out)", with the whole target at the sentinel
  0xdeadbeef, the value it is filled with before the job (2048 of 2048 pixels for the fill, 4096 of
  4096 for the two triangle runs, the first at (0, 0)); the triangle tool reports "FAILED after 0
  renders" in both.
- After each of the three, with the register back at 0xe, the check fill passes ("job: ok, 0 of
  2048 pixels differ").
- The twelve values give 67297 to 68131 us for the 256x256 render, all ok; 0xe, the value the
  init script writes, gives 67297 us and 0x14 gives 68131 us.

**Not shown.** Only the value 0 was written here, which cannot tell bits 4:1 from bits 5 and 0. E045
gives the values for the 64x64 triangle: 0, 1, 0x20 and 0x21 hang it, so it is bits 4:1, not bit 0
or 5, that matter there; for the fill and the geometry-only run this table has no other value. That
the field is a count that every PDS task needs, shared by the vertex, pixel and transfer programs,
is a reading and not shown: the cases show that a job of each of these three kinds fails and no
more. One run of each job.
