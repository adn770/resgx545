+++
id = "E193"
claim = "With the viewport's z offset at 0.75 and a vertex program that sets z to the clip x, the 64x64 triangle draws 1026 of its 1062 pixels, those whose clip x is below 0.5 (the last at 0.484375), so the depth is the z offset plus 0.5 times z against the background depth of 1.0, and vp5 (blk:11) is the viewport's z scale"
unit = "mte"
method = "the probe isp-depth-test-slope of probes/isp/depth-test.toml (vtx_zx.s, blk:1 = 0x400200 depth less written, blk:10 = 0x3f400000, vtx_coords 2, the pixel program writing the clip x it receives), 64x64 target, on the laptop with the linux fork and the debug option on, one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-depth-test"]
terms = ["VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE"]
+++

**What runs.** The vertex program writes the vertex's clip x as its z. The state block holds the
viewport z offset (`blk:10`, vp4, 0.5 in the job) at 0.75 and the z scale (`blk:11`, vp5) at its
default 0.5; the depth test is less with depth written. The pixel program returns the clip x
interpolated at the pixel, so a pixel that lost the depth test keeps the background colour and the
others hold their own clip x. The triangle covers 1062 pixels (E060).

**Results.** 1026 pixels carry a clip x and 3070 are background. The drawn pixels lie in columns 8
to 47; their clip x runs from -0.734375 to 0.484375. No pixel with a clip x of 0.5 or more is drawn.

**Reading [infer].** If the depth is vp4 + vp5 z and the background depth is 1.0, a pixel passes
where 0.75 + 0.5 x is below 1.0, that is for x below 0.5, which is the edge seen. The data fit that
and do not fix the two constants separately: a different scale with a different background depth
could give the same edge. The state-block sweep of E061 leaves vp4 and vp5 without effect on the
flat triangle (depth 0.5), as this reading says.

**Not shown.** That depth outside [0, 1] is not clipped is not measured here: no case moves the
triangle's depth past 1.0 or below 0, so the table cannot say whether such pixels draw. Only one
slope and one offset were run. One run.
