+++
id = "E962"
claim = "r9-ldpm stage w on module B60AB0B4 (Q211, the need of wide scenes of many vertices): held out at four targets wider than 2:1 never run, E874's replay gave the need of the 1500-vertex scene at each calibration ('w: H-REPLAY: H-REPLAY holds (8 of 8 rows decided)': 4096x1024 0x20f, 4096x1536 0x302, 3584x1024 0x1d0, 2048x512 0x9a, no partial render) and HU1 of the scene's triangles none ('HU1 holds is not supported: 0 held, 4 FAILED'); every calibration read S6 one or two pages above the replay (and 4096x1536 S3 one above), so each FAILED as a control (its frozen steps) and gated its own cell: the cells' frozen verdicts printed 'controls FAILED' (a result of the premise the build chose, not a scorer fault); read after the run without that gate, the four cells gave F9's count and every run peak (4 of 4), E625's overflow and the abort's global pages (E935's rule) 4 of 4, and E854's d = 7/4 and d = 1 none"
unit = "dpm"
method = "r9-ldpm (render/closing-r9-ldpm), round 9's session S9-ldpm (decision R9-5 (a): safe class only, no held reset, no planned fault; plan closing9/seeds/exp-seeds-r9.md section 7), built on the session kit (resgx545 main f32dfac, data 2d666bfa) and frozen before the run (FROZEN.sha256 8cb03392..., PREDICTIONS.sha256 54963f43...), dataset render-closing-r9-ldpm; attempt out/20261113-082650, run by the lead with the kit's driver (log fold/run-r9l.log), 2026-11-13, on the laptop, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753, every row replayed on the library mock built from it before the freeze) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls (r8-ldpm's rows token for token) gate every later stage (they passed); no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score files in 4 of 4 stages (fold/reproduce.out); no post-run fix. Post hoc (after the scores were read): fold/misses.py and its output read every row. Every prediction came from gen/r9_tables.json, the byte copy of offline/r9_tables.py's run 2 (FREEZE-tables.sha256), which loads E874's f5lib, E900's g3_span and F9's f9_loss from their published copies hash-checked (offline/ol7lib.py, r8-ldpm's), and from OD-1 to OD-3 (E960). Stage w (8 jobs): at 4096x1024, 4096x1536, 3584x1024 and 2048x512 (E960's OD-1) a calibration at P 0x422, a control whose pass needs its need and every step S2 to S7 in its bracket and which gates only its own cell (no stop), and one cell (thr0 0x9d, 0xed, 0x8a, 0x42: where F9's count with and without R-5's raise agree and part from E854's d = 7/4 and d = 1)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-ldpm:out/20261113-082650/w/", "render-closing-r9-ldpm:fold/", "render-closing-r9-ldpm:offline/", "vectors-closing-r9-ldpm-dpm"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E939 held HU1 for scenes of one object; the 1500-vertex scene's need comes from E874's
replay (E960). Stage w held the replay's need out at four wide targets and ran one F9 cell each.

**Frozen verdict (as printed).** `out/20261113-082650/score-w.txt`: the four controls "FAILED"
(`w-cal-c1604`: "s6 [0x17d, 0x17e] (frozen 0x17c)"; `w-cal-c1606`: "s3 [0xe1, 0xe1] (frozen
0xe0); s6 [0x22a, 0x22b] (frozen 0x229)"; `w-cal-c1404`: "s6 [0x14e, 0x14f] (frozen 0x14d)";
`w-cal-c0802`: "s6 [0x6f, 0x6f] (frozen 0x6e)"); "w: H-REPLAY: H-REPLAY holds (8 of 8 rows
decided)"; "w: HU1: HU1 holds is not supported: 0 held, 4 FAILED, 0 cannot tell of 4"; F9, d=7/4,
d=1, E625 and H-ABORT "controls FAILED".

**Results [HW].** Needs 0x20f, 0x302, 0x1d0, 0x9a, each the replay's (HU1 0x53, 0x78, 0x4b, 0x1d).
Steps: S2 to S5 and S7 the replay's, S6 `0x17e`, `0x22b`, `0x14f`, `0x6f` against `0x17c`,
`0x229`, `0x14d`, `0x6e`. Cells: 3, 3, 3 and 2 partial renders with the peaks F9 froze (`0x9d,
0xbd, 0xbd, 0x4f`; `0xed, 0x10d, 0x10d, 0x72`; `0x8a, 0xaa, 0xaa, 0x47`; `0x42, 0x42, 0x31`), 3
global pages at the first abort each.

**Read after the run (post hoc).** `fold/misses.out`, `fold/FOLD.md`: the cells read without
their calibration's gate give every frozen F9, E625 and abort-count value; the gate was the
builder's choice (exact replay steps as the premise of a count in bands 2 and 3).

**What it shows.** The need of the 1500-vertex scene is E874's replay U at wide targets too
(4 of 4 held out; thirteen targets with E960's nine kept calibrations), and its S6 runs one or two
pages above the replay
at all four, as at 2048x3072, 2560x3072 and 3072x2560 (E935, E936).

**What it does not show.** The need of wide scenes of other vertex counts (E630's 300 to 900) or
of 8 coordinate pairs; why S6 is late; F9's counts as a verdict (gated).

**Correction 2026-11-13 (round 10):** "S6 runs one or two pages above the replay" and "why S6 is
late" are read with E1009's replicates: the sampled bracket of S6 has its lower end at the replay
plus 1 in all four of these calibrations (0x6f, 0x14e, 0x17d, 0x22a against 0x6e, 0x14d, 0x17c,
0x229) and in 15 of 15 new replicates, the upper end moving by a page between runs. The replay is
low there by a bias of at least one page (H-BIAS 4 of 5 targets, H-NOISE 0 of 5), not by noise.
The gate of the calibrations on their steps stands as the record printed it.
