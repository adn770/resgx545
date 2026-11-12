+++
id = "E920"
claim = "R7 session r7-faults stage m (Q003; E848's held TA write fault at 288 x 144, page 0x20006, with a manipulation while held, before the reset: none, CR_BIF_CTRL.CLEAR_FAULT set then cleared through kregnow (E826's write), or a hold of about 10 s; order M0 M1 M2 M2 M1 M0): every job faulted 0x90004 at 0x20006061, both clear cells read the fault registers hidden with the bit set and back after it, and every cell ended with a triangle that drew; the first boot after the held reset timed out in both M0 cells (controls), in both 10 s holds and in one of the two clears, and came up after the other clear (m1b), whose first triangle then drew with no replay, the only held 0x90004 reset of the session without one; frozen verdict 'H-CLR REFUTED (1 held, 1 FAILED, 0 cannot tell of 2); H-TIME REFUTED (0 held, 2 FAILED, 0 cannot tell of 2); H-NULL REFUTED (3 held, 1 FAILED, 0 cannot tell of 4)', 35 controls passing; so neither the clear nor the hold time decides the boot, and the null fails on the same one cell; 5 held resets and 4 replays timed out, each dump with CR_CLKGATESTATUS 0x000ccff8 and BIF_INT_STAT 0x000d0004, the second boot up in all"
unit = "bif"
method = "R7 session r7-faults (E919's session, attempt out/20261112-222800, module, tool, freeze and s0), stage m after d (22:32:43 Mac time): six cells of E848's job at 288 x 144 (d1's), each as E919's cell with, after the registers at 2.8 s and 1 s later and with the hold still Y, M0 nothing (m0a, m0b: the stage's controls, E901's fit size), M1 kregnow 0x0c00^=0x10 (CLEAR_FAULT set), registers, kregnow 0x0c00^=0x10 (cleared), registers (m1a, m1b), M2 5.2 s more (m2a, m2b; about 10 s from the fault to the reset, E826 f2's hold was 9.1 s), in the order m0a m1a m2a m2b m1b m0b; the held reset came about 4.4 s after the fault in M0, 5.5 s in M1 and 10.1 s in M2. Frozen [infer, from one pair: E826 f2 cleared after 9.1 s and came up, E789 a6 timed out]: H-CLR (the clear while held makes the boot come up) and H-TIME (a 9 s hold makes it come up), against H-NULL (E901's R-PAGE: it times out at 0x20006 as without the manipulation); controls: M-CTL (m0a and m0b time out; they gate every m row), M-CLR (with the bit set the kernel read 0 and 0, cleared the fault's words back, E826), H-JOB and H-END per cell. The session's budget of 16 timed-out boots stood at 14 after m; no stop rule fired and the stage ran to its end. Scored by the frozen score/score_f.py (out/20261112-222800/score-m.txt), re-run on the kept files at the fold, byte-identical; postrun/posthoc.py as in E919"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-faults:out/20261112-222800/m/", "render-closing-r7-faults:postrun/"]
terms = [
    "CR_BIF_CTRL", "CR_BIF_CTRL.CLEAR_FAULT", "CR_BIF_FAULT", "CR_BIF_INT_STAT",
    "CR_CLKGATESTATUS", "CR_TE_DIAG2", "CR_TE_DIAG5", "Tile Accelerator (TA)",
]
+++
**What ran.** E901's one exception in its fit was R3k-pixel's k-bif f2 at 0x20008: held 9.1 s with
E826's `CLEAR_FAULT` writes, and its boot came up where E789's a6 at the same size timed out. Stage
m repeats the 288 x 144 cell, whose boot timed out in 10 of 11 kept boots, with each manipulation
separately, twice, in a balanced order.

**Frozen verdict (as printed).** `SUMMARY: m: H-CLR REFUTED (1 held, 1 FAILED, 0 cannot tell of 2);
H-TIME REFUTED (0 held, 2 FAILED, 0 cannot tell of 2); H-NULL REFUTED (3 held, 1 FAILED, 0 cannot
tell of 4)`; `SUMMARY: Q003 clear (m): H-CLR: CLEAR_FAULT set and cleared while held makes the boot
come up is not supported: 1 held, 1 FAILED, 0 cannot tell of 2`; `SUMMARY: Q003 time (m): H-TIME: a
9 s hold makes the boot come up is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; `SUMMARY:
Q003 null (m): H-NULL: the boot times out as without the manipulation is not supported: 3 held, 1
FAILED, 0 cannot tell of 4`; `SUMMARY: m: timed-out boots after the held resets 5`; `SUMMARY: m
controls: 35 PASS, 0 FAIL, 0 NODATA`.

**Results [HW].**

| cell | while held | held reset | replays (boot) | drew at | TE_DIAG2, DIAG5 at the hold |
|---|---|---|---|---|---|
| m0a | nothing | timed out | 1 (timed out) | t2 | 0x4a0, 0x353 |
| m1a | clear | timed out | 1 (timed out) | t2 | 0x4a0, 0x352 |
| m2a | 10 s | timed out | 1 (timed out) | t2 | 0x4a0, 0x353 |
| m2b | 10 s | timed out | 2 (up, timed out) | t3 | 0x4a0, 0x353 |
| m1b | clear | up | none | t1 | 0x4ab, 0x35b |
| m0b | nothing | timed out | 1 (up) | t2 | 0x4a4, 0x355 |

Every cell's `CR_DPM_PAGE_STATUS` read 0x000b000b at the hold. In both clear cells the two kregnow
writes returned 0 and the registers read as E826's (`BIF_INT_STAT` and `BIF_FAULT` 0 with the bit
set, the fault's words back after it). Each timed-out dump read `CR_CLKGATESTATUS` 0x000ccff8 and
`BIF_INT_STAT` 0x000d0004, `BIF_FAULT` 0x20006060 (m0a, m2a, m2b's held resets), 0x1000b050 (m1a,
m0b), 0x20004060 or 0x10002050 (replays), and the kernel's next boot came up, 9 of 9. Each reset
before a boot read `BIF_FAULT` 0 and `BIF_INT_STAT` 0x80000 before and after its own
`CLEAR_FAULT`. The stage's health passed.

**Read after the run [HW, post hoc].** m1b is the only held 0x90004 reset of the session's 13,
r6-held's six and E848's three triangle cells after which the first triangle drew with no replay
(E848's h3 ended it with a render on a context that maps the page): there the pending write that
the replays show elsewhere did not come back. Its `CR_TE_DIAG` counts at the hold
were the highest of the stage; E848's h1 read the same pair and timed out (E919).

**What it shows.** Neither manipulation decides the boot: the clear while held came up once and
timed out once, and both 10 s holds timed out, so E826 f2's boot coming up after its writes and its
9.1 s hold was not caused by either alone. The null (the boot times out at 288 x 144 whatever is
done while held) fails on the same single cell, so the outcome at this size is mostly a timeout (5
of 6 held resets, 7 of 9 boots in m) without being certain. A host toggle of `CLEAR_FAULT` while
held hides and returns the fault words as in E826 and does not, by itself, clear the pending write
(m1a replayed it).

**What it does not show.** Why m1b differs: one cell came up with no replay, after the clear, and
nothing read at its hold but the small TE count difference sets it apart; whether the clear made
that more likely needs more cells than two. Hold times between 5.5 and 10 s and other writes while
held were not run. That the pending write is the region-header write issued again inside the boot
is E901's reading [infer].
