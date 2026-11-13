+++
id = "Q260"
question = "the tie of a negative window coordinate 1/512 above the 1/256 grid rounds away from zero wherever the aimed pixel is clear of E914's band (E914, E943): which arithmetic decides the pixels within about 2e-3 pixel of an edge line (738 of 738 pixels off half away from zero's image within 6.4e-4 pixel of a long edge in E943, E683's 101 up to 2.3e-3 pixel, on edges under 195 pixels too), given that neither a vertex past the far edge nor the band is a rule on E683 and no fixed-point edge evaluation on half away from zero's vertices gives E683's images better than the exact one (E952)"
unit = "isp"
kind = "hw"
value = "high"
phase = 11
evidence = ["E683", "E607", "E606", "E680", "E681", "E914", "E943", "E952"]
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

Note 2026-11-12 (round 7 offline, post hoc on E683's and E681's kept images; no record, no claim
settled, the question stays open). The tile-relative reading of the line's last clause, each
coordinate rounded half away from zero relative to the origin of the tile being drawn (half up in
tiles whose origin is at or before it, half down after it), is worse than global half away from
zero on E683's 240 S3 cases at every tile size tried (32 x 16, 16 x 16, 16 x 8, 32 x 32, 64 x 64:
73 to 76 cases inexact and 112 to 117 pixels wrong, against 67 and 101) and breaks E681's positive
ties (6 to 14 of 588 cases inexact, 58 to 201 pixels, where half up and half away are exact).
Control that could fail and did not: the script reproduces E683's counts for half up (149 cases,
288 pixels), half away (67, 101) and half down (88, 142). `closing7/rank/q260_tilerel.py` (output
`q260_tilerel.out`) imports the dataset's numpy model; it was re-run from its published copy with
another local venv's interpreter under `python -I -B` (the repository's .venv has no numpy) and
printed byte-identical output. The offline routes are spent: the sweeps above remain the way to
settle it.

Narrowed 2026-11-12 (round 7, R7-geo stage zs, E914). The sweeps of "to settle it" ran (230 jobs,
512 x 256). No frozen rounding is exact held out: HA and SETUP(7) (the c the -0.5 x sweep fits;
the same image as HA here) 125 of 143, HU 121, FAR 119, and HU on the positive mirror 42 of 51.
The model-free step table settles the tie: on the -0.5 (x, y), -3.5 (x, y) and -64.5 x sweeps the
image changes one step after the 1/512 tie (the tie rounds away from zero, every step HA's), on
+0.5, +64.5 and the far side at the tie (half up; FAR refuted at its own two rows), and on -64.5 y
not at all. Read after the run, the rows no rival matches (all of -64.5 y, non-tie case 01) and
the mirror misses (+64.5 y from the tie on) differ from HU only in pixels within 6.4e-4 pixel of
an edge of 258 to 313 pixels, E684's band, so the open part looks like the edge evaluation of long
edges rather than the rounding [infer]. The simulator still refuses a negative coordinate with a
sub-grid fraction: no rounding held out. To settle it: HA frozen with the long-edge sweeps
repeated in x and y at 1, 4, 100 and 300 pixels, so that the band and the rounding separate.

Narrowed 2026-11-13 (round 8, R8-lgeo stage zs2, E943; the question line is reworded, the
question is not retired). It read "the tie of a negative window coordinate 1/512 above the 1/256
grid rounds away from zero on five of six sweeps (E914): what makes the y sweeps aimed 100 pixels
away ... differ from every frozen rounding by pixels within 6.4e-4 pixel of an edge 258 to 313
pixels long, and do half away from zero for negative coordinates and a rule for those long edges
reproduce E683's 101 pixels". At -1/256, -1.25 and -17.75 on both axes the tie rounds away from
zero (HA's step 6 of 8 held out, half up 0 of 8; the other two aim at a pixel within 4e-5 pixel of
a 300 to 600 pixel edge); H-BAND held on 90 of 90 long rows, and read after the run all 738 pixels
off HA's image lie within 6.4e-4 pixel of an edge line of 195 to 904 pixels. The y-axis reading of
E914 is refuted: on 256 x 512 the misses follow the transposed scene (H-GEOM 16 of 24, H-YAXIS 8),
and every sweep with a vertex past the far edge missed (12 of 12; post hoc, 4 more sweeps miss
1 to 3 pixels without one). The simulator refuses a negative sub-grid vertex naming this question.
To settle it: freeze the far-vertex reading and the band and hold them out (sweeps with and without
a vertex past the far edge at matched edge lengths), and find which side a band pixel takes.

Narrowed 2026-11-13 (round 9 offline, decisions S-2 a and R9-8 a, E952; the question line is
reworded, the question is not retired). It read "the tie of a negative window coordinate 1/512 above
the 1/256 grid rounds away from zero wherever the aimed pixel is clear of E914's band (E914, E943):
which arithmetic decides the pixels within 6.4e-4 pixel of a long edge (738 of 738 pixels off half
away from zero's image lie there, E943), and does a vertex past the target's far edge, read after
the run, predict the sweeps that miss". On E683's
240 kept cases, which neither reading used, E943's far-vertex reading fails both ways (61 of 167
cases with a far vertex off half away from zero, 6 of 73 without) and the band does not bound the
misses (up to 2.3e-3 pixel, 20 pixels on edges under 195 pixels): the far-vertex clause is
dropped. OZ, 1613 fixed-point edge-function variants on HA's vertices fitted on E914's and E943's
395 images and frozen by hash, held out on E683: the frozen best 154 and 162 of 240 against HA's
173 and the gate of 235 (post hoc at most 175), so the round's matched-length sweeps (zs3) do not
run. What stays: which arithmetic decides those pixels; candidates outside OZ's forms (the vertex
as the TA stores it, an edge set-up from the clip words in floating point, a tie rule near a long
edge) need an offline fit that beats HA on E683 before any row.
