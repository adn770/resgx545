+++
id = "E753"
claim = "At 4096x4096 with the green pixel program, the TA's threshold was raised by 0x20 (TA3DCtl dword 38 = 0x20, dword 37 = 1 << 16 | thr0) in all 6 ladder jobs at P = 0x320, 0x340 and 0x360 (1350 and 1500 vertices each; thr0 = P - 0x22 = 0x2fe, 0x31e, 0x33e) and in none of the 8 jobs at P = 0x380, 0x3a0, 0x3c0 (1350 and 1500 each; thr0 0x35e, 0x37e, 0x39e) and 0x3e0 (1350 and 1380; thr0 0x3be), all 14 of which had a second run that reached thr0; the step is at the same P for both scenes, last raise 0x360 and first silent 0x380, so the limit C of the raised threshold (raise iff thr0 + 0x20 <= C) lies in [0x35e, 0x37e), inside the S1 post-hoc bound [0x2fe, 0x3de): the frozen held-out verdict HP1 (one step for both scenes), with both controls passing (c-1500-0x422 no raise, p-1350-0x300 raise, each as in S1); the job's own register 0x0624 read P - 0x22 in 16 of 16 jobs (0x400 at 0x422)"
unit = "dpm"
method = "S1b stage g-e1 of the question-closing pass (16 jobs, one condition each; paths relative to render/closing-s1b/ of the dataset: probe --tri pixel --width 4096 --height 4096 --vertices V --dump-render with the plain green pixel program p1139-green, render_pb_pages written, read back and marked in the kernel log before each job, a debugfs reset before each, regtimeline over 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748, read-only), on the laptop (direct cable), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71, built from main), tables, predictions, scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256, TABLES.md; verified before each stage); scored by the frozen score/score_s1.py g-e1 (out/score-g-e1.txt; re-run from the dataset with the same output); the stage ran third in the session's order (p-b2, g-e8b, g-e1, g-e3, p-c, g-e5, p-d stopped, p-f, g-e4w); a job's raise is read from dword 38 of the TA/3D control block dump (buf09) after the job, the knob proof from the job's own 0x0624 rows (the first timeline row is the previous job's)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/g-e1/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E734 (S1) saw the raise at P = 0x300 and 0x200 and at no P from 0x3e0 up, with its
frozen positive control failing, and read post hoc a limit C on the raised threshold between 0x2fe
and 0x3dd (HP1) or a rule in P alone. S1b froze that reading as HP1 (one step in P for 1350 and
1500 vertices, a raise below a P* and none from P* on) against HPS (monotone in P for each scene,
the step differing by scene), with the controls taken only from jobs already measured under the
same words: c-1500-0x422 (E704's job, no raise) and p-1350-0x300 (S1's raise). The ladder is
P = 0x320 to 0x3c0 in steps of 0x20 for 1350 and 1500 vertices (12 jobs), plus 1350 and 1380
vertices at 0x3e0 for the dword-36 step S1 read post hoc.

**Frozen verdict.** `HP1: one step for both scenes, last raise 0x360, first silent 0x380: C in
[0x35e, 0x37e) inside [0x2fe, 0x3de); dword 36 at 0x3e0 (S1 post hoc): s-1350-0x3e0 2 (frozen 2),
s-1380-0x3e0 3 (frozen 3)` (out/score-g-e1.txt). Both controls held, every ladder cell was usable
(second run reaching thr0, two or three partial renders) and each scene showed exactly one flip,
raise to no raise, between neighbouring cells. The ladder rows are the held-out part; the two
rows at 0x3e0 are S1 post-hoc readings frozen and run again (the scorer prints them as such), so a
repeat and not held out.

**Results [HW].** All 16 jobs: rc 3 with "scene overflowed the parameter buffer, context kept",
the kernel log clean, the health triangle after the stage fine. The job's own 0x0624 (read from the
rows of the job's runs; the first row of the file is the previous job's) was P - 0x22 in all 16:
0x2de at P = 0x300, then 0x2fe, 0x31e, 0x33e, 0x35e, 0x37e, 0x39e and 0x3be at 0x320 to 0x3e0, and
0x400, the clamp, at 0x422.

