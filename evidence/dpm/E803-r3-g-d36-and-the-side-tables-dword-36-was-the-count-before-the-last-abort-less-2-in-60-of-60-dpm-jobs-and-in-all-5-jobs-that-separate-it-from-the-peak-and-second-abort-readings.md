+++
id = "E803"
claim = "R3-geo, H-last (dword 36 of the TA/3D control block = the low-half count of CR_DPM_GLOBAL_PAGE_STATUS, 0x072c, in the sample before the LAST abort, less 2, floor 0; a reading chosen after R1's and R2's data, frozen before this run as held out): in g-d36, the stage that gates on it (6 jobs at 2048x2048 thr0 0x60, 0x70, 0x90 and 0xb0 and 4096x4096 thr0 0x2c0 and 0x300, three to six aborts each), H-last HOLDS, 6 of 6 jobs and all 3 jobs that separate it from the peak and second-abort readings (d36-2048-0x90, d36-4096-0x2c0 and d36-4096-0x300: counts 2, 4, 3 or 3, 4, 3, dword 36 1); in the never-gating side tables of the other DPM stages it fitted g-c4 10 of 10 (1 separating, c3-2048-0xe2), g-c5 33 of 33 (none separating), g-c6 4 of 4 (none) and g-c7 7 of 7 (1 separating, c7-cal: counts 3, 3, 4, dword 36 2): 60 of 60 jobs, 5 of 5 separating; in no job did the count change between the two samples before the last abort"
unit = "dpm"
method = "R3-geo stage g-d36 of the question-closing pass, round 3 (session L1, decision R3-G3; sixth of nine stages, 6 jobs, the tool's triangle with 1500 vertices, p1139-green, P = thr0 + 0x22), and the side table of every DPM job of g-c4, g-c6, g-c5 and g-c7, dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, g-d36 started 15:52:38 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --tri pixel --width W --height H --vertices 1500 --dump-render (g-c7 with --tri-full), regtimeline 0x0720-0x072c among the registers, a debugfs reset before each job, g-d36's 6 of class ok (rc 3); the counts are the low half of 0x072c in the timeline sample just before each rising edge of 0x0658 bit 0, dword 36 read from the control block after the job (buf09); the H-last table, the separating column (H-last's value differs from the peak reading's or the second-abort reading's, PREFLIGHT deviation 3) and the verdicts are the frozen score/score_r3.py's (out/score-g-d36.txt and the side tables of out/score-g-c4.txt, -g-c5.txt, -g-c6.txt, -g-c7.txt), labelled heldout in predictions/; the totals over the five stages are a sum of the printed lines"
tiers = ["HW"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-d36/", "render-closing-r3-geo:out/g-c4/", "render-closing-r3-geo:out/g-c5/", "render-closing-r3-geo:out/g-c6/", "render-closing-r3-geo:out/g-c7/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl"]
+++
**What ran.** E775 and E790 refuted two readings of dword 36 as rules (the count at the first
abort less 2, and the job's peak count less 2). A dated note on Q273, made before this run, read
ten candidates on the existing jobs and found the count before the last abort, less 2, fitting 49
of 49 jobs with an abort, chosen after the ten were seen and with only two jobs separating it from
the peak and second-abort readings. It was frozen as a held-out side table in every DPM job of
this session, and g-d36 ran six jobs at low thresholds so that three or more aborts with differing
counts would separate the readings; g-d36 gates on it (H-last holds only if all separating jobs
fit, and at least 3 must separate).

**Frozen verdicts (as printed).** g-d36: `controls pass (g-c4's); H-last HOLDS: all 3 separating
jobs fit (6 of 6 jobs); usable jobs 6 of 6`. Side tables: g-c4 `H-last: 10 of 10 jobs fit;
separating jobs 1 of 1; jobs whose count changed in the two samples before the last edge: 0`; g-c5
`33 of 33 ... separating jobs 0 of 0 ... 0`; g-c6 `4 of 4 ... 0 of 0 ... 0`; g-c7 `7 of 7 ...
separating jobs 1 of 1 ... 0`.

**Results [HW].** g-d36:

| job | thr0 | partial renders | counts before the aborts | peak | dword 36 | separating |
|---|---|---|---|---|---|---|
| d36-2048-0x60 | 0x60 | 6 | 2, 3, 3, 3, 3, 3 | 3 | 1 | |
| d36-2048-0x70 | 0x70 | 6 | 2, 3, 3, 2, 2, 3 | 3 | 1 | |
| d36-2048-0x90 | 0x90 | 3 | 2, 4, 3 | 4 | 1 | yes |
| d36-2048-0xb0 | 0xb0 | 3 | 3, 4, 4 | 4 | 2 | |
| d36-4096-0x2c0 | 0x2c0 | 3 | 3, 4, 3 | 4 | 1 | yes |
| d36-4096-0x300 | 0x300 | 3 | 3, 4, 3 | 4 | 1 | yes |

All six raised the threshold by 0x20 (peaks thr0, thr0 + 0x20). The separating jobs of the side
tables: c3-2048-0xe2 of g-c4 (counts 3, 4, 3; peak 4; dword 36 1, R2's separating job run again)
and c7-cal of g-c7 (counts 3, 3, 4; peak 4; dword 36 2). The jobs without an abort (c5a-cal,
c6-cal) read dword 36 = 0; c5b-cal and c5c-cal had one abort at count 7 and read 5. The g-c7 cells
with 13 to 67 aborts had counts of 1 and 2 and read 0. Every job's row is in the score files.

**What it shows and does not.** Over these 60 jobs (the tool's triangle at 2048x2048, 4096x4096,
4096x2048, 2048x4096 and 3072x3072, a 2048x2048 target in a 4096x4096 context, and `--tri-full` at
2048x2048), dword 36 is the 0x072c count in the sample before the last abort less 2, floor 0, and
0 without an abort; the five jobs where that differs from the peak and second-abort readings all
followed it, three of them in the stage that gated on it. It is a reading of the register over the
job, held out; what the firmware computes it from (the register, the global list's pages or a count
of its own) is not read here, and every scene is one of the tool's two triangle scenes.

**Correction 2026-11-11:** "60 of 60 jobs" counts two jobs that cannot fail the reading. c5a-cal
(g-c5) and c6-cal (g-c6) had no abort; the frozen scorer's H-last table reads the count before the
last abort of a job with no abort as 0, and both read dword 36 = 0, so each row prints "ok"
(`score-g-c5.txt` and `score-g-c6.txt` of the dataset) without testing the count before the last
abort. Right: H-last held in 58 of 58 jobs with an abort (g-d36 6 of 6, g-c4 10 of 10, g-c5 32 of
32, g-c6 3 of 3, g-c7 7 of 7), and the two jobs without one read 0 as the reading's "0 without an
abort" says. The 5 separating jobs (d36-2048-0x90, d36-4096-0x2c0, d36-4096-0x300, c3-2048-0xe2
and c7-cal) are unchanged, and so is the verdict of g-d36, the stage that gated on it.

**Correction 2026-11-11:** This adds a reading of the firmware that writes the word, made offline in
round 4 (reading R-5, `closing4/p7/reading-r5.md`, with `flips.py`, `flips.out`, `guard.py` and
`sweep_last.out` beside it), and leaves the claim as is. [source, static, plus data] The routine
writes dword 36 at every abort as the high half of `CR_DPM_GLOBAL_PAGE_STATUS` less 2, floored at 0
(0xc0e-0xc11), and dword 35 as the high half of `CR_DPM_PAGE_STATUS` less 2 masked to 16 bits
(0xc17-0xc19), nowhere else in the routine. Against the kept timelines and each job's buffer, the
rule (the value at the last abort less 2, floor 0) equals dword 36 in 107 of 107 jobs of the DPM
stages, which extends this record's 60 of 60, and dword 35 follows PS_hi the same way. [infer] The
sample-time uncertainty this record bounds is the same one the reading rests on.
