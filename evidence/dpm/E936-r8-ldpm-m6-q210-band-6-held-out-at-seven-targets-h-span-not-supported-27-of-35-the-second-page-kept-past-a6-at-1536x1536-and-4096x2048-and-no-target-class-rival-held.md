+++
id = "E936"
claim = "r8-ldpm stage m6 on module 37EC97AB (Q210; band 6 of the tool's 1500-vertex triangle): held out at seven targets, H-SPAN (the first partial render leaves 2 global pages iff S_6 < thr0 < A_6, cells aligned on each target's calibration by R7's rule) is 'not supported', 27 held, 7 FAILED, 1 cannot tell of 35: 1536x1536 kept 2 pages at A_6 and A_6 + 1 and 4096x2048 at A_6, while 3072x2048 held (2 at A_6 - 1, 1 from A_6); the frozen rivals by target class all failed (H-BIG6 3 of 7, H-ANY6 2 of 7, H-6LATE 2 of 7); E874's step replay held at 1536x1536, 1024x1024, 4096x2048 and 3072x2048 and missed 2560x3072's S6 (0x2b4 against 0x2b3) and 3072x2560's S3 and S6 (0x116, 0x2b0 against 0x114, 0x2ae); read after the run, the first one-page cell lies 0 to 3 cells above A_6 by target (3072x3072 A_6 + 3, 2560x2560 + 2, 1536x1536 + 2, 4096x2048 and 2560x3072 + 1, the rest at A_6), not by the class of target"
unit = "dpm"
method = "r8-ldpm (render/closing-r8-ldpm), round 8's session L1 of round 7's leftovers (decision R8-8: safe class only, no held reset, no planned fault; plan closing8/leftovers/exp-leftovers-r8.md section 2), built on the session kit (resgx545 main 91f21da, data ca742f30e) and frozen before the run (FROZEN.sha256 3d2ef2ec..., kept as FROZEN.pre-fix.sha256; PREDICTIONS.sha256 24320c29...), dataset render-closing-r8-ldpm; attempt out/20261113-021431, run by the lead with the kit's driver (log run-r8l.log), 2026-11-13 from 02:14:31 Mac time, on the laptop, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls gate every later stage (they passed); no stop, fault, hang or lead decision. Every prediction came from the frozen OL7 tables (closing8/leftovers/ol7_c_tables.py, which loads E874's f5lib, E900's g3_span, F9's f9_loss and HU1 from their published copies hash-checked, ol7_tables.json sha256 ba59dc3a... in FREEZE-ol7c.sha256, written before L1 was built; its first run was stopped for speed with no output and its second run's k cells were refused at the build for up to 34 partial renders). The frozen scorer (score/score.as-run.py) re-run on the kept files gave output byte-identical to the kept score files in 7 of 7 stages; one post-run fix (POSTRUN-FIX.md: stage k's calibrations ended rc 1 with their diff line and were read as not completed). Post hoc (after the scores were read): postrun/misses.py and its output read every row. Stage m6 (69 jobs): controls 2048x2048 thr0 0x1c2 (2 pages left) and 0x1c3 (1), R7-dpm s-m's replicate cells; fit (mapping, with --dump-render) 3072x3072 thr0 0x3ce to 0x3d8 and 2560x2560 0x2b0 to 0x2b5 and their calibrations; held out at 1536x1536, 1024x1024, 4096x2048, 3072x2048, 2048x3072, 2560x3072 and 3072x2560 a calibration at P 0x422 and thr0 A_6 - 1 to A_6 + 3 of E900's A_6; explore band 7 of 2560x2560 (A_7 - 1 to A_7 + 2) and band 4 of 3072x3072 (A_4 - 1, A_4). A held-out cell's prediction is H-SPAN's at the model's cell thr0 - (S_6 read - S_6 model) when the calibration's S_6 bracket does not hold the model's (R7's alignment); the rivals were frozen at the A_6 cell: H-BIG6 (2 where both sides exceed 2048), H-ANY6 (2 where either does), H-6LATE (2 everywhere but 2048x2048), post hoc readings of E915's two misses"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-ldpm:out/20261113-021431/m6/", "render-closing-r8-ldpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E900's H-SPAN ends the margin in which the first partial render keeps two global
pages at A_k, the page count once the object block straddling global pages k - 1 and k is tiled;
E915 held it at bands 3 and 5 of four new targets and found band 6 of 3072x3072 and 2560x2560
keeping the second page at A_6. Stage m6 mapped those two targets cell by cell (fit) and held
band 6 out at seven targets of three classes with rivals frozen from the two misses.

