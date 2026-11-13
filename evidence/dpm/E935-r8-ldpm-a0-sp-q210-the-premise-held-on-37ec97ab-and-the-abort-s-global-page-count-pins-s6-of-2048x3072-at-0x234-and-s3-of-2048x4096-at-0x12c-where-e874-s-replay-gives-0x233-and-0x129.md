+++
id = "E935"
claim = "r8-ldpm stages a0 and sp on module 37EC97AB (Q210; the tool's triangle with 1500 vertices): the premise held, R7-dpm's six s-a0 controls repeated on this module ('a0: the premise held (R7's s-a0 controls repeat on 37EC97AB) (1 of 1 rows decided)'); held out, the global page count at the first abort (1 + the steps below thr0) pins 2048x3072's S6 at 0x234 (thr0 0x232 to 0x234 read 5 pages, 0x235 and 0x236 read 6; three calibrations read S6 0x234) and 2048x4096's S3 at 0x12c (thr0 0x125 to 0x12c read 2, 0x12d and 0x12e read 3): frozen verdicts H-R7S6 held 8 of 8 and H-KEPTS3 10 of 10, and E874's step replay, which gives 0x233 and 0x129 there, 'not supported' (26 held, 7 FAILED of 33); both controls (thr0 0xe8 = S4 of 2048x2048 3 pages, 0xe9 4) held"
unit = "dpm"
method = "r8-ldpm (render/closing-r8-ldpm), round 8's session L1 of round 7's leftovers (decision R8-8: safe class only, no held reset, no planned fault; plan closing8/leftovers/exp-leftovers-r8.md section 2), built on the session kit (resgx545 main 91f21da, data ca742f30e) and frozen before the run (FROZEN.sha256 3d2ef2ec..., kept as FROZEN.pre-fix.sha256; PREDICTIONS.sha256 24320c29...), dataset render-closing-r8-ldpm; attempt out/20261113-021431, run by the lead with the kit's driver (log run-r8l.log), 2026-11-13 from 02:14:31 Mac time, on the laptop, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls gate every later stage (they passed); no stop, fault, hang or lead decision. Every prediction came from the frozen OL7 tables (closing8/leftovers/ol7_c_tables.py, which loads E874's f5lib, E900's g3_span, F9's f9_loss and HU1 from their published copies hash-checked, ol7_tables.json sha256 ba59dc3a... in FREEZE-ol7c.sha256, written before L1 was built; its first run was stopped for speed with no output and its second run's k cells were refused at the build for up to 34 partial renders). The frozen scorer (score/score.as-run.py) re-run on the kept files gave output byte-identical to the kept score files in 7 of 7 stages; one post-run fix (POSTRUN-FIX.md: stage k's calibrations ended rc 1 with their diff line and were read as not completed). Post hoc (after the scores were read): postrun/misses.py and its output read every row. Stage a0 (6 jobs, every one a control declaring its readings, as R7-dpm's s-a0: two 2048x2048 calibrations at P 0x162 and 0x422, c4-b5, c4-b6 and t-s3m6 at P 0x104, 0x105 and 0xb9, g-qf at 4096x4096 P 0xa2; R-5's class was not read, the kit keeping no control block); stage sp (20 jobs: controls 2048x2048 thr0 0xe8 and 0xe9, R7-dpm s-k's k-b3 and k-s4p1 cells; 2048x3072 three calibrations at P 0x422 and thr0 0x232 to 0x236; 2048x4096 thr0 0x125 to 0x12e, no calibration completing there)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-ldpm:out/20261113-021431/a0/", "render-closing-r8-ldpm:out/20261113-021431/sp/", "render-closing-r8-ldpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E874's block-level replay of the TA gives the global steps S_k of the tool's
1500-vertex triangle; it had missed 2048x3072's S6 by one page (E915: a calibration read 0x234,
the replay 0x233) and 2048x4096's S3 by three (the kept creep cells, E874). Stage sp pinned each
step by the cell, not by a sampled bracket: the global page count at the first abort is 1 plus the
steps below thr0 (a step cell thr0 = S_k does not count its page, H-PENDREQ), so the first cell
whose count rises is S_k + 1. Its rivals were frozen from the earlier readings (H-R7S6: S6 0x234;
H-KEPTS3: S3 0x12c). Stage a0 repeated R7-dpm's six s-a0 controls on module 37EC97AB first.

**Frozen verdict (as printed).** `out/20261113-021431/score-a0.txt`: "a0: the premise held (R7's
s-a0 controls repeat on 37EC97AB) (1 of 1 rows decided)", six controls PASS.
`score-sp.txt`: "sp: H-STEPMODEL: H-STEPMODEL holds is not supported: 26 held, 7 FAILED, 0 cannot
tell of 33", "sp: H-R7S6: H-R7S6 holds (8 of 8 rows decided)", "sp: H-KEPTS3: H-KEPTS3 holds (10
of 10 rows decided)".

**Results [HW].**

| target | thr0 | global pages at the first abort | rows |
|---|---|---|---|
| 2048x2048 (controls) | 0xe8, 0xe9 | 3, 4 | the frozen values |
| 2048x3072 | 0x232, 0x233, 0x234 | 5, 5, 5 | S6 above 0x234 - 1 |
| 2048x3072 | 0x235, 0x236 | 6, 6 | S6 = 0x234 |
| 2048x4096 | 0x125 to 0x12c | 2 (8 cells) | S3 above 0x12b |
| 2048x4096 | 0x12d, 0x12e | 3, 3 | S3 = 0x12c |

The three 2048x3072 calibrations read the same steps, S2 to S7 `0x77`, `0xe6`, `0x156`, `0x1c3`,
`0x234`, `0x2a3`, and the need 783 (`0x30f`) as the replay, three times. a0's controls read S2 to
S7 and the need 0x213 in their brackets, 2 then 1 global pages left at c4-b5 and c4-b6, 1 at
t-s3m6, two partial renders with the peaks 0x80, 0xa0, 0x2 at g-qf: R7-dpm's E915 readings, on
module 37EC97AB.

**Read after the run (post hoc).** `postrun/misses.out`: at the step cell thr0 = 0x234 the first
partial render's last sample read 1 global page and the next sample 2 (the pending page of a grow,
as E918 read it); the 2048x4096 cells took three partial renders each.

**What it shows.** S6 of 2048x3072 is 0x234 and S3 of 2048x4096 is 0x12c, each the cell where the
abort's count rises, not a bracket: E874's replay is one page low at the first and three at the
second, as the earlier one-sample readings said. The premise of R7-dpm holds on module 37EC97AB.

**What it does not show.** Why the replay is off at these two targets (Q210); R-5's class at the
controls (not read here).
