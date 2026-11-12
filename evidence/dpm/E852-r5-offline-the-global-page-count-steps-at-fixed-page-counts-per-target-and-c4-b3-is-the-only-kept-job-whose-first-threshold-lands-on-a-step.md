+++
id = "E852"
claim = "Round 5 offline reading of the kept DPM timelines (Q210; post hoc, a FIT on one positive, nothing held out): in the first TA run of every kept job the high half of 0x072c (the global page count) steps at page counts of 0x0724 that are the same in every job of a target and scene, S_k being the count read before global page k appears: S2, S3, S4, S5 = 0x51, 0x9d, 0xe8, 0x132 at 2048x2048, 0x125, 0x240, 0x35b at 4096x4096 (1350 vertices as 1500 for S2 and S3), 0x97, 0x126, 0x1b9 at 4096x2048, 0x9a, 0x12c, 0x1be, 0x255 at 2048x4096 and 0xa9, 0x14d, 0x1ef, 0x293 at 3072x3072 (the tool's triangle, 1500 vertices), S4 lying 6, 10, 7, 8 and 7 pages above the last raise of E799, E774 and E801; of the 107 kept jobs with a partial render E799's c4-b3 (thr0 0xe8 = S4 at 2048x2048) is the only one whose first threshold equals a step, and the only one of 495 TA runs with the global list grown (0x0628) before an abort; two readings of its missing raise are named and not decided: H-PEND (the page the TA asked for is served after the resume read the count, so the guard is right and our resume count one page high) and H-BLOCK (the grow leaves a state that prevents the raise)"
unit = "dpm"
method = "Offline, no run (round 5, area dpm, decision R5-1 a: the plan's offline results land before any session; plan closing5/dpm/exp-dpm-r5.md sections 1 and 2). The planner's scripts closing5/dpm/gsteps.py, endstretch.py, allruns.py and run2.py (with tlc.py, standard library only) read the kept register timelines (the tool's output NAME.txt.gz, 16 registers sampled about every 8.4 us) and the buf09 control blocks of R3-geo g-c4, g-c5, g-c6, g-c7 and g-d36, R2-geo g-c3 and g-c2 and R1-pixgeo g-c1, g-c1f, g-u1 and g-u2 from resgx545-data, read-only; a partial render is a stretch of 0x0658 bit 0, the raise dword 38 = 0x20, a grow a sample of 0x0628 with its low half below 0x10 before the first abort. In the fold (2026-11-12) closing5/dpm/fold_s_hits.py pooled the steps of gsteps.out by target and scene and listed the jobs whose thr0 is within one page of one, and run2.py was run with the arguments c4-b3 c4-b5 c4-b6 c4-b2 to write run2.out (the planner kept no output of it). Every script was re-run from its published copy (resgx545-data cited/closing5/dpm/) and printed output byte-identical to the kept .out files. No frozen verdict: the table and the c4-b3 reading were read from data that had been seen (E799, E801, R-5's miss), so they are post hoc; H-GREQ, H-PEND and H-BLOCK were written by the planner after reading them, as predictions for a session that has not run"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r3-geo:out/g-c4/", "render-closing-r3-geo:out/g-c5/", "render-closing-r3-geo:out/g-c6/", "render-closing-r3-geo:out/g-c7/", "render-closing-r3-geo:out/g-d36/", "render-closing-r2-geo:out/g-c3/", "render-closing-r2-geo:out/g-c2/", "render-closing-r1-pixgeo:out/g-c1/", "render-closing-r1-pixgeo:out/g-c1f/", "render-closing-r1-pixgeo:out/g-u1/", "render-closing-r1-pixgeo:out/g-u2/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "ta3d_ctl"]
+++
**What was done.** R-5 (Q210's note of 2026-11-11, E799's correction) read the guard of the
firmware's + `0x20` write and placed 288 of 289 kept decisions; the one miss is c4-b3 (E799's grid,
2048x2048, 1500 vertices, P `0x10a`, thr0 `0xe8`, no raise), whose inputs (3 global pages at the
abort, 2 at the resume, 4 at the next entry) are those of the raised c4-b5. The round 5 planner
read the kept timelines again around that cell, offline (`closing5/dpm/gsteps.py`,
`endstretch.py`, `allruns.py`, `run2.py`, outputs beside them); the fold checked the one count the
plan states without a script (`closing5/dpm/fold_s_hits.py`, `fold_s_hits.out`). All re-run from
their published copies: byte-identical.

**Results [HW, read post hoc].** Where the global page count steps in the first TA run
(`gsteps.out`, S_k the count of `0x0724` before global page k appears):

