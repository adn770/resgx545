+++
id = "E174"
claim = "The library's render contexts, sized for their target by its own rule, draw the first triangle exactly on 16 target sizes from 64x64 to 4096x4096 (two renders of each, 0 wrong pixels in every one), and a context sized for 256x256 draws a 64x64 target exactly; that the same buffers serve every smaller target is shown for that one pair"
unit = "ta"
method = "the existing runs of sgxfive-test tri on the laptop, linux fork with the debug option on: the 13 sizes of probes/render/target-sizes.toml, the client-jobs run (128x96 and a 256x256 context drawing 64x64), and the baseline cases (full parameter buffer, 0x422 pages) of the two sweeps of probes/dpm/parameter-buffer.toml at 1024x768 and 4096x4096; the firmware's use of the sizes was not re-read"
tiers = ["HW"]
date = "2026-11-01"
data = ["render-target-sizes", "render-client-jobs", "dpm-parameter-buffer"]
terms = []
+++

**What runs.** `sgxfive-test tri` creates a render context "for targets up to" the size asked
for ("render context for targets up to WxH") and draws the triangle; the library derives the TE
words and the render target data sizes from the size (the rule is the library's and is not
restated here). Three groups of runs:

- the target-sizes script: 13 sizes (64x64, 64x128, 64x144, 64x160, 64x192, 64x256, 128x64,
  128x128, 128x144, 128x256, 256x64, 256x128, 256x256), two renders each;
- the client-jobs run: 128x96 twice, and a context for 256x256 targets that draws the 64x64
  triangle twice;
- the 1024x768 and 4096x4096 triangles of the parameter-buffer sweeps, at the full parameter
  buffer of 0x422 pages (case `pb=0x422:baseline` and its repeat `#1`).

**Results.**

- Target-sizes: all 26 renders report 0 wrong pixels inside the triangle, outside it and at its
  edges, `outside: 0 dwords`, `guard 0`. The kernel log of the run holds no fault line (one
  line, the campaign marker). Examples: 64x256 draws 4296 triangle and 12088 background pixels;
  256x256 draws 17208 and 48328.
- Client-jobs: 128x96 draws 3252 triangle and 9036 background pixels in both renders; the 256x256
  context draws the 64x64 target at 1062 and 3034, as a context sized for 64x64 does.
- Parameter-buffer sweeps: 1024x768 draws 207456 triangle and 578976 background pixels (hash
  0xc9e301d225fe2325, diff 0 of 786432) and 4096x4096 draws 4422528 and 12354688 (hash
  0x08197f1b8b083325, diff 0 of 16777216), each in both cases, with 0 wrong inside, outside and
  at the edges. A 4096x4096 render takes about 18.3 s, a 1024x768 one about 0.88 s.

That is 16 distinct sizes (the 13, 128x96, 1024x768 and 4096x4096), two exact renders of each, and
one context-size pair (256x256 context, 64x64 target).

**Not shown.** The sizes tried in a row on one context (a context that renders targets of
changing sizes) and the sizes between 256x256 and 1024x768 other than 1024x768 are not run. The
rule's formulas are not tested against alternatives: a different set of TE words that also
draws these sizes is not excluded. The claim that buffers sized for a largest target serve every
smaller one rests on the single 256x256 context drawing 64x64. The firmware's reads of the tail
size and the region-array size were not re-read. The visibility counters stayed at 0 in the
sweeps (0 of 20 counted in each).
