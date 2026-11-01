+++
id = "E225"
claim = "Writing 0, 1, 2, 4, 8, 0x10, 0x20 or 0x3f into bits 5:0 of 0x0800 (which holds 0x30 = 48 outside a render) does not change the time the ISP is clocked for a 1024x1024 render whose pixel shader runs 150 dependent fmads on 276192 pixels (28646 to 28776 us over 50 jobs), so a pixel-task maximum of 48 is not what the field holds; that it limits other work is a reading, not tested"
unit = "isp"
method = "the hand script task-limits.sh of probes/pds/task-limits.toml (function 0800_pixel_time) on the laptop, linux fork with the debug option on: a 1024x1024 triangle render, case 0 a pixel shader of 150 dependent fmads then the store, case 1 the store alone, 0x0800 (rd:22) poked before each job; the render's time from CR_CLKGATESTATUS bit 0 (the ISP clock) sampled by regtimeline; 5 jobs per value and case; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["pds-task-limits"]
terms = ["CR_REG_0800", "CR_CLKGATESTATUS"]
+++

**The reading.** 0x0800 holds 0x30 outside a render (E067). Open register descriptions of another
GPU's data-sequencer control speak of a maximum of 48 tasks in the system (no citation record of
this tree covers them, so the match is ours), and bits 5:0 of this register can hold 48. A test
would lower the field and time a render whose pixel shader is long.

**What runs.** The script of E136: 10 settings (no poke, 0x30, 0x1, 0x2, 0x4, 0x8, 0x10, 0x20,
0x3f and 0x0), each run 5 times in case 0 (the long shader) and 5 times in case 1 (the store alone),
100 jobs; the time with the ISP clock on is the sum of the sampled intervals in which
CR_CLKGATESTATUS bit 0 is set.

**Results.** All 100 jobs end with the same image (772384 pixels of 0xff203040 and 276192 of
0x00ff8040). Case 0, 50 jobs: 28646 to 28776 us with the ISP clock on, mean about 28685; per
setting the ranges are within that (28650 to 28688 us with no poke, 28664 to 28776 at 0x1, 28678 to
28762 at 0x3f, 28657 to 28690 at 0x0). Case 1, 50 jobs: 1521 to 1848 us, mean about 1610, the
largest being one job at 0x3f. A job's wall time (3426 to 3757 ms in case 0) is dominated by the
host's setup and readback and has no relation to the value. The long shader takes about 18 times the
time of the store alone at every setting, 0x1 and 0x0 included.

**What it shows.** No value of bits 5:0 tried changes the render's time or image, so these bits do
not cap the number of pixel tasks in flight in this render. The reading of 48 as a task maximum is
therefore not supported for pixel tasks.

**Not shown.** That another kind of work (vertex or state tasks, context switches) is what the
field limits is the reading that remains, and no such job was timed. That pixel tasks decide the
time of the long-shader render is not measured; the ratio to the store alone only shows the shader
dominates. The script does not read 0x0800 back after the poke, so that the register held the value
in the render is taken from the poke. One run of five jobs per value and case (the same data as
E136, which has the same figures).
