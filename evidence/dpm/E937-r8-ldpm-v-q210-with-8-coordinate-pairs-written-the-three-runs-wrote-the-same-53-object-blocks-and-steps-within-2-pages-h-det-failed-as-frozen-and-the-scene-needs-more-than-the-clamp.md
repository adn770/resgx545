+++
id = "E937"
claim = "r8-ldpm stage v on module 37EC97AB (Q210, larger objects): the tool's 1500-vertex triangle with --vtx-coords 8 and our vertex program vtx_coord8.s writing o4 to o11 (plan P3: the default program leaves those outputs unwritten) ran three times; the frozen verdict of H-DET (the three give the same steps, need and object block sizes) is 'not supported', 0 held, 3 FAILED of 3: S5 read 0x15e, 0x15c, 0x15e and S10 0x373, 0x371, 0x371, every other step S2 to S11 the same, while read after the run the three dumps hold the same 53 object blocks (sizes 193, 190, 187, 197, 137, ...) and each run took one partial render at the 0x400 clamp (the scene needs more); the N 4 control (R7-dpm's v-cal-c4) repeated 14 of 14, the written N 4 runs gave the plain N 4 scene (100 blocks of 127 dwords, the same 12 steps and need 538) and the two plain N 8 runs the same 94 blocks and need 608 as each other"
unit = "dpm"
method = "r8-ldpm (render/closing-r8-ldpm), round 8's session L1 of round 7's leftovers (decision R8-8: safe class only, no held reset, no planned fault; plan closing8/leftovers/exp-leftovers-r8.md section 2), built on the session kit (resgx545 main 91f21da, data ca742f30e) and frozen before the run (FROZEN.sha256 3d2ef2ec..., kept as FROZEN.pre-fix.sha256; PREDICTIONS.sha256 24320c29...), dataset render-closing-r8-ldpm; attempt out/20261113-021431, run by the lead with the kit's driver (log run-r8l.log), 2026-11-13 from 02:14:31 Mac time, on the laptop, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0; loaded = installed, the kit's preflight at each stage), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558..., source resgx545 4623753) run under ~/regtimeline (sha256 079f6359...) sampling R5-dpm's 16 registers, the debugfs knob render_pb_pages written per row to P = thr0 + 0x22, read back and restored to 0x422, a debugfs reset and the kit's health check around each job; stage a0's six controls gate every later stage (they passed); no stop, fault, hang or lead decision. Every prediction came from the frozen OL7 tables (closing8/leftovers/ol7_c_tables.py, which loads E874's f5lib, E900's g3_span, F9's f9_loss and HU1 from their published copies hash-checked, ol7_tables.json sha256 ba59dc3a... in FREEZE-ol7c.sha256, written before L1 was built; its first run was stopped for speed with no output and its second run's k cells were refused at the build for up to 34 partial renders). The frozen scorer (score/score.as-run.py) re-run on the kept files gave output byte-identical to the kept score files in 7 of 7 stages; one post-run fix (POSTRUN-FIX.md: stage k's calibrations ended rc 1 with their diff line and were read as not completed). Post hoc (after the scores were read): postrun/misses.py and its output read every row. Stage v (14 jobs, all at 2048x2048 with --dump-render: the control v-c4, --vtx-coords 4 at P 0x422, R7-dpm s-v's v-cal-c4; --vtx-coords 8 with --slot vtxuse=vtx_coord8.bin three times (held out, H-DET); --vtx-coords 4 with vtx_coord4.bin twice and six cells around its S4 and S5 (explore); plain --vtx-coords 8 twice (explore)). vtx_coord8.s is the session's (asm/, assembled with tools/usse-asm, run to its emit in sgx-sim with o0 to o11 written); OL7 (a), offline before the build (closing8/leftovers/ol7_a_dumps.py, FREEZE-ol7a.sha256), had held P3-DUMP: R6-dpm's and R7-dpm's N 4 calibration dumps hold the same 100 object blocks and their N 8 dumps no block alike. Object block sizes read from the dumps as OL7 (a) reads them (score/score.py blocks, the readers loaded from their pinned blobs)"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r8-ldpm:out/20261113-021431/v/", "render-closing-r8-ldpm:postrun/", "cited-scratch:closing8/leftovers/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS"]
+++
**What ran.** E917 found that the same `--vtx-coords 8` command gave other object blocks, steps and
need in R7-dpm than in R6-dpm. The tool's option only widens the vertex and the TA's outputs; its
default vertex program writes o0 to o3, so the extra outputs hold whatever they held (plan P3
[infer], held offline by OL7 (a) on the published dumps). Stage v wrote every extra output with
our own vertex program and froze H-DET: three runs give the same steps, need and block sizes.

**Frozen verdict (as printed).** `out/20261113-021431/score-v.txt`: "v: H-DET: H-DET holds is not
supported: 0 held, 3 FAILED, 0 cannot tell of 3"; the control v-c4 PASS.

**Results [HW].** The three written N 8 runs (v-w8-1 to 3): one partial render each at thr0 0x400
(the clamp: no need read), the second run peaking at 0x3c4; the steps S2 to S11 `0x4f`, `0xd3`,
`0x124`, S5, `0x1f3`, `0x24a`, `0x29f`, `0x319`, S10, `0x3de` with S5 `0x15e`, `0x15c`, `0x15e`
and S10 `0x373`, `0x371`, `0x371`. The control repeated R7-dpm's 14 readings (S2 to S13, need 538).
Explore: the written N 4 runs read the control's 12 steps and need 538; the six written N 4 cells
took one partial render each; the plain N 8 runs read 17 steps (S2 `0x4f` to S18 `0x21b`, S9 `0xee`
and `0xed`) and the need 608 (`0x260`) both times.

**Read after the run (post hoc).** `postrun/misses.out`: the three written N 8 dumps hold the same
53 object blocks, size by size (193, 190, 187, 197, 137, 175, 184, 197, ...); the two plain N 8
dumps the same 94 blocks as each other (187, 187, 196, 189, 127, ...), the count R7-dpm's had,
with sizes in another order than R7-dpm's and R6-dpm's (E917); the written N 4 dumps the plain
scene's 100 blocks of 127 dwords. The step brackets of the written runs overlap where their
values differ (S5 `[0x15b, 0x15e]`, `[0x15a, 0x15c]`, `[0x15b, 0x15e]`; S10 `[0x36f, 0x373]`,
`[0x371, 0x371]`), so the frozen point comparison is stricter than the sampling [infer].

**What it shows.** With the extra outputs written the TA writes the same object blocks in each run,
and with them unwritten the two runs of one session did too: E917's run-to-run difference is
between sessions, as P3 says the unwritten outputs vary [infer]. The steps of the written scene
repeat within the sampling, but H-DET as frozen (exact step values) failed.

**What it does not show.** A step rule for blocks larger than 67 dwords (E874's replay assumes 67);
the need of the written N 8 scene, which exceeds the 0x400 clamp; why the unwritten outputs differ
between sessions.
