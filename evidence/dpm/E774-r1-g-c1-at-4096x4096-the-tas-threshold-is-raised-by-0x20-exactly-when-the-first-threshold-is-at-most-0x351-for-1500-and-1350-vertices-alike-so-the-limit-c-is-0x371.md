+++
id = "E774"
claim = "R1-pixgeo stages g-c1 and g-c1f (23 jobs at 4096x4096 with 1500 vertices, 5 of them also with 1350, the tool's triangle and p1139-green, the first threshold thr0 = P - 0x22 set by render_pb_pages and proved by the job's own 0x0624 in 23 of 23): along P the TA's threshold was raised by 0x20 (dword 38 = 0x20, dword 37 = 0x10000 | thr0, the second run reaching thr0 + 0x20) at every cell from P = 0x360 to 0x373 and not at 0x374 to 0x380, one flip and no other, so the raise happens iff thr0 + 0x20 <= C with C = 0x371 (thr0 at most 0x351) for this scene and target; the controls reproduced E753 (raise at 0x360, none at 0x380), HP1 held (each of the 5 cells of 1350 vertices, P = 0x366, 0x36e, 0x372, 0x376 and 0x37a, gave the outcome of the 1500 cell at that P, 5 of 5, held out), and the frozen verdict was H-abs holds with the last raise 0x372, the first silent 0x374 and C in [0x370, 0x372), the step-1 cell 0x373 (g-c1f, run after the verdict) raised and fixed C in [0x371, 0x372); the ladder moves P and the threshold together, so a limit tied to P is not separated from a constant C by it"
unit = "dpm"
method = "R1-pixgeo stage g-c1 (22 jobs: the controls c-1500-0x360 and c-1500-0x380, 15 cells f-1500-0x362 to 0x37e at 1500 vertices in steps of 2, 5 cells f-1350-0x366, 0x36e, 0x372, 0x376 and 0x37a) and stage g-c1f (the one cell f-1500-0x373, chosen after the verdict from the 16 frozen candidates and run at 09:55:44) of the question-closing pass, round 2 (decision R2-14), dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:44 laptop time (08:44 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width 4096 --height 4096 --vertices V --dump-render with p1139-green, the knob render_pb_pages written to P and read back, regtimeline 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x072c (the gate had passed) and 0x0748, a debugfs reset before each job, all 23 of class ok (rc 3 'scene overflowed'); the knob proof per job the job's own 0x0624 rows (P - 0x22, never the first sample); the raise read from the control block (dword 38 = 0x20 and dword 37) and from the run peaks of 0x0724 (a cell whose second run does not reach thr0 would be void: none); frozen predictions from E753's controls and range ([0x35e, 0x37e)) with H-abs (one flip along P), HP1 (1350 as 1500) and the step-1 cell chosen by the flip; scored by the frozen score/score_r1.py g-c1 and g-c1f (out/score-g-c1.txt, out/score-g-c1f.txt), re-run on the kept files with the same SUMMARY lines; the check of earlier data against C was made after the run by hand"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-c1/", "render-closing-r1-pixgeo:out/g-c1f/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E753 found the TA's threshold raised at P = 0x320 to 0x360 and not at 0x380 to 0x3e0,
for 1350 and 1500 vertices alike, so a limit C on thr0 + 0x20 lay in [0x35e, 0x37e). The stage is
the fine ladder in steps of 2 across it (15 cells of 1500 vertices and 5 of 1350), the controls of
E753 first, and one step-1 cell after the flip.

**Frozen verdict.** `H-abs holds: one flip, last raise 0x372, first silent 0x374: C in [0x370,
0x372) (inside [0x35e, 0x37e)); the step-1 cell 0x373 (g-c1f f-1500-0x373) fixes C exactly;
HP1: 5 of 5 1350 cells equal the 1500 cell at that P; D36 unraised 6/9, raised 0/13`, and for the
cell `step-1 cell: f-1500-0x373: raise: C in [0x371, 0x372)`. The D36 part is E775's.

**Results [HW].** 1500 vertices: raise at P = 0x360 (control), 0x362, 0x364, 0x366, 0x368, 0x36a,
0x36c, 0x36e, 0x370, 0x372 and 0x373; none at 0x374, 0x376, 0x378, 0x37a, 0x37c, 0x37e and 0x380
(control). 1350 vertices: raise at 0x366, 0x36e and 0x372; none at 0x376 and 0x37a. Each job's
0x0624 read P - 0x22 (0x33e at P = 0x360 up to 0x352 at 0x374), and every job's second run reached
its first threshold. In the raised jobs the run peaks were thr0, thr0 + 0x20 and a lower third
(for P = 0x373: 0x351, 0x371, 0x23d), dword 37 = 0x10000 | thr0 (0x10351) and dword 38 = 0x20; in
the others the second peak equalled thr0 (0x352, 0x352, 0x352 at P = 0x374) and dwords 37 and 38
were zero. So at this scene and target the TA's threshold is raised by 0x20 iff thr0 + 0x20 <= C =
0x371 (881 pages), i.e. thr0 <= 0x351 (849): the last raised threshold the hardware accepted is
0x371, the first it refused 0x372.

**Read against earlier data after the run [infer; a check, not frozen].** E753's ladder (raises at
P = 0x320 to 0x360, none from 0x380), E734's raises (1350 vertices at P = 0x300, 900 at 0x200) and
none from 0x3e0, E704's 1500 vertices at P = 0x422 and above (thr0 clamped at 0x400, thr0 + 0x20 =
0x420, above C) and E625's default-triangle raises (thr0 at most 0x100) are all on the side of C
their thr0 puts them.

**What it shows and does not.** C is exact for the 4096x4096 target, 1350 and 1500 vertices of the
tool's triangle (HP1 held out: the limit does not depend on the vertex count there). The ladder
moves P and thr0 together (thr0 = P - 0x22), so a limit tied to P (the proposal's H-rel, C = P - 2 -
d) gives the same flip; telling a constant of the core or the firmware from a limit that follows
the knob needs the descriptor poke of the proposal's C2 (a threshold set without P), which did not
run, and the scorer's 'H-abs holds' says only that the outcome flipped once, in one direction. What
the DPM compares with C, why the increment is 0x20, and whether C moves with the target (C3 at
2048x2048 did not run) stay open (Q210).
