+++
id = "E886"
claim = "R6-misc stage q086 (Q086, 10 of 21 4x jobs run, 11 skipped by the frozen fault budget, one attempt): on contexts made for 4x targets (four region-header arrays) a render with CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE poked over the kernel's completes exactly when the macrotile grid the words describe (the last boundary plus one more macrotile of the first's size, B3 + B1 tiles per axis) covers the target's 1x grid of 32 x 16 tiles: the six U2 and U2Q words, whose grid covers it, completed 320 x 160 to 640 x 480 with 0 wrong pixels, the closed driver's 64 x 64 words (0x802002, 0x802002, 4) at 320 x 160 and E511's HS words (the target's single-sampled words shifted right by one, 0x1004004 at both sizes) at 320 x 160 and 384 x 192, whose grid covers 4 or 8 tiles a side of the 10 or 12 needed, faulted the job on the 3D side (BIF fault requestor 256, word 0x10000011, 3 of 3), and the control (the rule's own words at 1024 x 768) completed with 0 wrong; frozen verdict 'H-COV held (9 of 9 held-out rows), H-ANY refuted (6 of 9); 11 rows not run; control R passes'; read after the run, each faulted image holds the triangle (and one to two tiles of background) inside the rectangle the words' grid covers and the sentinel everywhere past it"
unit = "ta"
method = "R6-misc stage q086 of the question-closing pass, round 6 (decisions R6-2 a, R6-5 a: fault budget 3; plan closing6/rank/rank-round6.md R6-4), dataset render-closing-r6-misc, on the laptop (host cedar), 2026-11-12, attempt out/20261112-144153 (stage started 14:45:57 Mac time, the third of three; run-r6m.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the rgn4 module, installed = loaded, knobs at their defaults at the stage start), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (t4, sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a); E511's 20 skipped cases (ta/mtile-msaa-risky skipped.tsv: U2, U2Q, FX and HS words written by the tool's `--kpoke-render 1:ta:143/144/146` over the kernel's) and the safe script's 1024 x 768 R, each `tri --tri-full --pixels --aa4` with E824's 4x words (`CR_TE_AA` 0xe0000000, MULTISAMPLECTL 0xeaa26e26) at its size, a debugfs reset before each job, every pixel read; H-COV (frozen from a post hoc fit on E511's 6 jobs, 6 of 6) and H-ANY (every word set completes with four arrays) frozen with the tables before the first job (freeze 1: FROZEN.sha256 3199ecac..., PREDICTIONS.sha256 839d74ea...; FROZEN.commits pins the resgx545 files read at d9b2969), R first, the U2 and U2Q rows next (where both hypotheses predict completion), then FX, then HS last; the fault budget of 3 split into hypothesis groups u (1 fault), fx (1) and hs (2): a group that reached its count skipped its other rows, so after the first FX fault the 6 other FX rows and after the second HS fault the 5 other HS rows were not run (no lead decision; the runner's frozen rule); every fault of the 3D-side class (BIF_INT_STAT 0x0100, BIF_FAULT 0x100000xx), strict health after each (passed), health ok after the stage; the session was refrozen after this attempt for stage q287 only and this stage's verdict had been seen by the lead before. Scored by the frozen score/score_m.py q086 in the run (score-q086.txt); at the fold (2026-11-12) freeze 2's scorer (no verdict changed) re-run on the kept files gave output byte-identical to the kept one, and all 60 kept files decompress to the raw sha256 the laptop logged (fold/reproduce.sh, fold/reproduce.out); fold/q086_extent.py (post hoc, not frozen) counts each image's pixels inside and outside the words' covered rectangle"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-misc:out/20261112-144153/q086/", "render-closing-r6-misc:fold/"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA"]
+++
**What ran.** E511 ran 6 of its 26 poked 4x cases and skipped 20 at 320 x 160 and larger, where
4x faulted even with the rule's own words; E824 showed those faults were the kernel's one-array
layout, and with four region-header arrays 8 of 8 sizes up to 1024 x 768 complete. Stage q086 ran
the 20 skipped cases on contexts made for 4x targets, with the 1024 x 768 R job as the control.
The words are E511's families: U2 and U2Q (macrotiles of two tiles, with the quarter-block stride),
FX (the closed driver's 64 x 64 words 0x802002, 0x802002, stride 4) and HS (the target's
single-sampled words shifted right by one, the stride halved: the closed 64 x 64 relation). H-COV, read post hoc on
E511's 6 jobs, says a job completes iff the macrotile grid the words describe covers the target's
1x tile grid (B3 + B1 tiles per axis, `gen/models.py`), and otherwise faults on the 3D side; H-ANY
says that with four arrays every word set completes.

**Frozen verdict (as printed).** `Q086: H-COV held (9 of 9 held-out rows), H-ANY refuted (6 of
9); 11 rows not run; control R passes`.

**Results [HW].** From `out/20261112-144153/score-q086.txt` (cover: B3 + B1 tiles of the words'
grid, of the target's tiles across and down):

| job | cover of tiles | H-COV | observed |
|---|---|---|---|
| R 1024 x 768 (control) | 32, 48 of 32, 48 | ok | ok, 0 wrong of 786432 |
| U2 320 x 160, 384 x 192, 640 x 480 | 12, 12 of 10, 10; 12, 12 of 12, 12; 24, 32 of 20, 30 | ok | ok, 0 wrong |
| U2Q 448 x 224, 512 x 256, 512 x 384 | 16, 16 of 14, 14; 16, 16 of 16, 16; 16, 24 of 16, 24 | ok | ok, 0 wrong |
| FX 320 x 160 | 4, 4 of 10, 10 | fault | fault, 256 / 0x10000011 |
| HS 320 x 160, 384 x 192 | 8, 8 of 10, 10; 8, 8 of 12, 12 | fault | fault, 256 / 0x10000011 |
| FX 384 x 192 to 1024 x 768 (6), HS 448 x 224 to 1024 x 768 (5) | under the target | fault | not run |

Every completed job printed `diff: 0 of W*H` with H pixel rows. The three faults are the 3D-side
class the session allowed (bus-interface requestor 256, fault word 0x10000011, as E511's three);
strict health passed after each. Of the U2 and U2Q rows, three have a grid that covers the target
exactly (384 x 192, 512 x 256, 512 x 384) and three one that passes it.

**Read after the run (post hoc, not frozen; `fold/q086_extent.py`).** In the three faulted jobs
every pixel past the rectangle the words' grid covers (128 x 64 for FX, 256 x 128 for HS) kept the
sentinel (43008, 18432 and 40960 pixels), and inside it the image holds the triangle's colour
except 512, 1024 and 768 pixels of the background colour (one, two and one and a half 32 x 16
tiles' worth). Every completed image is the triangle's colour at every pixel.

**What it shows.** [HW] With four arrays the 4x render's completion still depends on the macrotile
words: the ones whose grid covers the target complete exactly, the ones whose grid falls short
fault, so four arrays did not make every word set valid (H-ANY refuted, 3 of 3 short grids
faulted). H-COV held on every row that ran, held out (9 of 9). [infer] The tiles inside the
covered grid are rendered before the fault and the first tile past it faults the 3D side, as the
images suggest; which tile faults was not read.

**What it does not show.** The closed driver's rule for the 4x macrotile words over sizes (Q086:
the capture batch has not run); the 11 rows skipped by the budget, among them every FX row past 320
x 160 and every HS row past 384 x 192; why a short grid faults rather than
drops tiles, and what bit 23 of the 4x words marks. One run of each job, one boot.
