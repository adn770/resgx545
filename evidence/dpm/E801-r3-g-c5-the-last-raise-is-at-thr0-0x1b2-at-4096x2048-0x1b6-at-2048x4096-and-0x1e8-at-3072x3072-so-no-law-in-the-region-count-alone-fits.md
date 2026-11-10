+++
id = "E801"
claim = "R3-geo stage g-c5 (36 jobs, the tool's triangle with 1500 vertices at three more targets, 12 a target: a calibration at P 0x422, 5 fixed cells and 6 bisect cells the runner picked from kept output; 33 run, 3 skipped as the bracket had closed): at each target one exact flip, the last raise at thr0 0x1b2 and the first silent at 0x1b3 at 4096x2048, 0x1b6 and 0x1b7 at 2048x4096, 0x1e8 and 0x1e9 at 3072x3072 (C = thr0 + 0x20: 0x1d2, 0x1d6 and 0x208 [arithmetic]); the two targets of equal region count, 4096x2048 and 2048x4096, have different limits, so every frozen law in the target's size was REFUTED at every target: LT (C proportional to the region count from 0x351 at 4096x4096; it predicted 0x1a8, 0x1a8 and 0x1dd), and the affine laws through g-c4's measured 2048x2048 point and 4096x4096 in the region count (0x1b1, 0x1b1, 0x1e5), in the tail-pointer side squared (0xe2, 0x351, 0x351) and in the macrotile area (0x1b1, 0x1b1, 0x1e5); the three calibrations were void for the raise (page need read 0x3f7, 0x400 and 0x400)"
unit = "dpm"
method = "R3-geo stage g-c5 of the question-closing pass, round 3 (session L1, decision R3-G5; eighth of nine stages, 36 jobs; the fixed cells are the ends of the affine-in-regions bracket and LT's flip pair, PREFLIGHT deviation 4), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:54:13 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width W --height H --vertices 1500 --dump-render with p1139-green, render_pb_pages written to P and read back, the regtimeline of g-c4, a debugfs reset before each job, 33 run of class ok (rc 3 for 32, rc 0 for c5a-cal), 3 skipped by the runner (c5a-b6, c5b-b6, c5c-b6: bracket closed); scored by the frozen score/score_r3.py g-c5 (out/score-g-c5.txt) with g-c4's controls and g-c4's measured C at 2048x2048, every law evaluated by the frozen scorer; C = the last raised thr0 + 0x20 is E774's definition applied to the scorer's thr0"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-c5/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** C was exact at 4096x4096 (0x371, E774) and at 2048x2048 (0x102, E799). Square
targets cannot separate a law in the region count from one in the macrotile area or the
tail-pointer side; 4096x2048 against 2048x4096 can (equal region counts, different sides). Each
target had a calibration, five fixed cells and up to six bisect cells.

**Frozen verdict (as printed).** `controls pass (g-c4's); laws consistent with all three targets
none, refuted ['LT', 'AR', 'AS', 'AM']; 4096x2048 and 2048x4096 (equal regions) have DIFFERENT
limits: every law in regions alone is REFUTED; 2048x2048 limit from g-c4 0xe2`. Per target: `LT
(the last raise thr0 proportional to the region count): c5a REFUTED (predicts 0x1a8); c5b REFUTED
(predicts 0x1a8); c5c REFUTED (predicts 0x1dd)`; `affine in regions through the two exact points:
... (predicts 0x1b1) ... (0x1b1) ... (0x1e5)`; `affine in the tail-pointer side squared: ...
(0xe2) ... (0x351) ... (0x351)`; `affine in the macrotile area: ... (0x1b1) ... (0x1b1) ...
(0x1e5)`.

**Results [HW].** The observations by thr0 (R raised, N not), as the scorer listed them:

| target | observations | last raise | page need (calibration) |
|---|---|---|---|
| 4096x2048 (c5a) | 0x19b R, 0x1a8 R, 0x1a9 R, 0x1b0 R, 0x1b1 R, 0x1b2 R, 0x1b3 N, 0x1b7 N, 0x1c5 N, 0x1c6 N | 0x1b2 (exact) | 0x3f7 |
| 2048x4096 (c5b) | 0x19b R, 0x1a8 R, 0x1a9 R, 0x1b0 R, 0x1b3 R, 0x1b5 R, 0x1b6 R, 0x1b7 N, 0x1c5 N, 0x1c6 N | 0x1b6 (exact) | 0x400 |
| 3072x3072 (c5c) | 0x1d1 R, 0x1dd R, 0x1de R, 0x1e4 R, 0x1e7 R, 0x1e8 R, 0x1e9 N, 0x1ea N, 0x1f6 N, 0x1f7 N | 0x1e8 (exact) | 0x400 |

Every observation is a cell with two partial renders, except c5b-b1 (thr0 0x1b7, three, peaks
0x1b7 three times, none). In the raised cells the second run peaked at thr0 + 0x20. The
calibrations at P 0x422 (thr0 0x400) were void for the raise: c5a-cal never overflowed (peak
0x3f7), c5b-cal and c5c-cal overflowed once at 0x400 (the scorer reads the need as 0x400). Each
target's flip lies between two cells one apart, so each limit is exact.

**What it shows and does not.** With the scene held (1500 vertices of the tool's triangle) C is
0x1d2 at 4096x2048 and 0x1d6 at 2048x4096: the same region count, a different limit, so C is not a
function of the region count alone, and the macrotile-area and side-squared affine laws through
the two square targets miss too. The ordered list of the measured limits is 0x102 (2048x2048),
0x1d2, 0x1d6, 0x208 (3072x3072), 0x371 (4096x4096); no law in the target's size is offered. Whether
the difference between the two transposed targets comes from the target or from where the scene's
triangles land in it is not separated.
