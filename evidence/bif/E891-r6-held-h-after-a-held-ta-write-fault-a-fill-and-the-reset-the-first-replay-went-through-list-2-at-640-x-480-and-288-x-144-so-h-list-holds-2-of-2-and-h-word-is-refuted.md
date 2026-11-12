+++
id = "E891"
claim = "R6 session r6-held part H stage q, the list rows (Q003's health-triangle clause; E848's held 4x job on one array, a TA write fault BIF_INT_STAT 0x90004, then the debugfs reset, the cell's follow-up and triangles until one drew, on the r6 kernel): with no follow-up (a0, 640 x 480, the control) the first triangle faulted at the job's word 0x2000a061 (the replay on this kernel, H-REPLAY's control); after a fill that passed, the first triangle faulted at the job's page and SB through list 2, 0x2000a062 at 640 x 480 (a1, held out at a new size) and 0x20006062 at 288 x 144 (a2, E848 h4's replicate), where the frozen word test wanted list 1; every held job faulted with the frozen word and every cell ended with a triangle that drew within three; frozen verdict 'H-LIST consistent (2 held, 0 FAILED, 0 cannot tell of 2); H-WORD REFUTED (0 held, 2 FAILED); H-REPLAY consistent (2 held of 2)', controls 40 PASS, 0 FAIL, 0 NODATA over the stage; so the replayed write goes through the directory list current at the next TA run, not the list of the faulted job"
unit = "bif"
method = "R6 session r6-held part H (round 6, decisions R6-3 a, R6-4 a, R6-5 a; plan closing6/rank/rank-round6.md session B and K2), dataset render-closing-r6-held, attempt out/20261112-154536 (s0 15:45:36, q 15:46:11 Mac time, after part P on the same boot, E890), host cedar, kernel 7.3.0-resgx545, module of the linux fork's branch r6-kernel at 3f0b3e74 (srcversion 41E2F5C756F96D20F7109A4, installed = loaded; render_tail_room at its default 0, checked and never written), stock firmware sha256 6a00268e..., tool ~/sgxfive-test-rgn4 (sha256 e6951558..., E848's); s0: n0 (bif_flush with nothing held refused with EBUSY, BIF_CTRL unchanged, the peek's line) and c1 (the 64 x 64 health triangle), 4 controls passing; q: six cells in the order a0, b0, a1, b1, a2, b2 (the b cells are E892's), each: a debugfs reset, render_rgn_arrays 1 written and read back, registers and the peek, hold_recovery Y, E848's job byte for byte (tri --tri-full with the maximum equal to the size, E824's four pokes, no --aa4), registers at 2.8 s and 1 s later, the debugfs reset with the hold set, hold_recovery N, registers, render_rgn_arrays 0, the fill in a1 and a2, then triangles one at a time until one drew (three at most), then strict health; the laptop's files under ~/scratch/r6h/; the stage stopped by its frozen rule after b2's health, rc 22 (a 'SGX recovery failed: -110' in two cells in a row, a2 and b2, the risk E848 named), with every cell run; the fault-class count reached 17 against a limit of 15 that stops a stage only with rows left (b2 was the last); the lead did not resume, the questions being decided, and the laptop's health passed after the stop (the lead's check); predictions frozen in predictions/q.tsv (PREDICTIONS.sha256) before the run from E848, E826, E789 and E507/E729 (H-LIST from E848 h4's post hoc reading, H-WORD E848's frozen test) and replayed before the freeze on E848's kept files (tests/test_replay.py); the driver writes a stage's score after the stage ends, so no score-q.txt was kept: the frozen score/score_h.py (scorekit byte for byte resgx545 main's) was run on the kept files at the fold (postrun/score-q.txt, postrun/verdict.txt), and score-s0.txt re-run gave the kept file byte for byte"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-held:out/20261112-154536/q/", "render-closing-r6-held:postrun/"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header", "Tile Accelerator (TA)"]
+++
**What ran.** E848 replayed the failed job's page in every health fault after a held TA write
fault, but its frozen word test failed once: after a fill the health triangle faulted at the job's
page and `SB` through list 2 (h4), which the round read after the run as the write going through
the list current at the next TA run. Stage q holds that reading out (H-LIST against H-WORD, the
whole word) at a size it was not read at (a1, 640 x 480) and replicates h4 (a2, 288 x 144), with
a0 (640 x 480, no follow-up) as the control that a replay happens on this kernel at all.

**Frozen verdict (as printed, the stage's lines).** `SUMMARY: q: H-LIST consistent (2 held, 0
FAILED, 0 cannot tell of 2); H-WORD REFUTED (0 held, 2 FAILED, 0 cannot tell of 2); H-FLUSH REFUTED
(...); H-PEND consistent (...); H-BOOT REFUTED (...); H-LATCH consistent (...); H-REPLAY consistent
(2 held, 0 FAILED, 0 cannot tell of 2)`, `SUMMARY: Q003 list (q): H-LIST: the replay goes through
the directory list current at the next TA run (2 of 2 rows decided)`, `SUMMARY: q controls: 40
PASS, 0 FAIL, 0 NODATA` (postrun/score-q.txt; the flush rows are E892's).

**Results [HW].** Each held job read `BIF_INT_STAT` 0x90004, `CR_EVENT_STATUS2` 0x480 and
`CR_CLKGATESTATUS` 0x000ccff8 at 2.8 s and 1 s later; after the reset 0x80000, 0 and 0x78.

| cell | size | job's BIF_FAULT | follow-up | steps after the reset | replays |
|---|---|---|---|---|---|
| a0 | 640 x 480 | 0x2000a061 | none | fault 0x2000a061, fault 0x2000a061, ok | 2 |
| a1 | 640 x 480 | 0x2000a061 | fill ok | fault 0x2000a062, fault 0x2000a061, ok | 2 |
| a2 | 288 x 144 | 0x20006061 | fill ok | fault 0x20006062, ok | 1 |

The first row in each is the scored one (a0's H-REPLAY control, a1's and a2's H-LIST and H-WORD).
The clock status read 0x78 after each fault and after each fill, 0x20 after the triangle that
drew. In the flushed cells of the stage the first replays were through the same lists (E892: list
1 with no fill, list 2 after a fill).

**Read after the run [HW, post hoc].** In a1 the second replay went through list 1 again
(0x2000a061, as in b1): the kernel's fault lines give each triangle's context its own directory (PD
0x357e3000 for the first, 0x6ffb000 for the second), so the list number moves with the context that
runs the TA, not with the count of replays. Replays by cell over E848 and this stage: at 640 x 480
two in each of 5 cells (h2, a0, b0, a1, b1); at 288 x 144 one in 3 of 4 cells (h1, h4, a2) and two
in b2. The -110 boots of a2 are E892's.

**What it shows.** The replayed TA write is issued through the directory list current when the TA
next runs: after a fill took list 1, the first triangle's context ran on list 2 and the fault named
the job's page and `SB` with list 2, at a size and page E848 had not read it at (a1, 0x2000a) and
again at h4's (a2): H-LIST holds 2 of 2 held out, H-WORD (the whole word, list included) is refuted.
With E848 and E892, all 15 replays of 9 cells kept the failed job's page and `SB` 6. The replay
happens on the r6 kernel as on the rgn4 one (a0, the control, two replays as in E848 h2).

**What it does not show.** What keeps the write pending through the reset, why two replays at 640
x 480 and one or two at 288 x 144, and what ends them (a render that maps the page, E848 h3, was
not run again). Which list a context gets is the kernel's, read here from its fault lines [infer];
lists other than 1 and 2 were not reached. One boot, one run of each cell.
