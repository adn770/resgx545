+++
id = "E416"
claim = "ISP word 0 bit 28 hangs a render in CR_ISP_MSAA mode 1 and mode 2 in 8 of 8 jobs whatever 0x0520 holds (0 or 0xeaa26e26), and single-sampled it widens a horizontal-edge right triangle only at k = 6 (45 to 64 pixels, not at k = 0 and 12) with the same counts at 0x0520 = 0 and 0x88; CR_ISP_REG_04DC with bit 1 set hangs the punch-through pass in 24 of 24 jobs, whether the shader only discards, always fails, or uses pcoeff alone, and bit 1 clear completes all of them (12 of 12); the punch-through pass with pcoeff and the source-34 iteration draws the same five times, and without that iteration its kept pixels differ from run to run (4 to 5 outcomes in 5 runs, with and without pcoeff)"
unit = "isp"
method = "probes/isp/bit28-modes.toml (14 probes of one to three cases, 18 jobs) and probes/isp/punch-through-repeat.toml (33 probes: pt2-punch-pcoeff-only, pt2-punch-neither and pt2-punch five times, pt2-punch-discard and pt2-punch-pcoeff-only with rd:21 = 0, 2 and 3 three times, 61 jobs) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: ISP word 0 with bit 28 (blk:1 0x11d00200) under mode 1 and 2 (cmd:13 0x80000001, 0x80000002, sample words cmd:10, cmd:16 0xeaa26e26) with rd:19 at 0 and 0xeaa26e26, twice; single-sampled with rd:19 at 0 and 0x88, twice; the layout probes' right triangle (legs 10, edges at 4 + k/16, k = 0, 6, 12) with bit 28 at rd:19 0 and 0x88"
tiers = ["HW"]
date = "2026-11-07"
data = ["isp-bit28-modes", "isp-punch-through-repeat"]
terms = ["CR_ISP_SAMPLE_POS", "CR_ISP_MULTISAMPLECTL", "ISP0", "FEEDBACK_CTL.ENABLE", "FEEDBACK_CTL.KEEP", "ISP0.PASS_TYPE", "CR_ISP_REG_04DC"]
+++

**Bit 28.** Mode 1 and mode 2 with bit 28, one case a probe: 8 of 8 jobs hung (job hung, context
lost, a reset), with rd:19 at 0 and at 0xeaa26e26 alike (two repeats each). Single-sampled (mode 0)
the same word completes with 1098 triangle pixels (the five copies) at rd:19 = 0 and 0x88, twice
each. On the right triangle with a horizontal edge the triangle's pixels are 55, 64 and 45 for k =
0, 6 and 12 with bit 28 at both values of rd:19; the same triangle without bit 28 (the layout probe
of probes/isp/msaa-layout.toml, mode 0, TE bits clear) has 55, 45 and 45. So single-sampled, bit 28
adds 19 pixels at k = 6 and none at k = 0 and 12, and 0x0520 plays no part.

**Bit 1 of 0x04dc.** With rd:21 = 0 the discarding punch scene (three cases) and the pcoeff-only
scene completed in all three repeats. With rd:21 = 2 and with 3 every one of the 24 jobs hung,
including the case whose alpha test always fails (every copy discarded) and the pcoeff-only scene:
no variant of these shaders avoids the hang.

**The punch pass and pcoeff.** The pass with pcoeff and the source-34 iteration drew the same image
in five of five runs (1062 pixels of one value, 36 of another). With pcoeff alone the five runs gave
four images (995, 90 and 8 pixels of three values; 786, 163, 93; 786, 150, 93; 786, 150, 101) and
with neither pcoeff nor the iteration five different ones (1062 and 36; 816, 128, 109; 816, 121,
118; 825, 115, 109; 816, 118, 109).

**What it shows.** Bit 28 makes a multisampled render hang whatever the sample words, and widens
coverage of a single-sampled edge at some phases. A set bit 1 of 0x04dc hangs the punch-through pass
whatever the shader does, so the hang is not the depth write (the question's reading). The kept
pixels of the pass without the source-34 iteration are not stable between runs with or without
pcoeff, so the variation follows the missing iteration, not pcoeff; whether pcoeff carries the depth
(the settle plan's constant and reversed depths) was not run.

**What it does not show.** Why bit 28 hangs multisampled renders; what the 0x04dc bit does besides
hanging.