| target (1500 vertices) | S2 | S3 | S4 | S5 | last raise | S4 - last raise |
|---|---|---|---|---|---|---|
| 2048x2048 | 0x51 | 0x9d | 0xe8 | 0x132 | 0xe2 (E799) | 6 |
| 4096x4096 (1350 too, S2 and S3) | 0x125 | 0x240 | 0x35b | - | 0x351 (E774) | 10 |
| 4096x2048 | 0x97 | 0x126 | 0x1b9 | - | 0x1b2 (E801) | 7 |
| 2048x4096 | 0x9a | 0x12c | 0x1be | 0x255 | 0x1b6 (E801) | 8 |
| 3072x3072 | 0xa9 | 0x14d | 0x1ef | 0x293 | 0x1e8 (E801) | 7 |

Each S_k is the same, to a page, in every job of its target that reaches it (S4 at 2048x2048 in
c4-b2, c6-0x100, c3-2048-0x162 and c3-2048-0x122 in two stages; S2 of 2048x4096 reads `0x99` in
the calibration job and `0x9a` in the others). E802's `--tri-full` scene takes its 2nd global page
at `0x200`, so all its cells have one; the default triangle never leaves one.

- *c4-b3 is the only job on a step* (`fold_s_hits.out`). Of the 107 jobs with a partial render, its
  thr0 `0xe8` equals S4 of its target; no other thr0 equals an S_k. The nearest are f-1500-0x37c and
  f-1500-0x37e at 4096x4096 (thr0 S4 - 1 and S4 + 1), with no grow.
- *The grow is unique* (`allruns.out`). Of 495 TA runs (first runs and the runs between partial
  renders) one shows `0x0628` grown, c4-b3's first (`0x10003` for about 25 us before the abort, as
  E799's correction says). Three second runs end within a page of a step extrapolated from their
  own run with no grow (c5a-b3, k-1500-0x35e, c-1500-0x380); second-run steps move by up to 2 pages
  between jobs, so whether they met a step is not known.
- *The resume side* (`endstretch.out`, `run2.out`). c4-b3's partial render ends as the silent cells'
  do (1 page, 1 global page 12 us before the last in-stretch sample), then the global count reads 2
  with the page count still 1, then 3 pages. The silent c4-b6 stays at 1 global page into the
  second run; the raised c4-b5 ends the render at 2 pages and 2 global pages. c4-b3's second run
  then steps as c4-b5's does (global 3 at `0x53`, 4 at `0xa0`; c4-b5 `0x51` and `0x9d`, c4-b6 2 at
  `0x50` and 3 at `0x9c`); after its second abort, not on a step, the count stays at 1.

**What it shows [infer].** The request the DPM refused at c4-b3's first abort fell where the next
page is the global list's, and the firmware's out-of-memory routine took its grow branch there
(3d.md §6.4: `CR_DPM_TA_GLOBAL_LIST` grown when `0x0734` bit 0 is clear), the only kept case. The
planner names three hypotheses, written after this data was read and frozen for a session only:
H-GREQ, the grow happens iff thr0 = S_k (fitted on 1 positive and 106 negatives); H-PEND, after a
grow the page the TA asked for is served at the restart, after the resume read the count, so the
guard is as R-5 reads it and our resume count (the last in-stretch sample) is one page high in S
cells only (with it one lower, c4-b3 is silent by the guard); H-BLOCK, the grow leaves a state that
prevents the raise (the resume's tests skipped, or `sa8` bit 7 or 9 otherwise wrong at the second
entry). They differ at S cells on the raising side (S2 and S3 at 2048x2048, S3 at 4096x4096), which
raise under H-PEND and stay silent under H-BLOCK. The planner also reads, from R-5's facts, that a
gate before `0xbbf` at the second entry does not explain the cell (with bits 7 and 8 set and bit 9
clear every entry that reaches `0xbbf` raises, and the abort is reached only through it) [infer].
The table restates the guard: below S3 every cell raises (the saved count floors at 0), from S3 to
S4 - m the partial render leaves 2 of 3 global pages (raise), in the last m - 1 pages before S4 it
leaves 1 (silent), above S4 2 of 4 (silent), with m 6, 10, 7, 8 and 7 at the five targets.

**What it does not show.** Which of H-PEND and H-BLOCK holds, or whether H-GREQ does: one positive,
no repeat, and `0x0734`, `sa8` and the exit paths were not sampled in any kept job. What m is, why
the steps fall where they do by target and scene, and why E802's scene holds one global page stay
open (Q210). The table is post hoc; no cell of it was predicted.
