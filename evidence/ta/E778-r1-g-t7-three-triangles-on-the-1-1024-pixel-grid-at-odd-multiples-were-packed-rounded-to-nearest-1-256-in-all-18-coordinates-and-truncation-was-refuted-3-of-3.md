+++
id = "E778"
claim = "R1-pixgeo stage g-t7 (4 jobs): with the control e3f-ctl (coordinates on the 1/256 grid, E651's packing) passing, the window coordinates of three held-out triangles given on a 1/1024 pixel grid at odd multiples (a quarter or three quarters of a 1/256 step from the 1/256 grid, no ties) were packed in the object's 24-bit fields as the nearest multiple of 1/256 in all 18 coordinates (18 x and y of t7-a, t7-b and t7-c, the frozen words of HF-round equal to the stored words 3 of 3 triangles) and truncation (HF-trunc) was refuted in all three (3 of 3); the frozen verdict: controls pass; held out consistent HF-round (3), refuted HF-trunc (3 of 3)"
unit = "ta"
method = "R1-pixgeo stage g-t7 of the question-closing pass, round 2 (decision R2-15; 4 jobs: e3f-ctl the control, t7-a, t7-b and t7-c held out) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:49 laptop time (08:49 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width 64 --height 64 --tri-v X0,Y0,X1,Y1,X2,Y2 --tri-unit 10 --dump-render with p1139-green (unit 10 = 1/1024 pixel; t7-a 8239,8341,57367,20727,20573,57373; t7-b 8309,8207,57535,20533,20559,57559; t7-c 8359,8263,57469,20519,20717,57447; the control with unit 8, 2048,2048,14336,5120,5120,14336), a debugfs reset before each job, all 4 of class ok (rc 0); the object decoded through pbdump and its packed 24-bit coordinate fields compared with the frozen integer (v + 4096) x 256 rounded (HF-round) or truncated (HF-trunc) per coordinate, six numbers a triangle; frozen predictions from S1's post hoc reading of E736's 1/1024 cells (a fit) and the proposal; scored by the frozen score/score_r1.py g-t7 (out/score-g-t7.txt), re-run on the kept files with the same SUMMARY"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-t7/"]
terms = ["VIEWPORT.X_OFFSET"]
+++
**What ran.** S1's cells on the 1/1024 grid (E736) were read post hoc as packed rounded to
1/256. The stage gave three triangles whose six coordinates each are odd multiples of 1/1024: one
a quarter of a 1/256 step above a multiple of 1/256 (residue 1 modulo 4 in units of 1/1024)
truncates and rounds alike, one three quarters of a step above (residue 3) truncates down where
rounding goes up. The frozen words were written for both rules before the run.

**Frozen verdict.** `controls pass; held out: consistent ['HF-round (3)'], refuted ['HF-trunc (3
of 3)']; repeat only: consistent none, refuted none`.

**Results [HW].** The stored numbers (the integer of the 24-bit field, x then y per vertex in the
input order) were, for t7-a, 1050636, 1050661, 1062918, 1053758, 1053719, 1062919, for t7-b
1050653, 1050628, 1062960, 1053709, 1053716, 1062966 and for t7-c 1050666, 1050642, 1062943,
1053706, 1053755, 1062938, which are the HF-round words in every one of the 18 fields; the
truncated words differ from them in 3 to 4 fields of each triangle (the residue 3 ones). The
coordinates decoded back to 8.04688, 8.14453; 56.0234, 20.2422; 20.0898, 56.0273 (t7-a), 8.11328,
8.01562; 56.1875, 20.0508; 20.0781, 56.2109 (t7-b) and 8.16406, 8.07031; 56.1211, 20.0391; 20.2305,
56.1016 (t7-c). 1/w was 0x3f800000 in all four jobs.

**What it shows.** The TA packs a window coordinate on the 1/1024 grid as the nearest multiple of
1/256, on 18 held-out coordinates (11 of residue 3, rounded up, and 7 of residue 1, rounded down,
none a tie). The simulator's refusal of such coordinates (sgx-pipe's ta.rs, `object_words`) can be
lifted for the 1/1024 grid without ties.

**Not shown.** The tie (residue 2, an exact half of a 1/256 step: to even, up or away), a
grid finer than 1/1024, coordinates computed through the viewport's multiply and add (the window x
here came out of the probe's own `--tri-v` path: whether the viewport's own arithmetic rounds
before the packing, as the three arithmetic orders of Q230 list, is not separated), and negative
window coordinates.
