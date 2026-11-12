+++
id = "E919"
claim = "R7 session r7-faults stage d (Q003; E848's held 4x TA write fault, one array, at seven sizes whose fault pages are 0x2000a, 0x20006, 0x20008 and 0x20009, then the held reset and triangles until one drew): every held job faulted 0x90004 at its frozen page and every cell ended with a triangle that drew; the first boot after the held reset timed out ('SGX recovery failed: -110') at 288 x 144 (0x20006, control) and at 128 x 528 (0x20009) and came up at 640 x 480 (0x2000a, control), 256 x 288 (0x20006), 320 x 400 twice and 384 x 384 (0x20008), so E901's frozen page rule fails held out: frozen verdict 'H-PAGE REFUTED (2 held, 8 FAILED, 0 cannot tell of 10); H-SIZE REFUTED (4 held, 1 FAILED, 0 cannot tell of 5)', 35 controls passing; 2 held resets and 3 replays of the stage timed out, every dump with CR_CLKGATESTATUS 0x000ccff8 and BIF_INT_STAT 0x000d0004 and the second boot up; read after the run with stage m (E920), the boots after a 0x90004 fault timed out in 11 of 14 at 288 x 144 and 3 of 15 at the other five sizes, and no register read at the hold separates the boots that timed out from those that came up"
unit = "bif"
method = "R7 session r7-faults (round 7, decisions R7-2 a and the plan's 2 a and 3 a: a -110 is a reading, budget 16 timed-out boots; plan closing7/c/exp-faults-r7.md sections 1.3 to 1.5), dataset render-closing-r7-faults, attempt out/20261112-222800 (run-r7f.log; s0 22:28:00, l 22:28:37, d 22:29:46, m 22:32:43 Mac time, the last of round 7's sessions on that boot), host cedar, module of the linux fork's branch r6-kernel at 3f0b3e74 (srcversion 41E2F5C756F96D20F7109A4), tool ~/sgxfive-test-rgn4 (sha256 e6951558...), the laptop's files under ~/scratch/r7f/; frozen before the first job against resgx545 1c64f3a and resgx545-data 830641e6 (FROZEN.sha256 aaf69a30..., 60 files, PREDICTIONS.sha256 04532e2d..., FROZEN.commits); s0's five controls passed first (kregnow's CLEAR_FAULT set and cleared with nothing held, E826 n0's readings, and the 64 x 64 health triangle). Stage d: seven cells in the order d0 640 x 480, d1 288 x 144 (the stage's controls, E901's fit sizes), d2 320 x 400, d3 256 x 288, d4 128 x 528, d5 384 x 384, d6 320 x 400 (held out), each E848's job byte for byte but the size (tri --tri-full, max = size, render_rgn_arrays 1, the four pokes), run as r6-held's cells: reset, registers, hold_recovery Y, the job, registers at 2.8 s (snap 1) and 1 s later, the debugfs reset with the hold still Y (about 4.4 s after the fault), hold_recovery N, registers, then triangles one by one until one drew (three at most), strict health; the row's kernel log kept whole and every timed-out boot counted in the session's ledger. Frozen: H-PAGE, E901's rule R-PAGE (the first boot after the held reset, and after the first replay, times out iff the fault page is 0x20006 to 0x20008), against H-SIZE (E892's wording: iff the size is 288 x 144); controls per cell (H-JOB the fault word and page, H-END a draw within three) and the stage's (D-CTL: d0 up, d1 timed out); the page of 128 x 528 (0x20009) from the fork's layout [infer] and checked by the cell's H-JOB control. No stop rule fired; the stage ran to its end. Scored by the frozen score/score_f.py (out/20261112-222800/score-d.txt); re-run on the kept files at the fold, byte-identical. postrun/posthoc.py (written at the fold after the scoring, standard library) reads every boot after a 0x90004 fault in the kept row slices of d and m and the registers at the hold; its output is postrun/posthoc.out"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-faults:out/20261112-222800/d/", "render-closing-r7-faults:postrun/"]
terms = [
    "CR_BIF_FAULT", "CR_BIF_INT_STAT", "CR_CLKGATESTATUS", "CR_DPM_PAGE_STATUS", "CR_TE_DIAG2",
    "CR_TE_DIAG5", "Tile Accelerator (TA)",
]
+++
**What ran.** E901 read every kept kernel log and froze a page rule from its scans: after a held
TA write fault (0x90004, `SB` 6) the boot times out iff the job's fault page is 0x20006 to 0x20008
(R-PAGE; 770 of 771 fit boots, r6-held SEMI). Stage d puts one held job at each reachable page,
two at a second size for 0x20006 and 0x20008, against E892's narrower wording (288 x 144 only).