**Frozen verdict (as printed).** `out/20261113-021431/score-m6.txt`: "m6: H-SPAN: H-SPAN holds is
not supported: 27 held, 7 FAILED, 1 cannot tell of 35", "m6: H-BIG6: ... 3 held, 4 FAILED, 0
cannot tell of 7", "m6: H-ANY6: ... 2 held, 5 FAILED", "m6: H-6LATE: ... 2 held, 5 FAILED"; both
controls PASS; H-STEPMODEL 58 held, 4 FAILED of 62 (the calibrations' steps in their brackets).

**Results [HW].** The global pages left by the first partial render at each run cell (the frozen
reader's: the last sample of the partial render), A_6 the replay's:

| target | A_6 | A_6 - 1 | A_6 | A_6 + 1 | A_6 + 2 | A_6 + 3 | calibration S_6, model |
|---|---|---|---|---|---|---|---|
| 1536x1536 | 0x109 | 2 | 2 | 2 | 1 | 1 | 0xe2, 0xe1 |
| 1024x1024 | 0x83 | 6 (2) | 1 | 1 | 1 | 2 (step) | 0x70, 0x6f |
| 4096x2048 | 0x362 | 2 | 2 | 1 | 1 | 1 | 0x2dc, 0x2db |
| 3072x2048 | 0x293 | 2 | 1 | 1 | 1 | 1 | 0x22d, 0x22c |
| 2048x3072 | 0x29a | 2 | 1 | 1 | 1 | 1 | 0x234, 0x233 |
| 2560x3072 | 0x333 | 2 | 2 | 1 | 1 | 1 | 0x2b4, 0x2b3 |
| 3072x2560 | 0x331 | 2 | 1 | 1 | 1 | 1 | 0x2b0, 0x2ae |
| 3072x3072 (fit) | 0x3cf | 2 | 6 (2) | 2 | 2 | 1 | 0x336, 0x335 |
| 2560x2560 (fit) | 0x2b1 | 2 | 2 | 2 | 1 | 1 | 0x244, 0x244 |

(In parentheses the global pages of the first sample after the partial render, where its last
sample still read the pages before the trim; 1024x1024's A_6 + 3 = S_7 is a step cell.) The fit
continues: 3072x3072 left 1 from 0x3d2 to 0x3d8, 2560x2560 from 0x2b3 to 0x2b5. Explore: band 7
of 2560x2560 left 2 at A_7 - 1 and 1 from A_7 (0x322); band 4 of 3072x3072 2 at A_4 - 1 and 1 at
A_4 (0x28a). The scorer's alignment moved 2048x3072 by one and 3072x2560 by two cells (their
calibrations' S_6 above the model's), and there H-SPAN failed at A_6 - 1 and A_6 - 2 of the run,
cells the unmoved model predicts (2 at A_6 - 1, 1 from A_6); 2560x3072, moved by one, held.

**Read after the run (post hoc).** `postrun/misses.out`: at 1024x1024 0x82 and 3072x3072 0x3cf the
partial render's last sample read 6 global pages and the next sample 2, so the "6" is the reader
catching the stretch before the global list was trimmed [infer]; with the next sample, 1024x1024
held at every scored cell and 3072x3072 kept 2 to A_6 + 2. The first one-page cell lies above
A_6 by 3 (3072x3072), 2 (2560x2560, 1536x1536), 1 (4096x2048, 2560x3072) and 0 (1024x1024,
3072x2048, 2048x3072, 3072x2560, and 2048x2048's controls); it is not set by the class of target
(1536x1536 and 4096x2048 have a side at most 2048) nor by the calibration's S_6 offset (3072x2048
and 2048x3072, S_6 one above the model, end at A_6) [infer].

**What it shows.** H-SPAN gives band 6's margin at five of ten targets run (2048x2048, 1024x1024,
3072x2048, 2048x3072 and 3072x2560 unaligned), and band 6 keeps the second global page one to
three cells past A_6 at the other five; no frozen class rule places the extra cells. E874's step
replay held at four held-out calibrations and missed two new targets by one and two pages.

**What it does not show.** What keeps the second page past A_6 (Q210); whether the calibration
alignment R7 froze is right (two targets read better unaligned, post hoc); bands above 7.
