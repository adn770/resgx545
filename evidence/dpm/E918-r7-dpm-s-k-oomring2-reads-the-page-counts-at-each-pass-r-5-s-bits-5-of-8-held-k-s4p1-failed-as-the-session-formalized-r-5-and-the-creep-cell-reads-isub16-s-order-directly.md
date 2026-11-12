+++
id = "E918"
claim = "R7-dpm stage s-k, set B, on module 37EC97AB after the lead's one-shot boot (Q210; our own task oomring2 armed before each of 10 jobs, logging pa1, sa8, sa9 and, new, the two DPM page status registers at every out-of-memory and end-of-render event): the premise held (every out-of-memory rung of k-b6 holds non-zero counts inside the host's samples) and both controls (c4-b5 sa8 & 0x380 = 0x180 and raised, c4-b6 0 and silent); the frozen verdicts: R-5's sa8 bits at the decision entry 'not supported', 5 held, 1 FAILED, 2 cannot tell of 8 (k-b3, k-s3, k-s3m6 and both creep cells held; k-s4p1, thr0 S4 + 1 at 2048x2048, read 0 and silent where the session froze 0x180; band 5 A - 1 and A took one partial render each, so no decision entry); H-PASS 'not supported', 20 held, 8 FAILED, 2 cannot tell of 30 (the task's global count at the abort is the host's, 10 of 10, and its page count lies between the host's samples, 10 of 10, but its global count at the decision entry is not the pages left, 0 of 8); the creep cell (dword 36 = 2, one page left), twice: silent with sa8 & 0x380 = 0, 'isub16 is source 1 minus source 2 (the count read minus dword 36): E864's [infer] read directly'; read after the run (post hoc), k-s4p1's miss is the session's shortcut for R-5 ('2 pages left raises'), not R-5: its abort saved dword 36 = 4 - 2 = 2 and the end of its partial render left 2 global pages, not above it (R6-dpm read the same cell silent, E881), and the 'decision entry' is the second TA run's own abort (0x0724 = thr0, 8 of 8), while the end-of-render rung reads the global pages left as the host's last sample in the render, 10 of 10, and 1 at both grow cells where the host's next sample reads 2 (H-PENDREQ)"
unit = "dpm"
method = "R7-dpm stage s-k (10 jobs, 2048x2048 unless named, the tool's triangle with 1500 vertices: k-b6 first (thr0 0xe3, the premise and a control), k-b5 (0xe2, control), k-b3 (0xe8 = S4, a repeat of c4-b3), k-s3 (0x9d = S3), k-s4p1 (0xe9), k-s3m6 (0x97), k-b5-0x177 and k-b5-0x178 (band 5 A - 1 and A), and the 2048x4096 creep cell thr0 0x24a twice) of round 7's laptop session, dataset render-closing-r7-dpm, set B (attempt b1, freeze FROZEN-B.sha256 with PREDICTIONS-B.sha256 and FROZEN-B.commits, which also pins the fork's verifier files at 664fd0d0), on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 37EC97AB0CB37213C42FCCC (fork 664fd0d0, round 7's own-task register list with ldr of 0x0724 and 0x072c, decision R7-4 a). Lead decisions: after set A (E915 to E917) the lead booted the laptop once into that module (closing7/kernel/deliver/664fd0d00765/gma500_gfx.ko by push-gma500.sh --ko, the user's OK) at about 22:37 Mac time, checked health and ran set B; s-k ran from 22:38:16 to about 22:40, health ok, no fault, hang, EDM stall or stop. Each job: a debugfs reset, oomring2 (bins/oomring2.blob, sha256 c855818e..., landed as asm/fwtask/oomring2.s) armed on PDS #13 slots 0 to 3, the job, the results page read; a rung is [slot + 1, pa0, pa1, sa8, sa9, CR_TIMER, CR_DPM_PAGE_STATUS, CR_DPM_GLOBAL_PAGE_STATUS], the decision entry the first out-of-memory rung after the first end-of-render rung (R5-dpm's reading, E864). Predictions frozen from R-5 (3d.md section 6.4) as the session's gen/r7model.py guard_class put it, H-SPAN (E900), E874's steps, and H-PASS (plan section 2: the counts the passes read are the timeline's at the abort and the pages left at the decision entry); the creep cell's scene check compared its steps with the kept 2048x4096 calibrations'. The scorer re-run at the fold on the kept files gave output byte-identical to out/b1/score-s-k.txt. Post hoc (after the run and its scores were read): postrun/misses.py and its output list every job's rungs beside the host's samples around each partial render; dword 36 after the jobs read from the kept TA/3D control blocks"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-dpm:out/b1/s-k/", "render-closing-r7-dpm:postrun/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "ta3d_ctl"]
+++
**What ran.** R-5 reads the guard of the firmware's raise of the first threshold from the
out-of-memory routine: the abort saves dword 36 as its global page count less 2, the resume sets
`sa8` bits 7 and 8 when its count is above dword 36, the next entry raises when it is above again
(E864, our task reading `sa8`). Which counts the passes compare had been read only from the host's
timeline. Round 7's register list lets our own task load `CR_DPM_PAGE_STATUS` and
`CR_DPM_GLOBAL_PAGE_STATUS`; stage s-k armed oomring2, R5-dpm's ring with those two loads, at the
cells of R6-dpm's r-k and at band 5 of 2048x2048.

