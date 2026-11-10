+++
id = "E754"
claim = "With every vertex at one w inside the guard band (x and y scaled by w, so the stored x and y equal the original triangle's: 4 of 4 jobs, w = 3, 7, 0.003 and 3e-5), the 1/w word of the TA's object is the float32 reciprocal truncated toward zero in 4 of 4 (0x3eaaaaaa, 0x3e124924, 0x43a6aaaa, 0x47023555 at all three vertices; round-to-nearest, one unit above, refuted 4 of 8 checks), the frozen held-out verdict of group e3i with its control (w = 1, E651's object) passing; with w = 1e-5 under a clamp (block word 14) of 3e-5, 1e-4, 3e-4 and 1e-3 the stored object has the original's x and y shrunk about the centre by w / clamp (to the 1/64 pixel) and 1/w = 1/clamp in 4 of 5 jobs (one of them with the clamp equal to w, so unshrunk), the fifth, at 1e-3, writing no object, and the clamp jobs' 1/w words are the truncated reciprocal in one case (3e-5) and the rounded one in another (3e-4), so every frozen clamp model (replace by the clamp with truncation or with rounding, the triangle shrinks, the object removed) is refuted at least once and none is consistent; the repeat of S1's cuts (z = +w and -w) gives clipped polygons of 4 and 3 vertices that are not the original three, 2 of 2"
unit = "ta"
method = "S1b stage g-e3 of the question-closing pass (14 jobs, each a vtxuse probe on a 64 x 64 target with --dump-render of the TA's object, group-gated: e3i (the w scan: control e3i-ctl w = 1, then w = 3, 7, 0.003 and 3e-5 with vertex program vtx_wclip taking S = w, A = 0, B = w), e3z (flat z = 0.99 control; the cuts z = 2x + 1 and 2x - 1, repeats of S1's e3z-cut-p and -m), e3k (control e3k-ctl, S1's w = 1e-5 under clamp 1e-3 with vtx_w; then w = 1e-5 in band with block word 14 = 1e-5, 3e-5, 1e-4, 3e-4 and 1e-3)), the scorer's decoder reading the parameter-buffer and TA-data dumps of each job; laptop (direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71); tables, predictions (RZ32 and RN32 of the exact reciprocal of the float32 word, both frozen), scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256); scored by the frozen score/score_s1.py g-e3 (out/score-g-e3.txt, re-run from the dataset with the same output); every job rc 0 and class ok, the kernel log clean; the words below were also found by counting them in the dumps"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/g-e3/"]
terms = ["PB_OBJ.RHW", "WCLAMP", "VIEWPORT.X_OFFSET"]
+++
**What ran.** E736 (S1) dumped the TA's object over seven groups and could not score the 1/w rule:
its w = 1e-3 and 1e-5 jobs were clipped to the guard band, so every stored vertex was made by the
clip, and its WCLAMP control wrote an object where the design expected none. S1b froze three
groups, each gated by its own controls only (the scorer prints "cannot tell" for a group whose
control fails, and no group did): e3i scans w inside the guard band, with the vertex program
scaling x and y by w so no vertex is clip-made, at four w where the truncated and the rounded
reciprocal differ; e3z repeats S1's two z cuts and scores them by vertex identity; e3k puts the
clamp above w = 1e-5 in five steps. The truncated reciprocal (RZ32) was fitted on E-records of the
mte/rhw table (9 vertices), the new w values are new inputs to it; the clamp models and the cuts
are S1 post-hoc readings (HREP, HC-poly), so e3z is a repeat and the e3k models are post hoc
frozen here.

