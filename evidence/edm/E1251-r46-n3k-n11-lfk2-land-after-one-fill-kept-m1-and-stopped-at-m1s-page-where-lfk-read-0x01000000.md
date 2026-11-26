+++
id = "E1251"
claim = "r46-n3k-n11 stage lfk2 (row LFK2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): LFK's stage again, after the plant W11 (E1250) and one stock fill as the begin draws: job 1 done with post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0101bf25, sa12 = V0, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-LFK2 RULE: LFK2-E12, LFK2-M1, LFK2-SA'; every prediction held (LFK2-PAGE0 and LFK2-SERVE failed as predicted, LFK2-OTHER (printed) read failed): one fill kept M1 and the stop faulted at M1's page, where LFK (E1247) read 0x01000000 and stopped there"
unit = "edm"
method = "r46-n3k-n11 (render/closing-r46-n3k-n11), stage lfk2 of the question-closing pass (round 46's addendum: row LFK2, closing29/n3k/design.md section 11.3 and 11.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 11.9: G=a, H=a, I=a, J=a, K=a), dataset render-closing-r46-n3k-n11; attempt out/20261125-231324 (23:13:46; stage lfk2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 and of its addendum on that one boot, no rebuild, install or boot since N4, post sa12 = V0 in every row of the addendum (the outcome E12); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK), K10's arm words pds=landr and pds=landp and K11's PAD control, armed in N12 only, which did not run (kit/ = resgx545 b4e31c76, branch r46-n3k2 on r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-46 and the mark, land, landr and landp images of the running module (round 46's build, E1234-E1245); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 936b6b25727450eb82aa099b6a3680df4f1ff755f72dcb144589a784a412884a (144 lines), PREDICTIONS.sha256 f74c9e303cc1c7bfbbee880e092a3170731e13fd5f4d5ba7316a80056b100249 (2 files), pins in FROZEN.commits (the kit and the blob sources at b4e31c76; round 45's kept stages of r45-n3j-n2 to -n6, the scorer's fixtures, at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/lfk2.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n11-lfk2.txt) and again by hand on the kept directory (fold/reproduce-lfk2-20261125-231324.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-26"
data = ["render-closing-r46-n3k-n11:out/20261125-231324/lfk2/", "render-closing-r46-n3k-n11:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM, LF, LF2, LT, LFF and LFF2 byte for byte:
Ma and Mb to attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right
after the plant W11 (E1250), with `begin_draws = "fill"`: between the plant's emit and the image's
ran the plant's disarm and exit resets, this stage's begin reset with one stock fill and the arm
[HW, the stages' kernel logs; DR passed; DK passed: KC begin delta 4]. Jobs: LM's two (E1198): job 1
the emit on the tick pass, job 2 command 6 on the next tick pass. The question: LFK's second read
(decision G (a)): page 0 (LFK2-PAGE0) or M1's page (LFK2-M1), with (2, M1, a timer word) (LFK2-SA)
and sa12 = V0 (LFK2-E12)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n11-lfk2.txt) and again by
hand on the kept directory, the same bytes:

```
SUMMARY: lfk2: controls: lfk21-a:B: FAILED; lfk21-a:J2: FAILED
Q128-N3K-LFK2 RULE: LFK2-E12, LFK2-M1, LFK2-SA
PREDICTION LFK2-E12: predicted held, read held: held
PREDICTION LFK2-M1: predicted held, read held: held
PREDICTION LFK2-OTHER: predicted printed, read FAILED: printed
PREDICTION LFK2-PAGE0: predicted failed, read FAILED: held
PREDICTION LFK2-SA: predicted held, read held: held
PREDICTION LFK2-SERVE: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage w11), PG, E0, T0, J1, DR, DK and SV passed; B (BIF_FAULT 0 after the row) and
J2 (job 2 done) failed, read by LFK2-M1, LFK2-PAGE0 and LFK2-SERVE (the outcomes that name the
stop). Every prediction held: LFK2-E12, LFK2-M1 and LFK2-SA held; LFK2-PAGE0 and LFK2-SERVE failed
as predicted; LFK2-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0101bf25 (an EVENT_TIMER sample's shape,
  sa02kind LF), sa12 = pa0 = V0 0x32004000, sa13 = pa1 = M13; post sa3-sa31 and pa0-pa15 equal W11's
  word for word (sa24 and sa26, pa12 and pa14, already held land's markers Ma and Mb).
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x005d100f** (list 15, page
  0x005d1000; the scorer: job 1's post sa1), post the same; job 2 not done (cmd_after 6, dwords
  224-255 still 0xdeadc0de); the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r46-n3k-logs/health-r46-n3k-n11.log).
- The kernel: the arm's stop line "1 events seen"; KC begin N0 382, delta 4, as one fill gives; HKC
  (printed): fill 1: 3:4 K 2 0x02000010; the end KC cannot tell (no exit load after the stop).

**What it shows.** One fill on this module, boot and sa12 again stopped at sa1's page, not at page
0: LFK and LFK2 agree that one fill does not stop at page 0 here **[HW, two reads]**, so C-FILL is
out on this boot, and LF's and LF2's page 0 (E1200, E1213: one fill, module 079DD0D1, sa12 3 or 0)
differ from these in the module, the boot, K and sa12 together **[infer]**. sa0 read 2, as in LFK,
LF, LF2 and ZF **[HW]**. But sa1 read M1 here and 0x01000000 in LFK, the same stage two minutes
apart on one boot and one build, and the stop's page followed sa1 both times **[HW]**: the one-fill
sa1, and with it the page land stops at, is not stable on this boot. The design's stop rule for that
case (LFK and LFK2 disagreeing, section 11.8) held N12-N16 for the user. That timing decides which
word the emit's pass reads (H-RACE) is the reading carried **[infer]**; nothing here measures it.

**What it does not show.** What makes one fill leave M1 or 0x01000000; whether K (C-K) or a low sa12
(C-E0 against C-MOD) brings page 0 back (row LFKP, N12, was not run); one run of this stage.
