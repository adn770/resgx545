+++
id = "E915"
claim = "R7-dpm stages s-a0 and s-m, set A, on the test module 41E2F5C7 (Q210; the tool's triangle with 1500 vertices, frozen from E874's step replay and E900's straddling-block rule H-SPAN): the premise held, 29 of 29 control rows (S2 to S7 and the need 0x213 in their brackets, c4-b5 R and 2 global pages left, c4-b6 N and 1, t-s3m6 1, g-qf at P 0xa2 two partial renders with H-REPLAY64's run peaks, the knob read back); held out, H-SPAN (the first partial render leaves 2 global pages iff S_k < thr0 < A_k) held at all 19 cells where it parts from E874's burst end B_k (2 pages left where B_k said 1) and per target at 3072x2048 8 of 8, 2048x3072 7 of 7 (cells re-picked on its calibration's steps), 1024x1024 6 of 6 and the six 2048x2048 replicates of bands 5 to 7, but its frozen verdict is 'not supported' at 3072x3072 (10 of 11) and 2560x2560 (6 of 7): at both the band 6 cell thr0 = A_6 (0x3cf, 0x2b1) left 2 pages, so the second page is kept past A_6 there; E874's step model gave the steps of four of five new targets in their brackets (3072x3072, 3072x2048, 2560x2560, 1024x1024; the needs 773, 808, 153 as replayed) and missed 2048x3072's S6 by one page (0x233 against 0x234); R-5's raise flipped at B3 at the three band 3 targets scored, 6 of 6"
unit = "dpm"
method = "R7-dpm stages s-a0 (6 jobs, 29 control rows: a0-cal-2048 at P 0x162, a0-cal-2048f at P 0x422, c4-b5, c4-b6, t-s3m6 and a0-qf-0xa2 at 4096x4096) and s-m (50 jobs: for 3072x3072 a calibration and thr0 B_k - 1 to A_k of bands 5 and 6; for 3072x2048, 2048x3072, 2560x2560 and 1024x1024, never run before, a calibration, B3 - 1, B3 and the parting band's B_k - 1 to A_k; at 2048x2048 A_k - 1 and A_k of bands 5 to 7, replicates of R6-dpm's r-m) of round 7's laptop session (decisions R7-2 a, R7-4 a, R7-6 a; plan closing7/b/exp-dpm-r7.md section 4, every plan decision a; the session's README.md and PREFLIGHT.md with its five deviations), dataset render-closing-r7-dpm, set A (attempt a1, freeze FROZEN.sha256 against resgx545 main 1c64f3a and data 830641e6), on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 41E2F5C756F96D20F7109A4 (fork 3f0b3e74, loaded = installed at each stage start), stock firmware, tool ~/sgxfive-test-rgn4 (sha256 e6951558...), ~/regtimeline sampling R5-dpm's 16 registers, a debugfs reset before each job; s-a0 from 22:10:30 and s-m from 22:11:53 Mac time, health ok after each, no fault, hang or stop, no lead decision during the stages. Predictions from the frozen offline rules (gen/r7model.py imports E874's f5lib.py, E900's g3_span.py and E899's g2_replay64.py from their published copies and refuses one whose hash is not its FREEZE file's): a cell's H-SPAN and E874-B predictions are the pages left at its thr0; a calibration whose steps leave the frozen model re-picks its cells as its own S_k + (model cell - model S_k), scored for H-SPAN only (2048x3072, whose S6 was off). Round 7's gate (plan section 6, landed in tools/closing): a control without a reading is its own state and stops the session at s-a0; a headline is gated only by its stage's controls and s-a0's rows of the same scene. The scorer re-run at the fold on the kept files gave output byte-identical to out/a1/score-s-a0.txt and score-s-m.txt. Post hoc (after the run and its scores were read): postrun/misses.py and its output read the two FAILED H-SPAN cells and the calibrations' brackets"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-dpm:out/a1/s-a0/", "render-closing-r7-dpm:out/a1/s-m/", "render-closing-r7-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "ta3d_ctl"]
+++
**What ran.** E874's block-level replay of the TA gives the global steps S_k of the tool's
1500-vertex triangle, and E900 read the end of the margin in which the first partial render keeps
two global pages as A_k, the page count once the object whose block straddles global pages k - 1
and k is tiled (H-SPAN), where E874 had the end of the burst, B_k. Both were read on kept data;
only 2048x2048 bands 5 to 7 parted them. Stage s-m froze cells from both at one target run once
(3072x3072) and four never run, with E874's step model checked by each target's calibration, after
the six s-a0 controls.