**Results [HW, frozen verdict].** `out/b1/score-s-k.txt`, its verdict lines: "R-5's sa8 bits at the
decision entry under oomring2 (k-b5 0x180, k-b6 0) is not supported: 5 held, 1 FAILED, 2 cannot
tell of 8 | H-PASS: the page counts oomring2 reads at the abort and the decision entries is not
supported: 20 held, 8 FAILED, 2 cannot tell of 30 | band 5 A - 1, A with R-5 under H-SPAN: 0 held, 0
FAILED, 2 cannot tell of 2; under E874-B: 0 held, 0 FAILED, 2 cannot tell of 2 | the creep cell
(dword 36 = 2 above 1 page left): isub16 is source 1 minus source 2 (the count read minus dword
36): E864's [infer] read directly".

| job (thr0) | pages left | `sa8 & 0x380`, class | abort: global, pages | decision: global |
|---|---|---|---|---|
| k-b6 (`0xe3`) | 1 | 0, N (control) | 3, `0xe3` | 3 (frozen 1) |
| k-b5 (`0xe2`) | 2 | `0x180`, R (control) | 3, `0xe2` | 4 (frozen 2) |
| k-b3 (`0xe8` = S4) | 1 | 0, N | 3, `0xe8` | 4 (frozen 1) |
| k-s3 (`0x9d` = S3) | 1 | `0x180`, R | 2, `0x9d` | 3 (frozen 1) |
| k-s4p1 (`0xe9`) | 2 | 0, N (frozen `0x180`, R) | 4, `0xe9` | 4 (frozen 2) |
| k-s3m6 (`0x97`) | 1 | `0x180`, R | 2, `0x97` | 2 (frozen 1) |
| k-b5-0x177 | 2 | no decision entry | 5, `0x177` | none |
| k-b5-0x178 | 1 | no decision entry | 5, `0x178` | none |
| k-creep, k-creep2 (`0x24a`) | 1, 1 | 0, N; 0, N | 4, `0x24a` | 4, 4 (frozen 1) |

The ring premise and both controls held; no rung was lost; every partial-render count matched F9's
(exploratory) and every pages-left row H-SPAN's.

**Read after the run [HW, post hoc].** `postrun/misses.out`. Each register's low half equals its
high half in every rung. At the first out-of-memory rung `0x0724` reads thr0 and `0x072c` the host's
sample before the first partial render, 10 of 10. The first end-of-render rung reads the global
pages left, both registers equal, the host's last sample in the render, 10 of 10; at the two grow
cells (k-s3, k-b3) it reads 1 where the host's first sample after the render reads 2. The "decision
entry" of the frozen reading is the second TA run's own abort: `0x0724` = thr0 (the threshold before
any raise) at 8 of 8, `0x072c` the global pages that run holds then. At k-s4p1 the abort's global
count was 4 (thr0 is past S4), dword 36 read 2 after the job, and the end-of-render rung read 2
global pages: by R-5 as 3d.md states it the resume sets no bit and the entry does not raise, which
is what ran; the frozen 0x180 came from the session's `guard_class`, which raises at 2 pages left
whatever the abort's count, and R6-dpm froze and read the same cell silent (E881). In the raised
jobs the entry after the decision read `sa8 & 0x380` = `0x380`, as in E864.

**What it shows [infer].** The out-of-memory routine reads the same page counts the host samples:
at the abort the counts where the TA stopped, at the end of the partial render the global pages it
kept. The `isub16` order of R-5 holds as a frozen held-out verdict (the creep cell, twice), and
R-5 places every cell with a decision entry once the abort's count is taken into dword 36 (k-s4p1
included, post hoc). The page a resume after a grow does not see is the one the host sees right
after the render: the pending request is the global list's own (H-PENDREQ), now read by the
firmware's own pass.

**What it does not show.** The frozen H-PASS clause at the decision entry was framed on the wrong
rung and failed as frozen; the readings at the end-of-render rung are post hoc. Band 5 A - 1 and A
took one partial render each, so R-5 was not read there. What the passes do with `0x0728` and
`0x0734` (not loaded).