**Frozen verdict (as printed).** `SUMMARY: d: H-PAGE REFUTED (2 held, 8 FAILED, 0 cannot tell of
10); H-SIZE REFUTED (4 held, 1 FAILED, 0 cannot tell of 5)`; `SUMMARY: Q003 page (d): H-PAGE: the
boot after a held 0x90004 fault times out iff the page is 0x20006 to 0x20008 is not supported: 2
held, 8 FAILED, 0 cannot tell of 10`; `SUMMARY: Q003 page (d): H-SIZE: it times out iff the size
is 288 x 144 is not supported: 4 held, 1 FAILED, 0 cannot tell of 5`; `SUMMARY: d: timed-out boots
after the held resets 2`; `SUMMARY: d controls: 35 PASS, 0 FAIL, 0 NODATA`. s0: `SUMMARY: s0:
controls all PASS (5)`.

**Results [HW].** Boots: the held reset's first, then each replay's (a triangle that faulted);
`0x0724` (`CR_DPM_PAGE_STATUS`) at the hold.

| cell | size | job fault | 0x0724 | held reset | replays | drew at |
|---|---|---|---|---|---|---|
| d0 | 640 x 480 | 0x2000a061 | 0x00060006 | up | up | t2 |
| d1 | 288 x 144 | 0x20006061 | 0x000b000b | timed out | timed out | t2 |
| d2 | 320 x 400 | 0x20008061 | 0x00130013 | up | up | t2 |
| d3 | 256 x 288 | 0x20006061 | 0x00130013 | up | up, timed out | t3 |
| d4 | 128 x 528 | 0x20009061 | 0x00120012 | timed out | up, up | t3 |
| d5 | 384 x 384 | 0x20008061 | 0x001f001f | up | up, up | t3 |
| d6 | 320 x 400 | 0x20008061 | 0x00130013 | up | timed out | t2 |

Every replay faulted at its cell's job word. Each timed-out boot's dump read `CR_CLKGATESTATUS`
0x000ccff8 and `BIF_INT_STAT` 0x000d0004, with `BIF_FAULT` 0x1000b050 (d1's held reset),
0x20009060 (d4's) or 0x20004060 (the three replays), and the kernel's next boot came up (5 of 5);
every reset before a boot read `BIF_FAULT` 0 and `BIF_INT_STAT` 0x80000 before and after
`CLEAR_FAULT`, as in E901. The ledger counted 5 timed-out boots in d; the stage's health passed.

**Read after the run [HW, post hoc] (postrun/posthoc.out, with stage m, E920).** Of the 29 boots
after a 0x90004 fault in d and m, 14 timed out: by page 12 of 17 at 0x20006, 1 of 7 at 0x20008, 1
of 3 at 0x20009, 0 of 2 at 0x2000a; by size 11 of 14 at 288 x 144 and 1 of 3 at 256 x 288 (the same
page), 1 of 4 at 320 x 400, 0 of 3 at 384 x 384, 1 of 3 at 128 x 528, 0 of 2 at 640 x 480. Of the
registers read at the hold, the ones whose values split the held boots that timed out from those
that came up are free-running (0x0144, 0x0acc, 0x0c38 differ in every dump; 0x0b14 interleaves)
and `CR_TE_DIAG2`/`CR_TE_DIAG5`, which interleave across sizes (timed out 0x4a0, 0x4a4, 0x840;
up 0x250, 0x4ab, 0x8d0, 0x900, 0xf10) and at 288 x 144 put the one held reset that came up (m1b,
0x4ab and 0x35b) above the six that timed out (0x4a0 or 0x4a4); E848's h1 read 0x4ab and 0x35b at
its hold and timed out, so that split does not carry to kept data. The predictor that does best
is the size 288 x 144 (23 of 29 boots as "times out iff 288 x 144"; R-PAGE gives 17 of 29), and it
is a rate, not a rule.

**What it shows.** E901's page rule does not hold out: at 0x20008 the boot came up after 3 of 3 held
resets (and 6 of 7 boots), at 0x20006 one size (256 x 288) came up after its held reset, and the
page 0x20009 that R-PAGE puts on the up side timed out. Its fit rested on 0x20006 being met only at
288 x 144 and on the one unique 0x20008 timeout (E789's a6). E892's size wording fails too (128 x
528 timed out; d3, d6 timed out on a replay). The same cell can go either way (d6's held reset up,
its replay timed out; d3's second replay timed out after two that came up), so the -110 after a
0x90004 is not decided by the page or the size alone; at 288 x 144 it is the common outcome (11 of
14 boots), elsewhere the rare one (3 of 15). Every timed-out boot is the E901 shape (TA clocks on, a
TA write through list 0) and the second boot recovered it [HW]; reading it as the replayed write
issued inside the boot is E901's [infer].

**What it does not show.** What decides a given boot: no register read at the hold separates them
and the rates are post hoc, from one run of each cell. Whether the TA's progress at the hold
matters (the `CR_TE_DIAG` counts and the page count vary slightly between cells of one size, and the
one contrast seen does not survive E848's h1) or something in the boot's own timing does (kernel
option K3, the boot trace, was not built). Plan step F2 (the pages a completed job allocates, the
rival H-DONE) was not compiled, so H-DONE was not tested.
