+++
id = "E417"
claim = "In the triangle's opaque pass a shader that stores o0 unchanged gives the previous job's colour on 390 to 450 of the triangle's 1062 pixels at 64x64 after a job of one constant colour and on 0 to 336 of 2403 at 96x96 and 0 to 183 of 4284 at 128x128, the rest the background, and the counts repeat (426 in four of seven pass-through jobs at 64x64); at 64x64 a pass-through job after a pass-through job keeps the colour, at 96x96 and 128x128 it shows it on 0 to 183 pixels (none in three of six)"
unit = "isp"
method = "probes/isp/o0-start.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: a run of 11 jobs each at 64x64, 96x96 and 128x128, each a fresh process: job A stores o0 = 0xff00ff00, job B o0 = 0xff112233, job P stores o0 = o0, in the order A P P B P A P P B P P, every pixel read (33 jobs)"
tiers = ["HW"]
date = "2026-11-07"
data = ["isp-o0-start"]
terms = ["ISP0.PASS_TYPE"]
+++
**What was seen.** At 64x64 the jobs A and B drew their colour on all 1062 triangle pixels. The
seven P jobs drew, on the triangle's pixels, the previous job's colour on 450 (after A), 426, 390
(after B), 426, 426, 426 and 390 pixels, the other pixels the background 0xff203040. At 64x64 P
after P kept the colour of the A or B before it (the second P after A: 426 pixels of 0xff00ff00);
the three P after P at 96x96 kept it on 0, 167 and 140 pixels and at 128x128 on 0, 183 and 0. At
96x96 (A and B 2403 pixels) the seven P jobs gave 243, 0, 238, 294, 167, 336 and 140 pixels of the
earlier colour and at 128x128 (4284 pixels) 144, 0, 13, 183, 183, 56 and 0. The count is not
constant but repeats (426 four times at 64x64, 183 twice at 128x128).

**What it shows.** o0 at the start of the shader is not defined by the pass: on a part of the
triangle's pixels it holds what the last job's shader wrote to o0, on the others the target's
background; the part is smaller on larger targets. This is E373's leftover output registers seen
from a triangle.

**What it does not show.** Which pixels they are (not mapped); a job of another size before the
pass-through (each probe ran its 11 jobs at one size, after the 64x64 baseline); whether the
translucent pass does the same.
