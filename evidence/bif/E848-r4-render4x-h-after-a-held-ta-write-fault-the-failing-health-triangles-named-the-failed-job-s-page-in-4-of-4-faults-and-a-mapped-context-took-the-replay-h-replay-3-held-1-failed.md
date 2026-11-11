+++
id = "E848"
claim = "R4-render4x stage h (4 held cells, each a 4x job on one array of region headers that faulted with a TA write, BIF_INT_STAT 0x90004, as frozen, then the debugfs reset, the cell's follow-up and health triangles until one passed): every failing health triangle named the failed job's page and SB 6, at 0x20006061 once after a 288 x 144 job (h1) and at 0x2000a061 twice after a 640 x 480 job (h2), a page never seen in a health fault and not the health context's own end (0x20006); a 64 x 64 triangle on a context made for 1024 x 768 run first passed and the health triangle after it too (h3, no replay seen); after a fill that passed, the first health triangle faulted at 0x20006062, the job's page and SB with directory list 2 in place of 1 (h4); the frozen verdict over both attempts: H-REPLAY not supported, 3 held, 1 FAILED (h4, which froze the job's whole word); CR_CLKGATESTATUS read 0x78 after every fault and after the fill and 0x20 once a render had completed; the kernel's 'SGX recovery failed: -110' followed 3 of the 4 held resets and 2 of the 4 health faults, its register dump reading BIF_INT_STAT 0x000d0004 every time"
unit = "bif"
method = "R4-render4x (R4-G) stage h (last; fault limit 5) of the question-closing pass, round 4 (Q003's health-triangle clause), dataset render-closing-r4-render4x, second attempt out/20261111-211649 (stage h 21:19:43 Mac time; the lead's `run/k.sh --from o` after E845's stop), laptop host cedar, 2026-11-11, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E845; each cell: render_rgn_arrays 1 written and read back, hold_recovery Y, the 4x full triangle with E824's words without --aa4 (h1, h3, h4 at 288 x 144, h2 at 640 x 480), the registers read at 2.8 s and 1 s later, the kernel's debugfs reset with the hold set, hold_recovery N read back, then the follow-up (h3: `tri --width 64 --height 64 --max-width 1024 --max-height 768`; h4: a fill), then health triangles (64 x 64) one by one until one passed, four at most, each step with its kernel-log slice and a register snapshot after it; the job's word frozen per cell, the replay words and the follow-ups' outcomes frozen in predictions/h.tsv before the first job (FROZEN.sha256 80a16d2b..., PREDICTIONS.sha256 7ceff7ba...); scored by the frozen score/score_r.py h (out/20261111-211649/score-h.txt, whose summary reads cannot tell only because s0's controls are in the first attempt) and by `score_r.py verdict out/20261111-211649 out/20261111-211315` (postrun/verdict.txt), both re-run on the kept files on 2026-11-11, score-h.txt byte-identical; the directory lists, page directories and -110 register dumps were read after the run from the kept kernel-log slices (post hoc)"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-render4x:out/20261111-211649/h/", "render-closing-r4-render4x:postrun/"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "region header", "Tile Accelerator (TA)"]
+++
**What ran.** After a 4x job on one array of region headers faults with the TA's write past the
layout (0x90004, `SB` 6; E729, E789), the next health triangles fault before one passes: twice
after each of K2's two such faults, at the failed job's own word, and once after E828's j2. The
round 4 planning read this as H-REPLAY: the TA's pending region-header write survives the reset
and is issued again when the TA next runs, through whatever directory is then current. Stage h
froze it on four cells: h1 and h2 the replay's word (h2 at a page never seen in a health fault,
the control that could fail: a fault at 0x20006, the health context's own end, refutes it), h3 a
first job on a context that maps the page (no fault predicted), h4 a fill first (passes, and the
health triangle still faults at the job's word).

**Frozen verdict (as printed, the verdict's stage-h line after its label).** `H-REPLAY: after a TA
write fault the pending region-header write is issued again when the TA next runs: every failing
health triangle names the failed job's own BIF_FAULT word (also at page 0x2000a, never seen in a
health fault), a context that maps the page and a fill do not fault is not supported: 3 held, 1
FAILED, 0 cannot tell of 4`. The stage's own score-h.txt prints `h: cannot tell` with s0's three
controls NODATA, s0 being in the first attempt; its four rows are as below.

**Results [HW].** The held job faulted with the frozen word in 4 of 4 (BIF_INT_STAT 0x90004,
EVENT_STATUS2 0x480 at 2.8 s). Steps after the reset, with `CR_CLKGATESTATUS` after each:

| cell | job's BIF_FAULT | steps (class, BIF_FAULT, clock status) | row |
|---|---|---|---|
| h1 | 0x20006061 | health fault 0x20006061 0x78; health ok 0x20 | held (1 of 1) |
| h2 | 0x2000a061 | health fault 0x2000a061 0x78; fault 0x2000a061 0x78; ok 0x20 | held (2 of 2) |
| h3 | 0x20006061 | 64 x 64 on a 1024 x 768 context ok 0x20; health ok 0x20 | held |
| h4 | 0x20006061 | fill ok 0x78; health fault 0x20006062 0x78; health ok 0x20 | FAILED |

No cell needed a fourth health triangle; health was ok at the stage's end.

**Read after the run [HW, post hoc].**

- h4's health fault differs from the job's word only in `CID` (bits 3:0, the directory list,
  E360): page 0x20006 and `SB` 6 are the job's, the list is 2 where every other fault of the stage
  names 1. [infer] The fill took list 1 after the reset and the health context list 2, the lists
  being given in turn (E360), so the write went through the list current when the TA next ran:
  what H-REPLAY says in words, while its frozen row compared the whole word.
- The kernel's fault lines name the directory each fault went through: in h1 the job and its
  health fault the same, 0x1ae32000; in h2 the job and the first health fault 0x57f2000, the
  second 0x3008b000; in h4 0x6cd3000 and 0x5dbf000.
- "SGX recovery failed: -110" (`SGX boot: no INIT_COMPLETE after 500 ms`) followed the held reset
  of h1, h3 and h4 (not h2) and the health faults of h1 and h4 (not h2's two). In the register
  dump before each -110 `BIF_INT_STAT` read 0x000d0004 (requestor bit 2, type 5) and `BIF_FAULT`
  0x1000b050 after the three held resets, 0x10002050 after h1's health fault and 0x20004060 after
  h4's (`SB` 5 or 6, `CID` 0; page 0x1000b, 0x10002 or 0x20004). The kernel's second reset then
  booted, its EDM up after 143 to 184 us. The scorer's exploratory -110 line reads
  `(False, 0, False, 0, 0)`: it takes the last register dump of the slice, the second boot's
  (0x80000, 0), not the one before the -110; it decides no row.
- h3: no fault anywhere after the reset, so whether a replay landed in the 1024 x 768 context's
  mapped page cannot be seen; no dump of that step was kept.

**What it shows.** [HW] After a held TA write fault and the debugfs reset the first renders that run
the TA fault at the failed job's page with `SB` 6, once (h1, h4) or twice (h2), and the next one
passes; a fill does not end it (the clock status stays 0x78 through the fill, and returns to 0x20
only after a render completes) and a render whose context maps the page ends it without a fault. In
4 of 4 faults the page is the job's, never the health context's own (h2's 0x2000a included). [infer]
The pending write is replayed by the TA through the list current at its next run, as H-REPLAY says;
the frozen word test failed on the list number alone (h4, post hoc). The -110 dumps show a fault
inside the boot itself with the TA's requestor bit, at a PARAMETERS page in 4 and at a page of the
0x2xxxx heap in 1 [post hoc], against the planning's shape (a PARAMETERS page, 4 of 4 in K2).

**What it does not show.** Why h2 replayed twice and h1 and h4 once (K2: twice each), what in the
reset keeps the write pending, and why the -110 followed some resets and not others. One run per
cell, one boot.
