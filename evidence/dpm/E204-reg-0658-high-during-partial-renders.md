+++
id = "E204"
claim = "Register 0x0658 reads 1 in jobs that overflow their parameter buffer and never in jobs that do not (40 timelines): one stretch per partial render, 1 to 10 of them as the buffer shrinks at 4096x4096 and one at 1024x768, each stretch 26.8 to 28.9 ms long at 4096x4096 and 1.0 to 1.2 ms at 1024x768; register 0x065c was never seen at 1"
unit = "dpm"
method = "the two sweeps of probes/dpm/parameter-buffer.toml: registers 0x0400-0x07fc sampled by regtimeline for 3 s around the 1024x768 and the 4096x4096 triangle at ten buffer sizes, each twice (40 timelines, 24 of jobs that overflow), on the laptop with the linux fork and the debug option on; read with E199's table of the firmware's writes"
tiers = ["HW", "RE"]
date = "2026-11-01"
data = ["dpm-parameter-buffer", "firmware-edm-dataflow"]
terms = ["CR_DPM_PARTIAL_RENDER", "CR_DPM_SPM_SWITCH", "partial render"]
+++

**What runs.** `regtimeline` reads the 256 registers of the range in a tight loop (about 37 000
samples in 3 s, one every 80 microseconds) and prints a line at every change of any of them, with
the time from the start of sampling in nanoseconds; the job starts 0.2 s into it. The stretches
where register 0x0658 is not zero are taken from those lines. Nothing is written to the registers.
E199 gives the firmware's writes of the two registers: 0x0658 is set to 1 in the partial-render
routine and cleared in the resume and in every 3D kick, 0x065c is set and cleared inside the same
two routines.

**Results.** The 16 timelines (8 sizes, 2 repeats) of 4096x4096 that overflow and the 8 (4 sizes, 2
repeats) of 1024x768 that overflow (E202) show 0x0658 going to 1 and back to 0 in separate
stretches; the 16 non-overflowing ones show it at 0 throughout. Stretches by buffer size:

| pages | 1024x768 | 4096x4096 |
|---|---|---|
| 0x422 to 0x40 (1024x768), 0x422 and 0x200 (4096x4096) | 0 | 0 |
| 0x100 | 0 | 1 (28.2 and 28.9 ms) |
| 0x80 | 0 | 2 (27.2 to 27.6 ms) |
| 0x62 | 0 | 3 (26.8 to 27.6 ms) |
| 0x40 | 0 | 5 (27.5 to 28.3 ms) |
| 0x30 | 1 (1.19, 1.22 ms) | 7 (27.0 to 27.8 ms) |
| 0x28 | 1 (1.02, 1.19 ms) | 8 (27.1 to 28.2 ms) |
| 0x24 | 1 (1.11, 1.07 ms) | 9 (26.8 to 27.7 ms) |
| 0x23 | 1 (1.11, 1.01 ms) | 10 (27.1 to 27.7 ms) |

The count of stretches is the same in the two repeats of every size; the first starts 97 to 103 ms
after the job starts at 1024x768 and 1.44 to 1.45 s after at 4096x4096, where the stretches follow
one another with gaps of 1 to 2 ms. Register 0x065c was never non-zero in any of the 40 timelines.
The lengths are good to about one sample (0.08 ms).

**What it shows.** Register 0x0658 is 1 while a partial render of the overflowing scene runs, so
each stretch is a partial render, consistent with the firmware raising it at the start of the
partial-render routine and lowering it at the resume (E199). The count grows as the buffer shrinks.
Register 0x065c, which the firmware sets and clears in the same routines, stays below the sampling
interval.

**Not shown.** What 0x0658 does inside the DPM: it is observed, not written. The host's own writes
of it are not looked at. That the number of stretches equals the number of partial renders is a
reading of the firmware: the RT data set's partial-render count was not read in these runs. The
scene is a single triangle, and the time of each stretch includes the render work between the two
writes.
