+++
id = "E780"
claim = "R1-pixgeo stage g-t5 (9 jobs): with both controls passing (the 0.96-pixel square t5-ctl-sq of S1's e3k-ctl present with 1/w 0x4479ffff, the 0.48-pixel triangle none) the TA wrote no object for any of the six triangles centred on the pixel corner (32, 32), the tool's triangle scaled to a bounding box of 0.30, 0.50, 0.60, 0.75, 0.90 and 0.98 pixels (areas 0.042, 0.117, 0.169, 0.264, 0.380 and 0.451 pixel), nor for the elongated 0.30 x 0.98 triangle (area 0.138), so the ladder had no flip; the frozen verdict reads `ladder monotone (flip at extent none); elongated none: HS-ext consistent (the 0.98 cell is none), HS-area consistent (area 0.138; absent up to 0.451, present from 0.000); the elongated cell does not separate them`, but the frozen row of the 0.98 cell predicted an object for HS-ext (extent at least T, T in (0.48, 0.96]) and the cell wrote none, so HS-ext as frozen is refuted by that cell and the scorer's word consistent compares the elongated cell with the top cell instead of the row"
unit = "ta"
method = "R1-pixgeo stage g-t5 of the question-closing pass, round 2 (decision R2-17; 9 jobs: the controls t5-ctl-sq and t5-ctl-none, the ladder s-e030, s-e050, s-e060, s-e075, s-e090 and s-e098 and the elongated s-elong) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:53 laptop time (08:53 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); the ladder jobs probe --tri pixel --width 64 --height 64 --tri-v X0,Y0,X1,Y1,X2,Y2 --tri-unit 10 --dump-render with p1139-green (the default triangle's three vertices scaled about the corner (32, 32) in 1/1024 pixel, e.g. s-e098 32266,32266,33270,32517,32517,33270 and s-elong 32614,32266,32922,32517,32691,33270), the controls the vertex programs t5-ctl-sq and t5-ctl-none through probe --temps 32 --pixels --tri vtxuse with block word 14 = 0x3a83126f (S1b's e3k-ctl and e3k-i-c1e3: w of 1e-5 under a clamp of 1e-3 for the square, the tiny one for none); a debugfs reset before each job, all 9 of class ok (rc 0); the object decoded through pbdump (none = no object words in the PB dump); frozen predictions from the proposal's hypotheses HS-ext and HS-area (the ladder rows frozen as present for HS-ext at 0.98, monotone for HS-area); scored by the frozen score/score_r1.py g-t5 (out/score-g-t5.txt), re-run on the kept files with the same SUMMARY; the disagreement of the verdict with the frozen row was read in score/score_geo2.py (score_t5: ext_ok compares the elongated cell with the ladder's top cell) and in predictions/g-t5.tsv after the run"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-t5/"]
terms = ["WCLAMP"]
+++
**What ran.** E736 and S1b left a sub-pixel cull: an object for a 0.96-pixel square that covers no
pixel centre (e3k-ctl), none for a 0.48-pixel triangle (e3k-i-c1e3). The proposal's hypotheses were
HS-ext (an object iff the bounding box is at least T, T in (0.48, 0.96]) and HS-area (an object iff
the area is at least some A*), and a ladder of the tool's triangle scaled about a pixel corner (so
that no pixel centre lies inside) with an elongated triangle that would separate them.

**Frozen verdict.** `controls pass; ladder monotone (flip at extent none); elongated none: HS-ext
consistent (the 0.98 cell is none), HS-area consistent (area 0.138; absent up to 0.451, present from
0.000); the elongated cell does not separate them`.

**Disagreement with the frozen rows [data and source].** predictions/g-t5.tsv froze, for the cell
s-e098 (bounding box 0.9805, area 0.4506), `object = present` under HS-ext and `monotone` under
HS-area. The cell wrote none. HS-ext as frozen (T at most 0.96, so a 0.98 box present) is therefore
refuted by that row; the scorer's 'consistent' for it rests on `ext_ok = (elongated state == the
ladder's top state)`, which is true when every cell is none. HS-area's 'consistent' is vacuous in
the same way: with no present cell, an A* above 0.451 fits. The verdict is recorded as printed
above and the rows as frozen here.

**Results [HW].** Controls: t5-ctl-sq an object of 4 vertices at (32.48, 32.48), (31.52, 32.48),
(32.48, 31.52), (31.52, 31.52) (a 0.96-pixel square, area 0.92) with 1/w 0x4479ffff, as S1; t5-ctl-
none none. Ladder (bounding box, area): 0.301 and 0.042, 0.500 and 0.117, 0.600 and 0.169, 0.750 and
0.264, 0.900 and 0.380, 0.980 and 0.451, all none (no object words); the elongated triangle (0.30 x
0.98, area 0.138) none.

**Read after the run [infer; not held out].** The largest absent triangle has a bounding box of 0.98
pixel and an area of 0.45; the smallest present one (the control) has a box of 0.96 and an area of
0.92. So the box is not the criterion (a 0.98 box is absent where a 0.96 box is present), and an
area criterion would put A* between 0.45 and 0.92; but the control reaches the TA through a vertex
program with a clamp and the ladder through the probe's own vertices, two routes, so the shape and
the route are not separated from the size by this stage.

**Not shown.** A ladder of squares or of the control's own route (a vertex program) between box
0.5 and 0.96, which would give the threshold and whether it is a box or an area, and the
threshold's dependence on w and the clamp.
