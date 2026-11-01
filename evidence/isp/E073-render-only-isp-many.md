+++
id = "E073"
claim = "With 42 overlapping triangles per tile, opaque and with depth less, 0x0418, 0x04dc, 0x04e8, 0x0520 and 0x0800 at the 18 values tried leave the covered-pixel count at 1275 of 4096 in every job; the check compares counts, not pixel positions"
unit = "isp"
method = "the hand script render-only-registers.sh of probes/isp/render-only-registers.toml (function many_triangles) with the probe programs staged: probes isp-render-only-registers-many-opaque and -many-less, 126 vertices, kernel pokes of render-details words, two runs, on the laptop with the linux fork and the debug option on"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-render-only-registers"]
terms = [
    "CR_ISP_LINE_SAMPLE_POS", "CR_ISP_REG_04DC", "CR_ISP_REG_04E8", "CR_ISP_SAMPLE_POS",
    "CR_REG_0800",
]
+++

**What runs.** 42 copies of the triangle, each 1/16 pixel further, draw the 64x64 target with
the pixel program writing 0x0a: once opaque and once with ISP0 depth less at z 0 (the first copy
wins every pixel). Each run runs both probes unpoked and then with a poke of 0x0800 at 0, 1,
2, 4, 8, 0x10, 0x20, 0x3f, 0x130 and 0xffff30, of 0x04e8 at 0, 1 and 0x101, of 0x04dc at 1, 2 and
4, of 0x0418 at 0 and of 0x0520 at 0xffffffff. The script prints each probe's summary of the
colours in the target and the job's wall time, and the poke that remains in the kernel's poke
file after the job.

**Results.** Both runs, 76 jobs: every job summarises as 1275 pixels at 0x0000000a and 2821
at the background 0xff203040, the unpoked jobs too. The poke file was empty after every job,
so each poke was taken by the render. The job time stays at 250 to 281 ms in all of them. The
value 2 and the other values of 0x04dc that hung the punch-through scene (E068) do not hang
these scenes.

**What it does not show.** The summary counts colours and does not say where they are, so a
change that moved the same number of pixels would not show; the pixel rows are in the table's
own run (unpoked) only. The values are those listed, not every bit. One run of each run.
