+++
id = "E963"
claim = "r9-ldpm stage f9b on module B60AB0B4 (Q211's count of the 1500-vertex scene, Q210's raise at band 4): the three calibrations held as controls (1280x1280, 1792x1792 and 2560x2048 never run: steps in their brackets, needs 0xe2, 0x19f, 0x28c, the replay's); off band 4 F9's replay gave the partial-render count at 5 of 5 cells and every run peak at 2 (the last run's peak 1 to 3 pages off at 3), at the three band 4 cells with 2 global pages left the threshold was not raised (the second TA run peaked at thr0 and a second partial render came: 2 renders where F9 with R-5's guard as formalized gives 1), H-NORAISE's count 3 of 3 (its last run's peak 1 page off at each): frozen 'F9 holds is not supported: 7 held, 9 FAILED, 0 cannot tell of 16', 'H-NORAISE holds is not supported: 3 held, 3 FAILED of 6'; E625's boundary and the abort's global pages (E935's rule) 8 of 8 each, E854's d = 7/4 and d = 1 0 of 8"
unit = "dpm"
method = "r9-ldpm (render/closing-r9-ldpm), round 9's session S9-ldpm (decision R9-5 (a): safe class only, no held reset, no planned fault; plan closing9/seeds/exp-seeds-r9.md section 7), built on the session kit (resgx545 main f32dfac, data 2d666bfa) and frozen before the run (FROZEN.sha256 8cb03392..., PREDICTIONS.sha256 54963f43...), dataset render-closing-r9-ldpm; attempt out/20261113-082650, run by the lead with the kit's driver (log fold/run-r9l.log), 2026-11-13, on the laptop, module srcversion B60AB0B475DD1E8972419B5 (fork 2a650d74; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753, every row replayed on the library mock built from it before the freeze) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls (r8-ldpm's rows token for token) gate every later stage (they passed); no stop, fault, hang or lead decision. The frozen scorer re-run on the kept files gave output byte-identical to the kept score files in 4 of 4 stages (fold/reproduce.out); no post-run fix. Post hoc (after the scores were read): fold/misses.py and its output read every row. Every prediction came from gen/r9_tables.json, the byte copy of offline/r9_tables.py's run 2 (FREEZE-tables.sha256), which loads E874's f5lib, E900's g3_span and F9's f9_loss from their published copies hash-checked (offline/ol7lib.py, r8-ldpm's), and from OD-1 to OD-3 (E960). Stage f9b (11 jobs): at 1280x1280, 1792x1792 and 2560x2048 a calibration at P 0x422 (control: need, ctl:need stops the stage when off; steps), cells off band 4 where F9's count with and without R-5's raise agree and part from E854's d = 7/4 and d = 1 (1280x1280 0x62; 1792x1792 0x44, 0x8a; 2560x2048 0x64, 0xd9) and one band 4 cell with H-SPAN's 2 global pages left where F9 (raised) and H-NORAISE part on the count (0x72, 0xde, 0x164)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r9-ldpm:out/20261113-082650/f9b/", "render-closing-r9-ldpm:fold/", "vectors-closing-r9-ldpm-dpm"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** F9's replay gave 13 of 15 held-out counts in E938; its misses were band 4 cells with 2
global pages left where the threshold was not raised. Stage f9b ran F9 at three new targets off band
4 and froze H-NORAISE (no raise at band 4) against F9's raise at one band 4 cell each.

**Frozen verdict (as printed).** `out/20261113-082650/score-f9b.txt`: three controls PASS; "f9b: F9:
F9 holds is not supported: 7 held, 9 FAILED, 0 cannot tell of 16", "f9b: H-NORAISE: H-NORAISE holds
is not supported: 3 held, 3 FAILED, 0 cannot tell of 6", "f9b: E625: E625 holds (8 of 8 rows
decided)", "f9b: H-ABORT: H-ABORT holds (8 of 8 rows decided)", d=7/4 and d=1 "0 held, 8 FAILED".

**Results [HW].** Off band 4 (counts, run peaks; F9's in parentheses where they differ): 1280x1280
0x62 2, `0x62, 0x62, 0x60` (`0x61`); 1792x1792 0x44 6, last peak `0x3f` (`0x3e`); 0x8a 3, every
peak; 2560x2048 0x64 6, last peak `0x63` (`0x60`); 0xd9 3, every peak. Band 4: 1280x1280 0x72 2,
`0x72, 0x72, 0x27` (H-NORAISE `0x25`); 1792x1792 0xde 2, `0xde, 0xde, 0x3f` (`0x3e`); 2560x2048
0x164 2, `0x164, 0x164, 0x60` (`0x5f`).

**What it shows.** F9 gives the count of the 1500-vertex scene off band 4 (5 of 5 here, 18 of 20
with E938) and at band 4 with 2 global pages left the threshold is not raised (3 of 3 here, as at
E938's three and E918's k-s4p1), against R-5's guard as formalized.

**What it does not show.** Why band 4 is not raised where bands 2, 3 and 5 are; the last run's
peak (1 to 3 pages off at 6 of 8 counted cells).
