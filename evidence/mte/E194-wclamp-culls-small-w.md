+++
id = "E194"
claim = "The triangle's size goes as 1/w (261 pixels at w 2, 3212 at w 0.5, the whole target from w 1e-3 to 1e-5) and below w 1e-5 it shrinks away (395 pixels at 2e-6, 100 at 1e-6, 16 at 5e-7, 1 at 1e-7, none at 0 or below); the state block's WCLAMP word (blk:14) holds 1e-5 in the job and, set to 1e-3, removes the triangle at w 1e-5 and below, set to 1e-7 or 0 keeps it whole down to 5e-7; the TA command's two 1e-6 floats change none of it"
unit = "mte"
method = "the probe mte-clipping-w-scan of probes/mte/clipping.toml (vtx_w.s, w the same for all three vertices, 12 values), and the control runs of its hand script clipping.sh (function wclamp_scan: the five smallest-w cases with blk:14 at four values and ta:152, ta:153 at 1e-8, 1e-4 and 0), on the laptop with the linux fork and the debug option on, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["mte-clipping"]
terms = ["WCLAMP", "PRESENCE.WCLAMP", "CR_MTE_RHW_MIN", "CR_MTE_RHW_CLAMP", "cmd_ta.mte_rhw_min", "cmd_ta.mte_rhw_clamp"]
+++

**What runs.** The vertex program writes the same w for the three vertices. Twelve values of w run
on the 64x64 target, and the pixels of the triangle's colour are counted. The control runs (E063
gives the full table) repeat the five smallest w with the state block's w clamp word (blk:14) at its
job value (0x3727c5ac, 1e-5), 1e-7, 1e-3 and 0, and with the TA command's floats ta:152 and ta:153
(0x0240 and 0x0244) at 1e-8, 1e-4 and 0.

**Results.** Triangle pixels by w:

| w | 2 | 1 | 0.5 | 1e-3 | 1e-5 | 2e-6 | 1e-6 | 5e-7 | 1e-7 | 0, -1, -1e-7 |
|---|---|---|---|---|---|---|---|---|---|---|
| pixels | 261 | 1062 | 3212 | 4096 | 4096 | 395 | 100 | 16 | 1 | 0 |

The size goes with 1/w from w 2 to w 0.5 and the target is full from w 1e-3 to 1e-5. Below 1e-5 the
triangle shrinks fast and is gone at 0 and for negative w. With blk:14 at 1e-3 the case at w 1e-3
stays whole and the four smaller show background only; with blk:14 at 1e-7 or 0 all five cases (down
to 5e-7) fill the target; the floats at the three values leave all five at their job images (395,
100 and 16 pixels for the three smallest).

**Not shown.** The table has no w between 2e-6 and 1e-5 or between 1e-5 and 1e-3, so the narrowing
below 1e-5 is not followed to its start, and that the clamp word is the only thing that sets it is
read from four values of the word. What the two floats do is not visible in the image (E063 finds
no scene where they act). E197 shows what they do to the stored 1/w: ta:152 is a minimum below
which the TA stores ta:153 in its place. The 1/w of these small-w vertices (1000 and more) is far
above the three values tried here, so that rule would replace none of them, which fits the
unchanged images **[infer]**. One run.

**Correction 2026-11-09:** The pixel counts above are unchanged; what they do not show is that the
triangle is removed. E736 dumped the TA's object for the same case (w = 1e-5 at every vertex, blk:14
= 1e-3, a 64 x 64 target) and found one: 4 vertices, a square 0.96 pixel wide centred on (32, 32),
which covers no pixel centre, so the image shows background only, as here; every 1/w word of it is
0x4479ffff, the reciprocal of the clamp. Read with E736's jobs at a clamp equal to, one ulp below
and one ulp above w = 1e-3 (only the last stores the clamp's reciprocal), the clamp replaces a
smaller w by its own value ([infer], from one case of each), and "removes the triangle at w 1e-5 and
below" is true of the image and not of the object. The claim line is left as it was measured.
