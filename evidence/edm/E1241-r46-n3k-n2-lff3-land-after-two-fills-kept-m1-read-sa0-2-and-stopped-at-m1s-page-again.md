+++
id = "E1241"
claim = "r46-n3k-n2 stage lff3 (row LFF3, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WC (E1240) and two stock fills as the begin draws: job 1 done with post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0102298f, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-LFF3 RULE: LFF3-KEEP, LFF3-SA0'; LFF3-KEEP and LFF3-SA0 held, LFF3-PAGE0 FAILED against its prediction (held): LFF2's read and stop a second time"
unit = "edm"
method = "r46-n3k-n2 (render/closing-r46-n3k-n2), stage lff3 of the question-closing pass (round 46: row LFF3, closing29/n3k/design.md section 4.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-n2; attempt out/20261125-160955 (16:10:17; stage lff3 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill,fill), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-45 and the mark, crumbz, land and landq images, their bytes unchanged in the r46 rebuild, which added landr and landp only; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 5115abdc234d44342b4074ff20e3c9322bbddf978151023cb6c7a19cebb299a8 (105 lines), PREDICTIONS.sha256 51c0048ca098029602e2ed6a7de11b5da86aa6e242324ca3e6503d9ea23ba47d (2 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/lff3.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n2-lff3.txt) and again by hand on the kept directory (fold/reproduce-lff3-20261125-160955.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-n2:out/20261125-160955/lff3/", "render-closing-r46-n3k-n2:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM, LF, LF2, LT and LFF byte for byte: Ma and
Mb to attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the
plant WC (E1240), with `begin_draws = "fill,fill"`: between the plant's emit and the image's ran the
plant's disarm and exit resets, this stage's begin reset with two stock fills and the arm [HW, the
stages' kernel logs; DR passed; DK passed: KC begin delta 6]. Jobs: LM's two (E1198): job 1 the emit
on the tick pass, job 2 command 6 on the next tick pass. The question: LFF2's question a second
time, in its own session: (0, 0x04000010) or (2, M1), and page 0 or not (LFF3-KEEP, LFF3-SA0,
LFF3-FILL2, LFF3-TRIPLE, LFF3-PAGE0)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n2-lff3.txt) and again by
hand on the kept directory, the same bytes:

```
SUMMARY: lff3: controls: lff31-a:B: FAILED; lff31-a:J2: FAILED
Q128-N3K-LFF3 RULE: LFF3-KEEP, LFF3-SA0
PREDICTION LFF3-FILL1: predicted failed, read FAILED: held
PREDICTION LFF3-FILL2: predicted failed, read FAILED: held
PREDICTION LFF3-KEEP: predicted held, read held: held
PREDICTION LFF3-OTHER: predicted printed, read FAILED: printed
PREDICTION LFF3-PAGE0: predicted held, read FAILED: FAILED
PREDICTION LFF3-SA0: predicted held, read held: held
PREDICTION LFF3-SERVE: predicted failed, read FAILED: held
PREDICTION LFF3-TRIPLE: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage wc), PG, E0, T0, J1, DR, DK and SV passed; B (BIF_FAULT 0 after the row) and
J2 (job 2 done) failed, read by LFF3-PAGE0 and LFF3-SERVE (the outcomes that name the stop).
LFF3-KEEP and LFF3-SA0 held as predicted. **LFF3-PAGE0 failed against its prediction (held): the
fault is at 0x005d1000, M1's page, not page 0.** LFF3-FILL2, LFF3-FILL1, LFF3-TRIPLE and LFF3-SERVE
failed as predicted; LFF3-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0102298f, sa13 = pa1 = M13; post sa3-sa31
  and pa0-pa15 equal WC's word for word (sa24 and sa26, pa12 and pa14, already held land's markers
  Ma and Mb, from the session before). The survey's pre read sa0 = V0, sa2 = V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x005d100f** (list 15, page
  0x005d1000; the scorer: job 1's post sa1), post the same; job 2 not done (cmd_after 6, dwords
  224-255 still 0xdeadc0de); the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r46-n3k-logs/health-r46-n3k-n2.log).
- The kernel: the arm after the fills "2 events seen"; KC begin 6, as two fills give; the end KC
  cannot tell (no exit load after the stop).

**What it shows.** LFF2's read and stop came back in a session of their own: land after a plant and
two fills kept M1, read sa0 2 and a timer word, and stopped at M1's page **[HW, LFF2 E1239 and
LFF3]**. On this module two reads of the list agree and none disagrees, while LFF (E1217, module
079DD0D1) read (0, 0x04000010) and stopped at page 0: across modules the reads of the list disagree
in sa0, sa1 and the stop's page **[HW]**. Every earlier stop with sa0 below one page went to page 0
(six of six: LC, LC2 on module 83FBFD86, E1176, E1178; LF on 079DD0D1, E1200; LF2, LT, LFF on
079DD0D1, E1213, E1215, E1217), and the two with this very bank (2, M1), LF and LF2, came after one
fill. Against those two this round's stops differ in two things at once, the number of fills before
land (two or three, against one) and the module (10BBF3BF, against 079DD0D1), and no row splits
them; LFF's two fills on 079DD0D1 stopped at page 0 but with another bank (0, 0x04000010)
**[infer]**.

**What it does not show.** Why the stop's page moved from page 0 to sa1's with the same kind of
bank; one run of this stage.
