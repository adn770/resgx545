+++
id = "E901"
claim = "Round 7 offline reading of every kept kernel log of resgx545-data (Q003; post hoc scans, then one rule frozen as a fit and scored on r6-held, which the planner's scans had already read: SEMI, not held out): over 2956 logs of 336 sessions the first boot after a BIF fault timed out (no INIT_COMPLETE, 'SGX recovery failed: -110') only after fault word 0x90004, 54 of 147 such boots (53 unique: one log is kept twice), and 0 of 756 after the fifteen other words; for SB 6 (the region headers) the kept boots split by the job's fault page, 10 of 11 at 0x20006 and 0 of 15 at 0x2000a, a split that did not hold out (E919: the boot does not follow the page); the frozen rule R-PAGE (times out iff the page is 0x20006 to 0x20008) gave 770 of 771 fit boots and 16 of 17 r6-held boots, the control (no time-out after 0x90008 or 0x90100) 109 of 109; every timed-out dump read CR_CLKGATESTATUS 0x000ccff8, BIF_INT_STAT 0x000d0004 and a BIF_FAULT through list 0 (54 of 54), and the second boot came up in 54 of 54; where the kernel logs it (27 boots), the reset read BIF_FAULT 0 and BIF_INT_STAT 0x80000 with every block held in reset, before and after CLEAR_FAULT and before the boot, in the 10 that timed out as in the 17 that came up [corrected 2026-11-12, see Correction]"
unit = "bif"
method = "Offline, no run (round 7, area faults, decision R7-1 a; plan closing7/c/exp-faults-r7.md section 1, steps F1, F4 and F5). The planner's scans closing7/c/offline/boot110.py, boot_clk.py, boot_page.py and reqtab.py (standard library only) walk every kernel log of resgx545-data (kernel.log*, *.kmsg, *dmesg*, gzipped or not; 2956 files, 336 sessions as the first two path components), de-duplicate events per session by (timestamp, text), and pair each 'BIF fault <status> at <addr>' line with the next 'SGX boot: kicking the EDM' and its result ('EDM up after' or 'no INIT_COMPLETE', with the register dump after it); the outputs are post hoc readings. F1: closing7/c/fold/f1_fit.py, written and hashed (FROZEN-f1.sha256 beside it, with boot110.py) before its first run, freezes the rule R-PAGE of the plan untuned (a 0x90004 fault with SB 6 is followed by a timed-out boot iff its page is 0x20006 to 0x20008; every other word by a boot that comes up), fits it on every session but render/closing-r6-held and scores r6-held as it falls; r6-held's boots were in the planner's scans, so the score is SEMI, not held out. F5: closing7/c/fold/f5_latch.py (post hoc) reads the two lines the fork's sgxfive_clear_faults logs (branch resgx545 at 3f0b3e74, read with git show: sgxfive_halt runs the deinit script and SOFT_RESET all, then sgxfive_clear_faults reads BIF_FAULT and BIF_INT_STAT, toggles CR_BIF_CTRL.CLEAR_FAULT and reads them again, then the boot). The scripts and outputs are published under cited/ of resgx545-data; each was re-run from its published copy on the fold's data worktree and its output is byte-identical to the kept one. Plan steps F2 (size to pages) and F3 (replay counts) were not done in this fold"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["cited-scratch", "render-closing-r6-held"]
terms = ["CR_BIF_FAULT", "CR_BIF_INT_STAT", "CR_BIF_CTRL", "CR_CLKGATESTATUS"]
+++
**What was done.** Q003's note of 2026-11-11 counted the -110 after a 0x90004 fault 51 times of
157 over 543 logs (round 4's faultseq.out), and E892 read the r6-held boot as "the timeouts
followed the 288 x 144 cells". The round 7 planner scanned every kept kernel log again, with the
r4 to r6 sessions, and paired each fault with the boot after it; this fold froze the page rule
those scans suggested and scored it, and read the kernel's reset lines before each boot.

**Frozen verdict (as printed, f1_fit.out).** `fit: 770 of 771 first boots as R-PAGE says, 1 not`
(the miss: R3k-pixel's k-bif f2, 0x20008061, held, up, after E826's writes); `scored (r6-held,
SEMI): 16 of 17 first boots as R-PAGE says, 1 not` (the miss: b2's first replay, 0x20006061, up);
`control: 109 of 109 first boots after 0x90008/0x90100 came up: PASS`. Out of the rule's domain,
0x90004 with SB other than 6: 42 timed out (all SB 5 at page 0x10000, the dpm context-table
sessions) and 73 came up (25 of them SB 5 there).

**Results [HW, post hoc].** First boot after a fault, by word (boot110.out):

| fault word | boot timed out | boot came up | no boot |
|---|---|---|---|
| 0x90004 | 54 (53 unique) | 93 | 1 |
| fifteen others (0x80400 to 0xd2000) | 0 | 756 | 208 |

0x90004 by the fault's page, SB 6 (boot_page.out):

| page | sizes seen | timed out | came up |
|---|---|---|---|
| 0x20006 | 288 x 144 (E848, E891, E892, K2) | 10 | 1 (b2's first replay) |
| 0x20008 | 320 x 400 (E789 a6, K2 k-bif f2) | 2 (1 unique) | 1 (f2) |
| 0x2000a | 640 x 480 | 0 | 15 |
| 0x2000e | te-words-repeat | 0 | 3 |

- The timed-out boots' dumps (boot110.out, boot_clk.out): `CR_CLKGATESTATUS` 0x000ccff8, the
  value during a held TA fault, 54 of 54; `BIF_INT_STAT` 0x000d0004 (requestor bit 2, the TA's
  write) 54 of 54; `BIF_FAULT` 0x20004060 (23), 0x10000050 (13), 0x10002050 (10), 0x1000b050 (5),
  0x20008060 (2) and 0x20006060 (1), all through list 0 (`BIF_FAULT[3:0]`). The 93 boots that came
  up after a 0x90004 read 0x20 or 0x78; over all words two boots that came up read 0xccff8 and
  0xccfa0 (after 0xd2000 and 0x92000). The second boot after a timed-out one came up 54 of 54
  (52 with 0x78, 2 still with 0xccff8; `BIF_INT_STAT` 0x80000 in all).
- The reset before the boot (f5_latch.out), on the kernels that log it: `BIF_FAULT 0x0
  BIF_INT_STAT 0x80000` before CLEAR_FAULT and the same after it, in the 10 boots that timed out
  and the 17 that came up; 120 boots of older kernels have no such line.
- Requestors (reqtab.out, a compilation, 1112 faults): `BIF_FAULT[11:4]` under requestor bit 2
  takes 1, 2, 5, 6, 8 and 12; the bits seen are 1, 2, 3, 7, 8, 9, 10, 12 and 13, so 0, 4, 5, 6,
  11, 14 and 15 are not in the kept logs (bit 5 is E021's transfer write, before these logs).

**What it shows.** The -110 is not a 288 x 144 effect but follows the job's fault page: at
0x20006 the boot times out in 10 of 11, at 0x2000a never in 15, and 320 x 400 (0x20008) timed out
too. It follows only 0x90004: no other fault word was ever followed by a timed-out boot. A boot
that times out has the TA's clocks on and a TA write through list 0 [HW]; read with the fork's
boot (list 0 is `DIR_LIST_BASE0`, the kernel's reset directory at that point) it is the pending
TA write issued inside the boot, through the reset directory, faulting there [infer]. The reset
does not clear that write: the fault registers read clear with every block held in reset before
the boot, and the boot then faults on them again, so "reads clear" at the reset is a reading
taken while held, not proof that the latch was cleared [HW for the reads; infer for the latch].
The firmware's boot is not what clears the registers (they read clear before it). E892's wording
is right for its boot and too narrow for the corpus; no landed claim is contradicted.

**What it does not show.** The rule is a fit on data the planner read: r6-held scores it SEMI,
not held out, and its one miss there (b2's first replay came up at 0x20006) and the fit's (f2 at
0x20008, after E826's writes and a 9.1 s hold) are not explained. Why page 0x20006 to 0x20008 and
not 0x2000a (H-PAGE against H-DONE, the plan's stage d), when in the boot the write is issued
(kernel option K3), whether the latch is cleared or only reads zero while held, and what makes
the SB 5 faults at 0x10000 time out (42 of 67) are open. The sizes' page counts (F2) and the
replay counts (F3) were not compiled here. Nothing here was measured anew: every number is a
reading of kept logs.

**Correction 2026-11-12:** The claim read "for SB 6 (the region headers) it follows the job's fault
page, 10 of 11 at 0x20006 and 0 of 15 at 0x2000a". Round 7's session r7-faults scored R-PAGE held
out (E919): 'H-PAGE REFUTED (2 held, 8 FAILED, 0 cannot tell of 10)'. At 0x20008 the boot came up
after 3 of 3 held resets (320 x 400 twice, 384 x 384) and 6 of 7 boots, at 0x20006 a second size
(256 x 288) came up after its held reset, and 0x20009 (128 x 528), on R-PAGE's up side, timed out;
at 288 x 144 the stage's control and five of six cells of stage m timed out (E920). Read after the
run over d and m, 12 of 17 boots timed out at 0x20006 (11 of 14 at 288 x 144), 1 of 7 at 0x20008,
1 of 3 at 0x20009 and 0 of 2 at 0x2000a: the corpus split came from 0x20006 being met only at 288
x 144 and from one unique 0x20008 timeout, and the -110 after a 0x90004 is neither a page rule nor a
size rule, the same cell going either way. The claim line is edited to say the split did not hold
out; "What it shows" ("not a 288 x 144 effect but follows the job's fault page") is corrected the
same way: it is most frequent at 288 x 144 and follows no page threshold. The counts of the corpus,
the word table, the dumps and the reset readings stand, and every timed-out boot of r7-faults (14)
had the dump this record describes (`CR_CLKGATESTATUS` 0x000ccff8, `BIF_INT_STAT` 0x000d0004, a
fault through list 0) and a second boot that came up.
