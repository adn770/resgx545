+++
id = "E103"
claim = "setm #0 to #15 masks no sample of a 4x multisampled triangle, before an o0 write with or without .skipinv: all 34 cases draw the same 1248 samples; and no pixel of a single-sample triangle written without .skipinv is masked: all seven cases draw the 1062 covered pixels, 22 to 36 more than the triangle covers"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/instance-masking.toml, probes usse-instance-masking-setm-msaa-skipinv and -setm-msaa-plain (the 64x64 triangle at 4x, render command words 1, 10, 13 and 16 set to 0xe0000000, 0xeaa26e26, 0x80000002, 0xeaa26e26), and -setm-tri-plain (single sample), one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-instance-masking"]
terms = []
+++

**What runs.** At 4x each pixel's four samples are stored over 2x2 pixels of the 64x64 image,
unresolved, so a sample mask would show directly. The pixel shader runs `setm #k` and then writes o0
= 0xFF00FF00, with `mov.skipinv.end` in one probe and a plain `mov.end` in the other; k runs from
none through 0 to 15 (17 cases each). The single-sample probe runs the plain `mov.end` after no
`setm` and after `setm #0`, `#1`, `#2`, `#4`, `#8` and `#15`.

**Results.** At 4x all 34 cases (17 with `.skipinv`, 17 without) give one image, the same hash in
both probes: 1248 samples of 0xff00ff00 and 2848 of the background. No `setm` value removes or adds
a sample. In the single-sample probe the covered 1062 pixels are green in every case; the plain
write also lands on uncovered pixels of quads the triangle covers (E104), 22, 27, 36, 28, 33, 28 and
26 of them for no `setm`, `#0`, `#1`, `#2`, `#4`, `#8` and `#15`, whole quads at a time in each case
(9 to 13 quads of the 42 partly covered ones). The same plain write repeated three times gives 20,
18 and 18 in E104, so the spread is of the same size as the repeats' and `setm` does not separate
the cases. Baselines before and after were exact.

**Not shown.** One run. That the count of extra pixels changes from case to case varies from run to
run as in E111 and E113, not an effect of `setm`.
