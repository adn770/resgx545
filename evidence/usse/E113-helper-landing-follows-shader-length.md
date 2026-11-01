+++
id = "E113"
claim = "How many uncovered helper pixels' o0 lands is largest at 32 nops (71 of the triangle's 102 in all three runs), against 26 to 43 for 0 to 16 nops and 53 to 59 from 64 nops on; quads whose instance 0 (top left) is covered land more often (17 of 18 at least once in nine runs from 32 nops on) than those whose instance 0 is a helper (16 of 24)"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/helper-instances.toml, probe usse-helper-instances-helpers-len (the triangle's pixel shader writes o0 with a plain mov after 0, 2, 4, 8, 16, 32, 64 or 128 nops, pix_helpers_len.s, three runs each, every pixel read back), compared with the 1062 covered pixels of E104's .skipinv run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-helper-instances"]
terms = []
+++

**What runs.** The same triangle as in E111 (42 partly covered quads, 102 uncovered pixels), a plain
write of o0 after n `nop`s, so the write lands on the uncovered pixels of the partly covered quads
(the helper pixels of the probe) as in E104. The 24 cases are the eight lengths three times. The
covered 1062 pixels are green in every case.

**Results.** Uncovered pixels landed (and quads landed), three runs per length:

| nops before the write | pixels landed | quads landed |
|-----------------------|---------------|--------------|
| 0 | 28, 26, 38 | 11, 10, 14 |
| 2 | 26, 39, 35 | 10, 14, 13 |
| 4 | 40, 36, 40 | 15, 13, 15 |
| 8 | 37, 32, 39 | 13, 11, 14 |
| 16 | 43, 38, 43 | 15, 14, 15 |
| 32 | 71, 71, 71 | 28, 27, 27 |
| 64 | 55, 55, 59 | 21, 21, 22 |
| 128 | 55, 53, 55 | 21, 20, 21 |

In all 24 cases a quad that lands shows all of its uncovered pixels (whole quads). The 42
partly covered quads have three shapes: 18 cover only instance 0, 12 the bottom row and 12 the
right column. Over the nine runs from 32 nops on:

| quad covers | quads | land in every run | land in some runs | never |
|-------------|-------|-------------------|-------------------|-------|
| instance 0 only | 18 | 11 | 6 | 1 |
| bottom row (instance 0 uncovered) | 12 | 2 | 6 | 4 |
| right column (instance 0 uncovered) | 12 | 2 | 6 | 4 |

So of 18 quads with a covered instance 0, 17 landed at least once; of the 24 with a helper
instance 0, 16 did. No visibility counter counted.

**What it shows.** Landing is largest at 32 nops (71 in all three runs) and smaller at 64 and 128
nops; from 0 to 16 nops the runs of different lengths overlap (26 to 38 at 0 nops, 26 to 39 at 2,
36 to 40 at 4, 32 to 39 at 8, 38 to 43 at 16) and the means do not rise steadily (38.7 at 4 nops,
36.0 at 8). It favours quads whose instance 0 is covered. The count changes between runs of the
same shader (28, 26, 38 at 0 nops), which suggests a race between the shader's end and whatever
masks the quad's uncovered pixels **[infer]**; no timing was measured.

**Not shown.** What decides a quad; why 32 nops is a peak. Three runs per length.
