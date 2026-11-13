+++
id = "E939"
claim = "r8-ldpm stages k and u on module 37EC97AB (Q211, the U clause): HU1's page need of the union of a scene's triangles (a region counted once, 128 bytes a stream, a page per 32 streams of a macrotile, plus the global page) was held out at five scenes of two to four kicks of the default triangle (2048x2048 and 4096x4096, U 108, 131, 136, 377, 492: 'k: HU1: HU1 holds (10 of 10 rows decided)' by the fixed scorer, the frozen one printing 'cannot tell' for a bug, POSTRUN-FIX.md) and at eight one-triangle shapes drawn by --tri-unit 12 --tri-v at four targets, from the full target to slivers 8 pixels wide and a 20-pixel triangle (U 2 to 257: 'u: HU1: HU1 holds (16 of 16 rows decided)'), each a completed job at P 0x422 with no partial render; the rival H-BBOX (a stream for every region of the bounding box) failed 5 of 8 (the slivers need 15 to 17 pages where it gives 257 or 513); the control s22 needed 78 again"
unit = "dpm"
method = "r8-ldpm (render/closing-r8-ldpm), round 8's session L1 of round 7's leftovers (decision R8-8: safe class only, no held reset, no planned fault; plan closing8/leftovers/exp-leftovers-r8.md section 2), built on the session kit (resgx545 main 91f21da, data ca742f30e) and frozen before the run (FROZEN.sha256 3d2ef2ec..., kept as FROZEN.pre-fix.sha256; PREDICTIONS.sha256 24320c29...), dataset render-closing-r8-ldpm; attempt out/20261113-021431, run by the lead with the kit's driver (log run-r8l.log), 2026-11-13 from 02:14:31 Mac time, on the laptop, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls gate every later stage (they passed); no stop, fault, hang or lead decision. Every prediction came from the frozen OL7 tables (closing8/leftovers/ol7_c_tables.py, which loads E874's f5lib, E900's g3_span, F9's f9_loss and HU1 from their published copies hash-checked, ol7_tables.json sha256 ba59dc3a... in FREEZE-ol7c.sha256, written before L1 was built; its first run was stopped for speed with no output and its second run's k cells were refused at the build for up to 34 partial renders). The frozen scorer (score/score.as-run.py) re-run on the kept files gave output byte-identical to the kept score files in 7 of 7 stages; one post-run fix (POSTRUN-FIX.md: stage k's calibrations ended rc 1 with their diff line and were read as not completed). Post hoc (after the scores were read): postrun/misses.py and its output read every row. Stage k's five calibrations (P 0x422, the 2048x2048 ones dumped; their cells are E938). Stage u (9 jobs: the control u-c-s22, R7-dpm s-b's b-cal-s22 command, need 78; eight shapes at P 0x422: u-full-1024 and u-full-2048 (a triangle twice the target, covering it), u-sliver and u-anti-2048 (8 pixels wide along each diagonal of 2048x2048), u-small20 (a 20-pixel triangle), u-band40 (40 pixels high across 4096x2048), and the slivers of 4096x2048 and 2048x4096 picked by ol7_c_tables.py where HU1 and H-BBOX part most, every U below 0x3f0 under both)"
tiers = ["HW"]
date = "2026-11-13"
data = ["render-closing-r8-ldpm:out/20261113-021431/k/", "render-closing-r8-ldpm:out/20261113-021431/u/", "render-closing-r8-ldpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** HU1 (E773) gives the page need of scenes of the tool's triangle and had been held
out on 26 scenes of one or more triangles in one kick (E773, E863, E883, E916). Stages k and u
held it out on scenes of several kicks (`--geometry`) and on triangles of other shapes given by
their vertices in 1/4096 pixel, with a rival that streams every region of the bounding box.

**Frozen verdict (as printed).** `out/20261113-021431/score-u.txt`: "u: HU1: HU1 holds (16 of 16
rows decided)", "u: H-BBOX: H-BBOX holds is not supported: 3 held, 5 FAILED, 0 cannot tell of 8",
the control PASS. `score-k.txt`: "k: HU1: cannot tell: no row decided", the calibrations ending
rc 1 with their diff line (POSTRUN-FIX.md); `score-k.fixed.txt`: "k: HU1: HU1 holds (10 of 10
rows decided)".

**Results [HW].** Needs (the peak of 0x0724 of a job with no partial render) against HU1: k22-n2
108, k22-n3 131, k22-n4 136, k44-n2 377, k44-n4 492, each HU1's; u-full-1024 49, u-full-2048
257, u-sliver 15, u-anti-2048 15, u-small20 2, u-band40 11, u-sliver-4096x2048 15,
u-sliver-2048x4096 17, each HU1's. H-BBOX equals HU1 where the bounding box is the triangle's
coverage (the full-target triangles, the 20-pixel one) and fails on the slivers and the band
(257, 257, 513, 513 and 13 pages predicted).

**What it shows.** The page need of a scene is HU1 of the regions its triangles list, whatever the
shape and however many kicks build the scene: 13 of 13 held out here, 39 with the earlier ones.
`dpm.rs` gives it (`scene_page_need`).

**What it does not show.** The need of wide scenes of many vertices (E630's 300 to 900 vertices),
which the 1500-vertex scene's replay gives only up to the clamp; the count of multi-kick scenes
(E938).
