+++
id = "E938"
claim = "r8-ldpm stages f9 and k on module 37EC97AB (Q211, the partial-render count of scenes of many objects and of several kicks): held out, F9's replay of the 1500-vertex scene gave the count at 13 of 15 cells and every run's peak at 6 (frozen 'not supported', 19 held, 11 FAILED of 30) at 1536x1536, 1024x1024 and 3072x2048, its rivals E854's d = 7/4 and d = 1 4 of 15 each and E625's overflow boundary 15 of 15; the two missed counts (1024x1024 thr0 0x48, 3072x2048 0x1a0) and the run peaks at 1536x1536 0x90 are band 4 cells where the second TA run peaked at thr0, the threshold not raised by 0x20 (read after the run); the three calibrations, controls, held; at five multi-kick scenes (explore: OL7 (b) had not fitted the kept cells) the multi-kick replay H-KICKS gave 11 of 20 counts (8 of 8 at 4096x4096, 3 of 12 at 2048x2048) and no run's peaks, the replay of the union 0 of 20"
unit = "dpm"
method = "r8-ldpm (render/closing-r8-ldpm), round 8's session L1 of round 7's leftovers (decision R8-8: safe class only, no held reset, no planned fault; plan closing8/leftovers/exp-leftovers-r8.md section 2), built on the session kit (resgx545 main 91f21da, data ca742f30e) and frozen before the run (FROZEN.sha256 3d2ef2ec..., kept as FROZEN.pre-fix.sha256; PREDICTIONS.sha256 24320c29...), dataset render-closing-r8-ldpm; attempt out/20261113-021431, run by the lead with the kit's driver (log run-r8l.log), 2026-11-13 from 02:14:31 Mac time, on the laptop, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls gate every later stage (they passed); no stop, fault, hang or lead decision. Every prediction came from the frozen OL7 tables (closing8/leftovers/ol7_c_tables.py, which loads E874's f5lib, E900's g3_span, F9's f9_loss and HU1 from their published copies hash-checked, ol7_tables.json sha256 ba59dc3a... in FREEZE-ol7c.sha256, written before L1 was built; its first run was stopped for speed with no output and its second run's k cells were refused at the build for up to 34 partial renders). The frozen scorer (score/score.as-run.py) re-run on the kept files gave output byte-identical to the kept score files in 7 of 7 stages; one post-run fix (POSTRUN-FIX.md: stage k's calibrations ended rc 1 with their diff line and were read as not completed). Post hoc (after the scores were read): postrun/misses.py and its output read every row. Stage f9 (18 jobs: at 1536x1536 and 1024x1024 thr0 0x24, 0x30, 0x48, 0x60, 0x90, at 3072x2048 0x60, 0x90, 0xc0, 0x120, 0x1a0, each target with a calibration at P 0x422 whose steps and need, 314, 153 and 773, were controls). Stage k (25 jobs: tri -n K --geometry 1 .. K - 1 --move i:(i - 1)DX,(i - 1)DY at 2048x2048 K 2, 3, 4 and 4096x4096 K 2, 4, moves chosen by ol7_c_tables.py where H-KICKS and H-UNION part most with at most 10 partial renders, a calibration at P 0x422 and four cells each; gated by a0's g-qf row). OL7 (b) (closing8/leftovers/ol7_b_multikick.py, frozen in FREEZE-ol7b.sha256 before its fit was read) did not reproduce 4 of 31 kept multi-kick cells of S1 and R1-pixgeo (counts 28, every peak 27; the union's 28 and 25), so by the plan k's counts ran as explore"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-ldpm:out/20261113-021431/f9/", "render-closing-r8-ldpm:out/20261113-021431/k/", "render-closing-r8-ldpm:postrun/", "cited-scratch:closing8/leftovers/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E874's F9 replays the 1500-vertex scene's page take with partial renders (a refused
page request starts a partial render that keeps the pages of objects not yet tiled; the threshold
raised by 0x20 after the first when R-5's guard raises); E874 read its counts as exploratory at
2048x2048. Stage f9 held it out at three targets with counts of 1 to 7. Stage k ran scenes of
several kicks of the default triangle, where E899 had read (G4) that a later kick fills the pages
its macrotiles left open.

**Frozen verdict (as printed).** `out/20261113-021431/score-f9.txt`: "f9: F9: F9 holds is not
supported: 19 held, 11 FAILED, 0 cannot tell of 30", "f9: d=7/4: ... 4 held, 11 FAILED ... of
15", "f9: d=1: ... 4 held, 11 FAILED ... of 15", "f9: E625: E625 holds (15 of 15 rows decided)";
the three calibrations PASS. `score-k.txt` (and the fixed scorer's `score-k.fixed.txt`): "k:
H-KICKS: cannot tell: no row decided", "k: H-UNION: cannot tell: no row decided" (explore rows):
H-KICKS 11 held, 29 FAILED of 40 explore rows, H-UNION 0 held, 40 FAILED.

**Results [HW].** F9's counts held at 13 of 15 cells: 1536x1536 7, 7, 3, 3, 2 at thr0 0x24 to
0x90, 1024x1024 3, 2, 2 (F9 1), 1, 1, 3072x2048 7, 6, 4, 3, 2 (F9 1); the last run's peak differs
by 1 to 3 pages at six cells. At k the counts at 4096x4096 were H-KICKS's at all eight cells (10,
4, 2, 2; 10, 5, 3, 2), at 2048x2048 one more than H-KICKS's at 8 of 12 cells and one fewer at one
(k22-n4 0x1c, 4 against 5) and 1 to 6 more
than the union's at all; run peaks matched at no cell (`postrun/misses.out`).

**Read after the run (post hoc).** The two missed counts and 1536x1536 0x90 are the band 4 cells
of the stage (S4 < thr0 < A4, 2 global pages left): in each the second TA run peaked at thr0
itself (0x48, 0x1a0, 0x90), so the threshold was not raised by 0x20, where R-5's guard as
formalized ("2 pages left raises") and F9 raised; the band 2 and 3 cells with 2 pages left raised.
That is E918's k-s4p1 cell again (S4 + 1, silent) [infer]. At 2048x2048 the multi-kick runs after
a partial render peak below thr0 + 0x20 several times (0xd, 0x12, 0x2a), as if a later kick's
render came before the threshold was reached.

**What it shows.** F9's replay gives the count of the 1500-vertex scene at other targets except
where the threshold is not raised at band 4. Neither the multi-kick replay of OL7 (b) nor the
union's gives the count of scenes of several kicks; H-KICKS is right at 4096x4096 only.

**What it does not show.** The raise rule at band 4 (Q210, R-5); a count rule for several kicks.
