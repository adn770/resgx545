+++
id = "E431"
claim = "After a reset CR_EVENT_STATUS2 bit 6 (0x40) is set by a fill whose pixel program loops 55 or 56 iterations (eight instructions each) in 3 of 3 runs, 54 in 2 of 3, and never by 53 or fewer (3 of 3 runs each, 16 to 53 iterations tried), and always by 56 to 136 iterations in steps of 8"
unit = "edm"
method = "probes/platform/event-steps.toml and event-fine.toml (event-steps.sh, event-fine.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: sgxfive-test probe of int_loop.s fills (six integer multiply-adds and a counter in an eight-instruction loop) of 16 to 136 iterations in steps of 8 and of 48 to 56 in steps of 1, each after a debugfs reset (which puts the register back to 0x400), regtimeline over 0x0008, 0x0118 and 0x012c, the register read after the job, three runs in three different orders"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["platform-event-steps", "platform-event-fine"]
terms = ["CR_EVENT_STATUS2"]
+++

**Results.** Steps of 8 (48 jobs): 0x0118 reads 0x400 after the job for 16, 24, 32, 40 and 48
iterations and 0x440 for 56 to 136 (3 of 3 runs each, 16 cases). Steps of 1 (27 jobs): 0x400 for
48 to 53 iterations (3 of 3 each), 0x440 for 54 in two of three runs and 0x400 in the other, 0x440
for 55 and 56 (3 of 3). The order of the runs (ascending, descending, interleaved) did not change
the outcome.

**What it shows.** The latch is a threshold in the pixel task's running time (or iteration count)
between 53 and 55 iterations, soft at 54 [infer: time], not a function of the program alone: E357
had it between 16 and 128. 55 iterations of eight instructions is 440 instructions; the time was
not measured here.

**What it does not show.** The condition's meaning beyond the task running or stalled for a while
(E357's reading), and bit 7 (the TA). Q082 is narrowed.

**Correction 2026-11-10:** A reading of this record's own data (platform-event-steps, the steps-of-8 jobs
of its first order), made before the round 2 runs. [data] The job times the probe printed rise with
the loop length: 797 us at 16 iterations, 858 at 24, 972 at 32 and 1917 us at 136 (single runs,
about 9.3 us per iteration between the ends; the same jobs in the second order read 2117 us at 136,
so single times are not tight). The "time was not measured here" above is therefore not quite so:
the probe's job time was, and it does not show the latch at a time: the jobs of 48 and 56
iterations took 1135 and 1308 us, while in E357's loop fills the bit sets about 0.1 ms after the
pixel units start. [infer] Since E357's renders (one to three per case, up to 4096x4096; long, but
not looping) never set bit 6, and
the loop's threshold is in iterations (53 against 55) and not in time since the pixel units started,
the latch watches something counted per instance of the pixel program, with the loop length as the
knob; which quantity (instructions executed by one instance, instances resident, a queue depth) is
not shown. Occupancy (the target's size) is the untried knob.