**Frozen verdict.** `e3i: held out: consistent ['RZ32(1/w) [fit: mte/rhw 9 vertices] (8)', 'in
band: x/w = the original (4)'], refuted ['RN32(1/w) (4 of 8)']; repeat only: consistent none,
refuted none; e3z: held out: consistent none, refuted none; repeat only: consistent ['HC-poly (S1
post hoc: both cuts clipped polygons) (2)'], refuted ['HC-orig (2 of 2)']; e3k: held out:
consistent none, refuted ['HREP ... RZ (3 of 10)', 'HREP ... RN (3 of 10)', "HREM (E194's image
read as removal) (3 of 5)", 'HREP-xy (1 of 5)']; repeat only: consistent none, refuted none`
(out/score-g-e3.txt; the HREP and HREP-xy names are shortened here). Controls: e3i-ctl and
e3z-flat099 equal E651's object (1/w 0x3f800000, the default triangle); e3k-ctl reproduced S1's
measurement (4 vertices, a square 0.96 pixel wide at the centre, x and y 31.5195 to 32.4805, 1/w
0x4479ffff at all four).

**Results [HW].** e3i: at w = 3, 7, 0.003 and 3e-5 the object is present with 3 vertices at (8,
8), (56, 20), (20, 56), the original triangle, and a 1/w of 0x3eaaaaaa, 0x3e124924, 0x43a6aaaa and
0x47023555 at all three vertices (the rounded reciprocals would be ...ab, ...25, ...ab and ...56;
the rounded word of w = 3 occurs in no dump of that job). e3z (repeat only): z = 2x + 1 stored 4
vertices, (32, 44), (20, 56), (32, 14) and (8, 8); z = 2x - 1 stored 3, (56, 20), (32, 44) and
(32, 14), not the original three; the 1/w words of both are 0x3f800000 and 0x3f800001 (the
clip-made vertices carry one unit more), as in E736. e3k, w = 1e-5 in band, x and y scaled by w:

| clamp | object | x and y | 1/w word | reciprocal of the float32 clamp |
|---|---|---|---|---|
| 1e-5 (= w) | present | the original, (8, 8) (56, 20) (20, 56) | 0x47c35000 | 100000.0025 |
| 3e-5 | present | (24, 24) (40, 28) (28, 40) = shrunk by 1/3 | 0x47023555 | 33333.3342, truncated |
| 1e-4 | present | (29.6, 29.6) (34.4, 30.8) (30.8, 34.4) = by 1/10 | 0x461c4000 | 10000.00025 |
| 3e-4 | present | (31.2, 31.2) (32.8, 31.6) (31.6, 32.8) = by 1/30 | 0x45505555 | 3333.33318, rounded |
| 1e-3 | none | | | |

Each frozen clamp model misses at least once: truncation (RZ) at the 3e-4 word (it predicted
...54) and at the 1e-3 job, rounding (RN) at the 3e-5 word (it predicted ...56) and at the 1e-3
job, the position clause at the 1e-3 job, and "removed" at 3e-5, 1e-4 and 3e-4.

**Post hoc (read after the run; [infer], not held out).** For the four clamp jobs that wrote an
object, the stored x and y equal x_in / clamp and the 1/w equals 1 / clamp, i.e. the TA divides by
the clamp where w is below it, which is S1's replacement reading with its position clause; the
position clause was not what S1's e3k-ctl square gave for the other program (vtx_w leaves x and y
at +-0.75), so this reading rests on the vtx_wclip jobs. The 1e-3 job's missing object is a
triangle 0.48 pixel wide (31.76 to 32.24), not a different rule, but E736's e3k-ctl, a 0.96 pixel
square, was written, so a size limit is not shown either. The 1/w rounding is not one rule over
all paths: truncated for w itself at four values and for the clamp 3e-5, rounded at the clamp 3e-4
(where the two float32 neighbours differ by 2.4e-4 and the exact value lies 0.77e-4 from the
rounded one); the clamp's reciprocal may be computed another way than w's. Counts of the frozen
scorer: "refuted 4 of 8" for RN32 is 4 jobs by two checks each, the object (hit) and the word
(miss).

**Not shown.** What the e3z or e3k models say about w at the boundary (clamp equal to w gives the
original's words, one job), the rounding of 1/w for w below 1e-4 other than the clamp, other
exponents of w than the four, depth at w other than 1 (the group scored no depth), whether the
clamp-substituted x and y or the 1/w come first, a triangle that is sub-pixel by construction (the
object of the 1e-3 job and the e3k-ctl one differ in size and in program), and the limit of the
guard band (e3i stays in band by construction).