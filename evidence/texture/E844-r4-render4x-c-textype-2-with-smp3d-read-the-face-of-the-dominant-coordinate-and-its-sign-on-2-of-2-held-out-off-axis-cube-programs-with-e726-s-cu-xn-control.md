+++
id = "E844"
claim = "R4-render4x stage c (3 probe fills of 64 x 32, TEXTYPE 2 sampled with smp3d): E726's own cu-xn program, run again as the control, read face 1 (-x) on 2048 of 2048 pixels with E726's pixels byte for byte, and two new off-axis programs, frozen before the run with the dominant-axis rule (face = 2 x axis + (coordinate < 0), axis u, v, w; +x, -x, +y, -y, +z, -z are faces 0 to 5 of 256 dwords each), read every pixel's predicted face, 2048 of 2048 each (r4g-cube-a: faces 0, 643, 0, 882, 235, 288 pixels; r4g-cube-b: 903, 0, 235, 261, 0, 649; all six faces between them, the dominant axis changing inside each image and no pixel within 0.0078 of a tie): the face select of E726, post hoc there, held out"
unit = "texture"
method = "R4-render4x (R4-G) stage c of the question-closing pass, round 4 (decision R4-3: Q113's held-out cube row, a stage added after s0), dataset render-closing-r4-render4x, first attempt out/20261111-211315 (stage c 21:13:59 Mac time), on the laptop (host cedar), 2026-11-11, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (fork resgx545 a2788bd8; installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, from resgx545 r3-rgn4 4623753); each job `probe --temps 32 --coords --pixels PROGRAM`, a debugfs reset before it, all 3 of class ok (rc 0), health ok after the stage; the gate (s0's three controls, all PASS) open; the two held-out programs built offline with p1141's own generator code (gen/cubegen.py, which rebuilds E726's six axis programs byte for byte in the session's tests), their coordinates: a, u = 1.5 (1 + x / 64) - 2.5, v = -0.5, w = 1.5 (1 + y / 32) - 2.25; b, u = 0.5, v = 1.5 (1 + x / 64) - 2.25, w = 1.5 (1 + y / 32) - 2.5; the face of every pixel, its histogram and sha256 frozen in predictions/c.tsv before the first job (FROZEN.sha256 80a16d2b..., PREDICTIONS.sha256 7ceff7ba...); scored by the frozen score/score_r.py c (out/20261111-211315/score-c.txt; scorekit byte for byte resgx545 eb84f54's), re-run on the kept files on 2026-11-11 with byte-identical output"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-render4x:out/20261111-211315/c/"]
terms = ["TEXTYPE"]
+++
**What ran.** E726 found TEXTYPE 2 under smp3d to be a cube map of six faces of 256 dwords, read
over 2048 of 2048 pixels of six axis directions, and named the faces +x, -x, +y, -y, +z, -z after
the dominant coordinate and its sign; the plan had predicted only faces 1, 3 and 5 for the
negative axes, so the mapping and the rule were post hoc. Q113 waited for a held-out row
(decision R4-3). Stage c ran E726's `cu-xn` again as the control, then two programs never run
before, whose three coordinates are all non-zero, one constant and two ramping, so that the
dominant axis changes inside the image; the rule's face for every pixel was frozen.

**Frozen verdict (as printed).** `c: control PASS, held-out [True, True]; Q113: TEXTYPE 2 with
smp3d reads the face of the coordinate of largest magnitude and its sign on 2 held-out off-axis
jobs (4096 pixels), the cu-xn control again as in E726: the face mapping is no longer post hoc
[infer]; Q113 may be retired as answered (R4-3), its edges and (s, t) are Q284's (2 of 2 rows
decided)`.

**Results [HW].**

| job | set | faces 0 to 5 (pixels) | read as the rule says |
|---|---|---|---|
| c-cu-xn | control | 0, 2048, 0, 0, 0, 0 | 2048 of 2048, E726's pixels byte for byte |
| c-cube-a | held out | 0, 643, 0, 882, 235, 288 | 2048 of 2048 |
| c-cube-b | held out | 903, 0, 235, 261, 0, 649 | 2048 of 2048 |

A pixel's value is 0xD0000000 plus the dword index of the scratch buffer it read; its face is the
index divided by 256. Between them the two held-out jobs read all six faces, and in each the face
changes inside the image where the largest magnitude passes from one coordinate to another.

**What it shows.** [HW] With TEXTYPE 2, smp3d picks the face by the coordinate of largest
magnitude and its sign, faces 0 to 5 for +x, -x, +y, -y, +z, -z, 256 dwords each, off the axes as
on them: E726's reading held out on 4096 pixels. With E725 and E726 this answers Q113's open
part: the TEXTYPE (2), the faces' order and distance in memory, and the face select. The names
of the faces are ours, after the axis that selects them [infer].

**What it does not show.** Where inside a face a pixel reads (the faces' (s, t)), the filtering
at a face's edge, ties between two equal magnitudes (no pixel was within 0.0078 of one) and faces
other than 16 x 16: Q284. One format, point sampling, one configuration of the T0 to T3 words.