| P | thr0 | 1350 vertices | 1500 vertices |
|---|---|---|---|
| 0x300 | 0x2de | raise (control; dwords 35, 37, 38 = 0x2fc, 0x102de, 0x20) | not run |
| 0x320 | 0x2fe | raise (0x31c, 0x102fe, 0x20) | raise (same words) |
| 0x340 | 0x31e | raise (0x33c, 0x1031e, 0x20) | raise (same words) |
| 0x360 | 0x33e | raise (0x35c, 0x1033e, 0x20) | raise (same words) |
| 0x380 | 0x35e | none (dword 35 = 0x35c, 37 and 38 = 0) | none |
| 0x3a0 | 0x37e | none (0x37c) | none |
| 0x3c0 | 0x39e | none (0x39c) | none |
| 0x3e0 | 0x3be | none (0x3bc; also 1380 vertices) | not run |
| 0x422 | 0x400 | not run | none (control; 0x3fe, 3, 0, 0, 6 as E704) |

The raised jobs read dword 38 = 0x20 and dword 37 = 1 << 16 | thr0 as in E734, and dword 35 = thr0
- 2 in every job. The vertex count did not move the step: at each P of the ladder both scenes
gave the same outcome.

Dword 36 (E734: 2 at 1350 vertices, 3 at 1380 to 1500) at 0x3e0 read 2 at 1350 and 3 at 1380, as
frozen (the S1 post-hoc step reproduced, once each). Across the ladder it is not a function of the
vertex count: 1350 read 2, 2, 3, 2, 2, 2 and 1500 read 1, 1, 3, 2, 3, 3 at P = 0x320, 0x340,
0x360, 0x380, 0x3a0 and 0x3c0, so at 1500 vertices the 3 of E630 and E704 is one of several
values over P (and 1 below 0x360).

**Post hoc (read after the run; [infer], not held out).** The raise is a threshold test: the
second abort, at thr0 + 0x20, happens when that value is at most a limit C, and C lies in [0x35e,
0x37e) for both scenes. That reading is the one the frozen HP1 states; the data here fix the
interval by one flip per scene, it does not say what the limit is. E704's 1500-vertex scene at P
from 0x422 up does not raise because the clamp keeps thr0 at 0x400, so thr0 + 0x20 = 0x41e is far
above C; it is not an exception to the rule for 1500 vertices. A rule that does not depend on the
vertex count fits all 16 jobs; E625's overflow-and-reach condition alone does not give the step,
every non-raising ladder job having reached thr0 (parts 2 or 3).

**Not shown.** What the limit compares (the page count, a register, a firmware constant), why the
increment is 0x20, whether the limit is the hardware's or the firmware's, whether it depends on
the target size or the other settings (one target, 4096x4096, one pixel program), a ladder finer
than 0x20 (C is known to 0x20), vertex counts below 1350, and what dword 36 counts (it moves with
P at 1500 vertices).

**Correction 2026-11-10:** The "1, 1, 3, 2, 3, 3 over P" of dword 36 is read post hoc (a fit on
data measured before the reading, not a test) as the page count of the global list at the first
abort, less 2, saturating at 0, and not as a function of the vertex count alone. [data] Across 150
jobs with a control block and a TA-data dump (S1 g-e1 22, S1b g-e1 16, E630's wd-glist 5, E704's
dpm-oom 8, E625's triangle jobs 99) dword 36 equals max(g - 2, 0), g the pages of the global list
in the dump, in all 99 jobs that did not raise (g = 1 gives 0 in 54, g = 2 gives 0 in 3, g = 4
gives 2, g = 5 gives 3); the jobs where it differs from g - 2 are the raised ones (9 of 9 in S1 and
S1b, 77 in E625's data), as E627 explains: after a raise the state page holds the lists the TA built
after the last partial render. [infer] So dword 36 is the global list's page count at the first
abort less 2 (E310's firmware reading, the count of `CR_DPM_GLOBAL_PAGE_STATUS` less 2, with a
floor), and the global list's pages hold the objects (packed vertices in the walked pages of the
1500-vertex list, streams in the macrotile pages): the step between 1350 and 1380 vertices is one
more object page at that threshold. This corrects the wording "dword 36 moves with P" as a
property of P: what moves is how far the scene had got when the threshold hit. The 99 of 99 is a
fit; the held-out part is the raised jobs, which a sample of `CR_DPM_GLOBAL_PAGE_STATUS` (0x072c,
glossary G0828) during them would score. It was sampled before (E256, E312, E358: 0x10001 through
renders and a 1024x768 partial render, 0 after the jobs in E438) but in none of this record's or
S1's g-e1 jobs, whose timelines cover 0x0720 to 0x0724. The counts come from
scratch scripts (dw36_glist.py, dw36_tri.py, closing2/geometry) that read the published dumps and
are not in the repository.
