+++
id = "E063"
claim = "The two TA command floats at 0x0240 (ta:152) and 0x0244 (ta:153) act on no clipping scene: in 11 scenes (a vertex at w 0.1, 0, -0.05 and -0.5, all three at w 2, -1, 1.25, and 8x, 64x and 1024x the triangle) each of 8 values of each float gives the scene's baseline image, 176 images equal to their baselines; the state block's w clamp word (blk:14) does change the w-scan scenes under the same tool"
unit = "mte"
method = "the hand script clipping.sh of probes/mte/clipping.toml (functions mte_floats_under_clipping and wclamp_scan) with the table's probe programs staged on the laptop: the 11 scenes of probe mte-clipping-wclip with ta:152 and ta:153 poked through the kernel's poke file to 0, 0.01, 0.1, 0.5, 1.0, -1.0, 1000.0 and the largest single, and the five smallest-w cases of mte-clipping-w-scan with blk:14 and the two floats at chosen values, on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["mte-clipping"]
terms = ["CR_MTE_RHW_MIN", "CR_MTE_RHW_CLAMP", "cmd_ta.mte_rhw_min", "cmd_ta.mte_rhw_clamp"]
+++

**What runs.** The vertex program of the wclip probe scales x and y by a factor S and sets w from
the vertex's own x, so one vertex goes to w 0.1, 0, -0.05 or -0.5, or all three to a given w, or
the triangle becomes 8, 64 or 1024 times its size. Each of the 11 scenes ran once unpoked and
then with each of ta:152 and ta:153 at the eight values: 17 jobs a scene, 187 in all, every poke
taken (the poke file was empty after each job) and every image hashed.

**Results.** In every scene all 17 hashes are equal: the baseline. The baselines are the pixel
counts of a crossing vertex, 1062 triangle pixels at w 1, 1156 for the perspective scene, 1216
(w 0.1), 1258 (w 0), 1273 (w -0.05), 1394 (w -0.5), 1610 for all three at w 2, -1, 1.25, and the
whole target in triangle colour for 8x, 64x, 1024x and 8x with a vertex at w -0.5. Neither float
changes a pixel of any of them.

As a control, the w-scan probe (all three vertices at one w) ran its five smallest cases (w 1e-3,
1e-5, 2e-6, 1e-6, 5e-7) with the state block's w clamp word (blk:14) at the default, 1e-7, 1e-3
and 0, and with the floats at 1e-8, 1e-4 and 0:

| setting | w 1e-3 | w 1e-5 | w 2e-6 | w 1e-6 | w 5e-7 |
|---|---|---|---|---|---|
| default, and ta:152, ta:153 at 1e-8, 1e-4, 0 | all triangle | all triangle | 395 | 100 | 16 |
| blk:14 = 1e-7 or 0 | all triangle | all triangle | all triangle | all triangle | all triangle |
| blk:14 = 1e-3 | all triangle | all background | all background | all background | all background |

(395, 100 and 16 are triangle pixels.) The floats leave all five images at their default hash;
the clamp word changes three or four of them, so the tool does reach a w clamp and the floats are
not it.

**What it does not show.** The two floats might act on a scene this set does not contain (a
vertex behind the eye with clip planes on, for example, or w near the guard band edge). Eight
values each of two floats were tried one at a time, not together except at 0. One run.
