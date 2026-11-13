+++
id = "E961"
claim = "r9-ldpm stages a0 and m6b on module B60AB0B4 (Q210; band 6 of the tool's 1500-vertex triangle): the premise held, r8-ldpm's six a0 controls repeated ('a0: the premise held (E935's a0 controls repeat on B60AB0B4) (1 of 1 rows decided)'), and E936's six band 6 cells at 1536x1536 and 4096x2048 repeated as controls (6 of 6); held out at four targets never run, H-NEXT1 (E960: the first partial render leaves 2 global pages iff S_6 < thr0 < the page count once object b_6 + 1 is tiled) 'holds (20 of 20 rows decided)', where H-SPAN (the end at A_6) is 'not supported', 14 held, 6 FAILED of 20: the second page was kept to A_6 + 2 at 2304x2304, A_6 + 3 at 2048x2304 and A_6 + 1 at 2304x1792, as H-NEXT1's ends, and ended at A_6 at 1792x1792, where both agree; H-NEXT2 19 of 20, E936's class rivals H-BIG6 2 of 4, H-ANY6 4 of 4 (it agrees with H-NEXT1 at these four A_6 cells), H-6LATE 3 of 4; the step replay held at three of the four calibrations and missed 2048x2304's S3 and S6 by one page (26 of 28), the four needs the replay's"
unit = "dpm"
method = "r9-ldpm (render/closing-r9-ldpm), round 9's session S9-ldpm (decision R9-5 (a): safe class only, no held reset, no planned fault; plan closing9/seeds/exp-seeds-r9.md section 7), built on the session kit (resgx545 main f32dfac, data 2d666bfa) and frozen before the run (FROZEN.sha256 8cb03392..., PREDICTIONS.sha256 54963f43...), dataset render-closing-r9-ldpm; attempt out/20261113-082650, run by the lead with the kit's driver (log fold/run-r9l.log), 2026-11-13, on the laptop, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753, every row replayed on the library mock built from it before the freeze) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls (r8-ldpm's rows token for token) gate every later stage (they passed); no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score files in 4 of 4 stages (fold/reproduce.out); no post-run fix. Post hoc (after the scores were read): fold/misses.py and its output read every row. Every prediction came from gen/r9_tables.json, the byte copy of offline/r9_tables.py's run 2 (FREEZE-tables.sha256), which loads E874's f5lib, E900's g3_span and F9's f9_loss from their published copies hash-checked (offline/ol7lib.py, r8-ldpm's), and from OD-1 to OD-3 (E960). Stage a0 (6 jobs): r8-ldpm's a0 rows token for token (2048x2048 calibrations at P 0x162 and 0x422, c4-b5, c4-b6, t-s3m6 at P 0x104, 0x105, 0xb9, g-qf at 4096x4096 P 0xa2). Stage m6b (34 jobs): controls, E936's cells 1536x1536 thr0 0x109, 0x10a, 0x10b and 4096x2048 0x362, 0x363, 0x364 (gps_next as E936 read them; no stop, one off would gate every verdict); at 2304x2304, 2048x2304, 2304x1792 and 1792x1792 a calibration at P 0x422 (held out: steps and need), thr0 A_6 - 1 to A_6 + 3 (held out) and A_6 again with --dump-render (explore). The cells are read as gps_next, the global pages of the first sample after the first partial render (E960's OD-2 (a)), and scored at the model's cell (no calibration alignment; E936's alignment tallied as H-SPAN-AL, 15 of 20)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-ldpm:out/20261113-082650/a0/", "render-closing-r9-ldpm:out/20261113-082650/m6b/", "render-closing-r9-ldpm:fold/", "render-closing-r9-ldpm:offline/", "vectors-closing-r9-ldpm-dpm"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E936 found band 6 keeping the second global page one to three cells past A_6 at five
of ten targets; E960 fitted the end to the object after the straddling block (H-NEXT1) on two of
them and found it at the eight others post hoc. Stage m6b held it out at four targets never run,
three where its end parts from A_6, after repeating six of E936's cells as controls.

**Frozen verdict (as printed).** `out/20261113-082650/score-a0.txt`: "a0: the premise held (E935's
a0 controls repeat on B60AB0B4) (1 of 1 rows decided)". `score-m6b.txt`: six controls PASS; "m6b:
H-NEXT1: H-NEXT1 holds (20 of 20 rows decided)", "m6b: H-SPAN: H-SPAN holds is not supported: 14
held, 6 FAILED, 0 cannot tell of 20", "H-NEXT2 ... 19 held, 1 FAILED", "H-BIG6 ... 2 held, 2
FAILED", "m6b: H-ANY6: H-ANY6 holds (4 of 4 rows decided)", "H-6LATE ... 3 held, 1 FAILED",
"H-STEPMODEL ... 26 held, 2 FAILED, 0 cannot tell of 28".

**Results [HW].** Global pages after the first partial render (gps_next), A_6 the replay's, E the
page count once object b_6 + 1 is tiled:

| target | A_6 | E | A_6 - 1 | A_6 | A_6 + 1 | A_6 + 2 | A_6 + 3 |
|---|---|---|---|---|---|---|---|
| 2304x2304 | 0x233 | 0x235 | 2 | 2 | 2 | 1 | 1 |
| 2048x2304 | 0x1f7 | 0x1fa | 2 | 2 | 2 | 2 | 1 |
| 2304x1792 | 0x1ba | 0x1bb | 2 | 2 | 1 | 1 | 1 |
| 1792x1792 | 0x161 | 0x161 | 2 | 1 | 1 | 1 | 1 |

The four dumped A_6 replicates read as their cells. The calibrations' needs were 0x298, 0x24f,
0x208 and 0x19f, the replay's; 2048x2304 read S3 `0xae` and S6 `0x1ad` (replay `0xad`, `0x1ac`).
The controls read 2, 2, 1 at 1536x1536 and 2, 1, 1 at 4096x2048, as E936.

**What it shows.** Band 6's margin ends at the page count once object b_6 + 1 is tiled, not at
A_6: held out at four targets, with E960's ten (fit and SEMI) fourteen. `dpm.rs` gives it at the
four held-out targets (`first_partial_render_global_pages_left`) and the steps of 2304x2304,
2304x1792 and 1792x1792.

**What it does not show.** Why the object after the straddling block; whether other bands end
there (bands 3 and 5 held at A_k, E915, where b_k + 1 may open no page) [infer]; 2048x2304's step
miss.
