+++
id = "E1239"
claim = "r46-n3k-n1 stage lff2 (row LFF2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WB (E1238) and two stock fills as the begin draws: job 1 done with post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x01015e75, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-LFF2 RULE: LFF2-KEEP, LFF2-SA0'; LFF2-KEEP and LFF2-SA0 held, LFF2-PAGE0 FAILED against its prediction (held): land after two fills kept M1 and read sa0 2, not LFF's 0x04000010 and 0, and the stop faulted at M1's page, not at page 0"
unit = "edm"
method = "r46-n3k-n1 (render/closing-r46-n3k-n1), stage lff2 of the question-closing pass (round 46: row LFF2, closing29/n3k/design.md section 4.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-n1; attempt out/20261125-160752 (16:08:58; stage lff2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill,fill), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-45 and the mark, crumbz, land and landq images, their bytes unchanged in the r46 rebuild, which added landr and landp only; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 7dba4dade3969cefedfa07512de743d5933f41963d85b8bab803fbd73f4b90a2 (109 lines), PREDICTIONS.sha256 870969762787c6fba3f3b3aef8d6cb46c7dc56be3ee4a022eaa8e3f3c108dc9c (4 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/lff2.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n1-lff2.txt) and again by hand on the kept directory (fold/reproduce-lff2-20261125-160752.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-n1:out/20261125-160752/lff2/", "render-closing-r46-n3k-n1:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM, LF, LF2, LT and LFF byte for byte: Ma and
Mb to attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the
plant WB (E1238), with `begin_draws = "fill,fill"`: between the plant's emit and the image's ran the
plant's disarm and exit resets, this stage's begin reset with two stock fills and the arm [HW, the
stages' kernel logs; DR passed; DK passed: KC begin delta 6]. Jobs: LM's two (E1198): job 1 the emit
on the tick pass, job 2 command 6 on the next tick pass. The question: does land after two fills
read LFF's (0, 0x04000010, a timer word) again (LFF2-FILL2, LFF2-TRIPLE: H-FL) or keep M1 with sa0 2
(LFF2-KEEP, LFF2-SA0: H-TRI), and does it stop at page 0, as every stop with sa0 below one page did
(LFF2-PAGE0)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n1-lff2.txt) and again by
hand on the kept directory, the same bytes:

```
SUMMARY: lff2: controls: lff21-a:B: FAILED; lff21-a:J2: FAILED
Q128-N3K-LFF2 RULE: LFF2-KEEP, LFF2-SA0
PREDICTION LFF2-FILL1: predicted failed, read FAILED: held
PREDICTION LFF2-FILL2: predicted failed, read FAILED: held
PREDICTION LFF2-KEEP: predicted held, read held: held
PREDICTION LFF2-OTHER: predicted printed, read FAILED: printed
PREDICTION LFF2-PAGE0: predicted held, read FAILED: FAILED
PREDICTION LFF2-SA0: predicted held, read held: held
PREDICTION LFF2-SERVE: predicted failed, read FAILED: held
PREDICTION LFF2-TRIPLE: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage wb), PG, E0, T0, J1, DR, DK and SV passed; B (BIF_FAULT 0 after the row) and
J2 (job 2 done) failed, read by LFF2-PAGE0 and LFF2-SERVE (the outcomes that name the stop).
LFF2-KEEP and LFF2-SA0 held as predicted. **LFF2-PAGE0 failed against its prediction (held): the
fault is at 0x005d1000, M1's page, not page 0.** LFF2-FILL2, LFF2-FILL1, LFF2-TRIPLE and LFF2-SERVE
failed as predicted; LFF2-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x01015e75, sa13 = pa1 = M13; post sa3-sa31
  and pa0-pa15 equal WB's word for word but for sa24 and sa26 (pa12, pa14), land's markers Ma
  0x5a5a3a18 and Mb 0x5a5a3a1a. The survey's pre read sa0 = V0, sa2 = V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x005d100f** (list 15, page
  0x005d1000; the scorer: job 1's post sa1), post the same; job 2 not done (cmd_after 6, dwords
  224-255 still 0xdeadc0de); the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r46-n3k-logs/health-r46-n3k-n1.log).
- The kernel: the arm after the fills "2 events seen"; KC begin 6, as two fills give; the end KC
  cannot tell (no exit load after the stop).

**What it shows.** Land after a plant and two fills kept M1 in attribute 1 and read sa0 2 and a
timer word in sa2 **[HW]**: LFF's (0, 0x04000010) (E1217) did not repeat, and the list's sa1 has now
read M1 six times (FF, FF2, ZFF, ZFF2, LFF2, LFF3) against LFF's once **[HW]**, so an image effect
of land's running tick (H-FL) is not what LFF read **[HW against LFF2-FILL2]**. The stop faulted at
page 0x005d1000, sa1's page, with sa0 2 **[HW]**: the bank LF and LF2 stopped with at page 0 (2, M1,
E1200, E1213) stopped here at M1's page. Every earlier stop with sa0 below one page went to page 0
(six of six: LC, LC2 on module 83FBFD86, E1176, E1178; LF on 079DD0D1, E1200; LF2, LT, LFF on
079DD0D1, E1213, E1215, E1217), and the two with this very bank (2, M1), LF and LF2, came after one
fill. Against those two this round's stops differ in two things at once, the number of fills before
land (two or three, against one) and the module (10BBF3BF, against 079DD0D1), and no row splits
them; LFF's two fills on 079DD0D1 stopped at page 0 but with another bank (0, 0x04000010)
**[infer]**. Both readings Q (E1233) left, the lowest faulting page kept (R-LOW) and sa0 read first
(R-SA0), predicted page 0 here; neither fits this stop if sa0's 2 is read as an address **[infer]**.

**What it does not show.** Whether the fill count or the module moved the page; which access of the
tick pass read M1's page; one run of this stage.