**Results [HW, frozen verdict].** `out/a1/score-s-a0.txt`: "the premise holds on the test module
(S2..S7 and the need in their brackets, 2 then 1 pages left at c4-b5 / c4-b6, R and N, t-s3m6 1
left, g-qf 2 partial renders with H-REPLAY64's peaks, knob proof) (29 of 29 rows decided)".
`out/a1/score-s-m.txt`, its verdict lines:

| target | H-STEPMODEL | H-SPAN | rival E874-B | R-5 |
|---|---|---|---|---|
| 3072x3072 | 6 of 6 | not supported: 10 held, 1 FAILED | 3 held, 8 FAILED | 0 rows |
| 3072x2048 | 8 of 8 | 8 of 8 | 4 held, 4 FAILED | 2 held |
| 2048x3072 | not supported: 7 held, 1 FAILED | 7 of 7 | 7 cannot tell | 2 cannot tell |
| 2560x2560 | 8 of 8 | not supported: 6 held, 1 FAILED | 3 held, 4 FAILED | 2 held |
| 1024x1024 | 8 of 8 | 6 of 6 | 4 held, 2 FAILED | 2 held |
| 2048x2048 bands 5 to 7 | - | 6 of 6 (replicates) | 3 held, 3 FAILED | - |

("n of n" is the printed "(n of n rows decided)", a verdict that held; no row cannot tell unless
named) and "the discriminating cells (H-SPAN 2, E874-B 1): 19 held, 0 FAILED, 0 cannot tell of 19".
The steps read at the calibrations (the frozen model's in every case but one): 3072x3072 `0xa9`,
`0x14d`, `0x1ef`, `0x293`, `0x335`, `0x3d9` (its U, `0x479` by the replay, is above the `0x400`
clamp: steps only); 3072x2048 `0x77` to `0x299`, need 773 (`0x305`); 2048x3072 `0x77`, `0xe6`,
`0x156`, `0x1c3`, `0x234` (model `0x233`), `0x2a3`, need 783 (`0x30f`); 2560x2560 `0x7a` to `0x2b6`,
need 808 (`0x328`); 1024x1024 `0x1c` to `0x86`, need 153 (`0x99`). H-GREQ (no grow off a step) held
at all 45 cells and F9's partial-render counts (exploratory) at all 45.

| target | band | cells thr0: pages left | A_k (H-SPAN) | B_k (E874) |
|---|---|---|---|---|
| 3072x3072 | 5 | `0x329` to `0x32e`: 2, `0x32f`: 1 | `0x32f` | `0x32a` |
| 3072x3072 | 6 | `0x3cc` to `0x3ce`: 2, `0x3cf`: 2 | `0x3cf` | `0x3cd` |
| 3072x2048 | 5 | `0x224` to `0x228`: 2, `0x229`: 1 | `0x229` | `0x225` |
| 2048x3072 | 5 | `0x229` to `0x22c`: 2, `0x22d`: 1 | `0x22d` | `0x22a` |
| 2560x2560 | 6 | `0x2ad` to `0x2b0`: 2, `0x2b1`: 2 | `0x2b1` | `0x2ae` |
| 1024x1024 | 5 | `0x6a` to `0x6c`: 2, `0x6d`: 1 | `0x6d` | `0x6b` |
| 2048x2048 | 5 | `0x177`: 2, `0x178`: 1 | `0x178` | `0x176` |
| 2048x2048 | 6 | `0x1c2`: 2, `0x1c3`: 1 | `0x1c3` | `0x1c1` |
| 2048x2048 | 7 | `0x20c`: 2, `0x20d`: 1 | `0x20d` | `0x20c` |

At band 3 every target's B3 - 1 left 2 pages and raised, B3 left 1 and was silent (A3 = B3).

**Read after the run [HW, post hoc].** `postrun/misses.out`: the two band 6 cells that FAILED,
3072x3072 `0x3cf` and 2560x2560 `0x2b1`, each took one partial render, no grow, with the
calibration's steps (S6 `0x336` and `0x244` read in those jobs); the session ran no cell above A_6
there, so where one page is first left at band 6 is not read. 2048x3072's S6 was a one-sample
bracket at `0x234`.

**What it shows [infer].** Held out, the margin ends at the straddling block and not at the burst
end at bands 3 and 5 of four new targets and at bands 5 to 7 of 2048x2048: every cell where the two
rules part kept two pages, as H-SPAN says. At band 6, run only at 3072x3072 and 2560x2560, the
second page was kept at A_6 at both, so H-SPAN is not the rule of every band, as B_k was not at
2048x2048. E874's replay places the steps of
targets it was not read on, with one more one-page miss.

**What it does not show.** Why band 6 keeps the second page longer at those two targets, and how
far; the margin at bands not run; the step miss at 2048x3072 S6 (and E874's at 2048x4096 S3); any
other scene than the tool's 1500-vertex triangle.
