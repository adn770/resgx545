+++
id = "E860"
claim = "R5-dpm stages d-a0 and d-a1 on the rgn4 module (Q210; 2048x2048 and 4096x4096, the tool's triangle with 1500 vertices, thr0 = P - 0x22 read back from the job's own 0x0624, 16 registers sampled with 0x0734, 0x0730, 0x012c and 0x0a74 in place of four that read 0 in every kept DPM timeline): the premise held, 29 of 29 rows (the two calibrations stepped the global page count at E852's S2 to S5 = 0x51, 0x9d, 0xe8, 0x132 at 2048x2048 and 0x125, 0x240, 0x35b at 4096x4096, with no grow; the six kept flip cells repeated, thr0 0xe2 and 0xc0 raised and 0xe3, 0x100, 0x35a and 0x35c did not); then c4-b3 (P 0x10a, thr0 0xe8 = S4) grew the TA's global list before its first abort in 5 of 5 repeats, with 0x0734 bit 0 clear before the grow in 5 of 5, and stayed silent in 5 of 5, while the four cells around it (thr0 0xe7, 0xe9, 0xe4, 0xf0) grew in none and were silent: the frozen verdict is H-GREQ held on its fit side (5 of 5, neighbours 4 of 4) and H-NOISE (at most 1 grow in 5) refuted"
unit = "dpm"
method = "R5-dpm stages d-a0 (8 jobs, controls) and d-a1 (9 jobs: c4-b3 five times, the FIT side of H-GREQ, interleaved with S4 - 1 and S4 + 1 read by the runner from a0-cal-2048's own timeline, c4-b4 and c4-b2) of the question-closing pass, round 5 (decisions R5-3 a, R5-4 a, R5-5 a; plan closing5/dpm/exp-dpm-r5.md sections 2 and 4), dataset render-closing-r5-dpm, on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (rgn4), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558...), probe --tri pixel --vertices 1500 with p1139-green, a debugfs reset before each job. Attempt 1 (freeze 1) ran a0-cal-2048 and a0-cal-4096 at 09:28 Mac time and stopped by its frozen premise rule (rc 10: a0-cal-4096's own 0x0624 not read) because the laptop's /tmp (tmpfs, 991M), where the runner's work directory sat, was full: the TA-data dump ended on a short write (--dump-render: Input/output error), the job text was cut at 4096 bytes and buf09, regs and the kernel-log slice were not kept (out/d-a0, run-r5d.log). The lead stopped there, confirmed /tmp at 100% with 14 leftover runner work directories of earlier sessions and removed them; the builder refroze the measurement path only (the work directory on the kept files' filesystem, a 200 MB check per job, a whole-capture check before any reading, --dump-render on the 2048x2048 rows only; predictions byte-identical, PREDICTIONS.sha256 unchanged; README.md, Freeze 2). Attempt 2 (freeze 2, out/a2) ran d-a0 at 09:40:32 and d-a1 at 09:41:45, health ok after each. Scored by the frozen score/score_r5.py (scorekit of resgx545 f0d5b39): a grow is 0x0628's low half below 0x10 between 0x0720 leaving 0 and the first 0x0658 = 1, a raise dword 38 = 0x20 in after.buf09, S_k the count of 0x0724 before global page k appears (rule max(a, b - 1), PREFLIGHT deviation 1). The scorer re-run at the fold on the kept files printed output byte-identical to score-d-a0.txt and score-d-a1.txt. Post hoc (read after the run from the runner's reading lines in out/a2/d-a1.log, not scored): the global page count at the last in-stretch sample of the first partial render"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-dpm:out/a2/d-a0/", "render-closing-r5-dpm:out/a2/d-a1/", "render-closing-r5-dpm:out/d-a0/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "ta3d_ctl"]
+++
**What ran.** E852 found, post hoc, that R-5's one miss (E799's c4-b3: 2048x2048, P `0x10a`,
thr0 `0xe8`, silent with the inputs of the raised c4-b5) is the only kept job whose first threshold
lands on a step S_k of the global page count and the only TA run with the global list grown before
an abort, and the planner froze H-GREQ (the first entry grows the list iff thr0 = S_k) against
H-NOISE (a one-off) for this session (`closing5/dpm/exp-dpm-r5.md` section 2). Stage d-a0 checked
the premise on the rgn4 module with the new register list; d-a1 repeated c4-b3 five times between
four cells around it. Attempt 1 stopped in d-a0 on a full `/tmp` (method); its two jobs are kept in
`out/d-a0` and are not a reading.

**Results [HW, frozen verdict].** d-a0 (`out/a2/score-d-a0.txt`): "the premise holds on rgn4
(steps of section 1, the four flips, no grow, knob proof) (29 of 29 rows decided)". The steps read
`0x51`, `0x9d`, `0xe8`, `0x132` (a0-cal-2048, P `0x162`) and `0x125`, `0x240`, `0x35b`
(a0-cal-4096, P `0x422`), E852's table; c4-b5 (`0xe2`) and c3-2048-0xe2 (`0xc0`) raised, c4-b6
(`0xe3`), c3-2048-0x122 (`0x100`) and the 4096x4096 cells `0x35a` and `0x35c` did not; no grow.

d-a1 (`out/a2/score-d-a1.txt`): "H-GREQ held (5 of 5); H-NOISE refuted (5 of 5); grows in the
replicates [True, True, True, True, True]; neighbours 4 held, 0 FAILED, 0 cannot tell of 4 |
silent (all 9): 18 held, 0 FAILED, 0 cannot tell of 18".

| job | thr0 | grow | `0x0734` bit 0 clear | raise |
|---|---|---|---|---|
| a1-rep1 to a1-rep5 (c4-b3) | `0xe8` | 5 of 5 | 5 of 5 | none |
| a1-s4m1, a1-s4p1 | `0xe7`, `0xe9` | no | - | none |
| a1-b4, a1-b2 | `0xe4`, `0xf0` | no | - | none |

**Read after the run [HW, post hoc].** The runner's reading of the global page count at the last
in-stretch sample of the first partial render is 1 in a1-rep1, rep3, rep4 and rep5 and 2 in a1-rep2,
with 3 global pages at the abort in all five; E852's kept c4-b3 read 2. With 1 R-5's guard places
the cell silent from the timeline alone; with 2 it does not (E861, E864).

**What it shows [infer].** c4-b3's grow is no one-off: a first threshold on S4 at 2048x2048 makes
the first out-of-memory entry take the list-kind branch (`0x0734` bit 0 clear, 3d.md §6.4) every
time, and one page either side does not. Its missing raise repeats too, so it is a property of the
cell, not a fault of the kept run. That rgn4 and the new register list change nothing the guard
reads is the premise's 29 rows.

**What it does not show.** Why the cell stays silent: H-PEND and H-BLOCK both predicted silence
here (they part at the raising-side steps, E861, and in `sa8`, E864). The repeats are the fit side
of H-GREQ: its held-out cells are E861's. Attempt 1's jobs are not used.
