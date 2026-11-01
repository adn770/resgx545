+++
id = "E136"
claim = "Writing 0, 1, 2, 4, 8, 0x10, 0x20, 0x30 or 0x3f into bits 5:0 of register 0x0800 before a 1024x1024 render whose 150-instruction pixel shader runs on 276192 pixels does not change the time the ISP is clocked (28646 to 28776 us in 50 jobs, against 1521 to 1848 us for the store alone) or any pixel"
unit = "pds"
method = "hand-run script probes/pds/templates/task-limits.sh (0800_pixel_time) and probe pds-task-limits-long-pixel of probes/pds/task-limits.toml on the laptop, linux fork with the debug option on: a 1024x1024 triangle render, case 0 a pixel shader of 150 dependent fmads then the store, case 1 the store alone, 0x0800 written through the kernel fork's debugfs kpoke file (the script's spec rd:22) before each job; the render's time taken from CR_CLKGATESTATUS sampled by regtimeline; one run of 5 jobs per value and case"
tiers = ["HW"]
date = "2026-11-01"
data = ["pds-task-limits"]
terms = ["CR_REG_0800", "CR_CLKGATESTATUS"]
+++

**What runs.** The target is 1024x1024 and the triangle covers 276192 of its pixels. Case 0 gives
each pixel a shader of 150 dependent fmads followed by the store, so the shader is expected to
dominate the render's time. Case 1 is the store alone. Before each job the script pokes register
0x0800 (rd:22) with one of nine values: 0x30 (the value it holds outside a render), 0x1, 0x2, 0x4,
0x8, 0x10, 0x20, 0x3f and 0x0, or with nothing for the base case. Each of the ten settings runs five
times per case, 100 jobs. The wall time of a job is mostly the CPU's setup and readback, so the
render's own time is taken from `CR_CLKGATESTATUS` (0x0008), sampled about every 8 us: the sum of
the intervals in which bit 0 (the ISP clock) is on.

**Results.**

- Every one of the 100 jobs ends with the same image: 772384 pixels of 0xff203040 and 276192 of
  0x00ff8040.
- Time with the ISP clocked, case 0 (the long shader), 50 jobs: 28646 to 28776 us, mean about 28685.
  Per setting the ranges are within that: 28650 to 28688 us for the base, 28646 to 28708 for 0x30,
  28664 to 28776 for 0x1, 28678 to 28762 for 0x3f and 28657 to 28690 for 0x0.
- Case 1 (the store alone), 50 jobs: 1521 to 1848 us, mean about 1610. The largest value, 1848 us,
  is one job at 0x3f; no setting has a range apart from the others.
- Wall time of a job: 3426 to 3757 ms in case 0 and 3377 to 3709 ms in case 1, with no relation to
  the value.
- A shader of 150 fmads takes about 18 times the time of the store alone at every setting,
  including 0x1 and 0x0.

So within this run no value of bits 5:0 of 0x0800 changes the render's time or its image. A limit
of one pixel task at a time (value 1) would be expected to lengthen a render whose time the pixel
tasks decide, and it did not; that the pixel tasks decide the time is not measured, the ratio to
the store alone shows only that the shader's time dominates.

**Not shown.** One run of five jobs per value and case. The script does not read 0x0800 back after
the poke, so that the register held the value during the render is taken from the poke only. What
bits 5:0 of 0x0800 do is not shown; only that they do not limit pixel tasks in this render.
