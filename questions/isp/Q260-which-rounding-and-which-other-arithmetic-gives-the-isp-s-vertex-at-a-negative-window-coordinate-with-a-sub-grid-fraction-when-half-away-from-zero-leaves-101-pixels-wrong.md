+++
id = "Q260"
question = "which rounding of a vertex coordinate to 1/256 pixel, and which other step of the ISP's setup, reproduces its coverage when a coordinate is negative with a fraction finer than 1/256 (E683: half up is wrong in 288 pixels of 149 cases, half away from zero in 101 pixels of 67 cases, no variant of eight is exact, also when applied to the vertex as the float32 clip words give it), and does the sign act on the coordinate or on a tile-relative offset"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E683", "E607", "E606", "E680", "E681"]
terms = []
+++
E607 fitted a rounding half up to 1/256 pixel at x >= 0 and E681 shows it holds at positive ties up
to 4096 wide. E683's 240 cases with negative coordinates at 1/4096 refuted it on fit and held-out;
the ties go away from zero (82 of 99 decided), a threshold of 7/16 in place of 8/16 fits best (23
and 78 pixels), and 101 pixels (3e-6 to 2.2e-3 pixel from an edge line) remain with that rounding;
in 10 of the inexact cases no floor/ceil combination reproduces the image. The eight variants were
also run on the vertex as the float32 clip words give it (exact, float32 (c + 1) * half, float32 c *
half + half): none reaches 0 (post hoc, not in the dataset). 25 of the 240 cases have a coordinate
below -25 pixels (minimum -843.2), where E684's far-vertex band cannot be excluded, but the mismatch
rate does not depend on the distance (72 of 124 inexact above -1.6 pixels, 19 of 25 below -25) and
the 101 pixels lie up to 2.2e-3 pixel from an edge line, above E684's 5.6e-4. The simulator refuses
a vertex with a negative coordinate with a sub-grid fraction until this is settled.

To settle it: sweeps of E681's kind with one vertex at a negative coordinate (-0.5, -3.5, -64.5
pixels) in steps of 1/4096 across the tie with the edge's other end fixed, on a pixel row one pixel
from the vertex and then 100 pixels from it (a slanted edge, both axes); the same with the vertex at
+0.5 and +64.5 for the comparison in one run; and cases with exactly one non-tie negative coordinate
to separate the rounding from a setup offset; a positive mirror control (the same construction at x
> W, with the same fractions and edge aim), which was not run, to tell a negative-coordinate effect
from one of the far side.

Status: open.
