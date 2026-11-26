+++
id = "E1257"
claim = "r46-n3k-n15 stage r2 (row R2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image landr at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant W15 (E1256) and no draws: landr wrote 0x04400000 to attribute 0 and M1 0x005d1000 to attribute 1; job 1 done with post sa0 0x04400000, sa1 = M1, sa2 = V2 0x32002000, sa12 = V0, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-R2 RULE: R2-E12, R2-LOW, R2-WRITE'; every prediction held (R2-SA0, R2-SUM and R2-SERVE failed as predicted, R2-OTHER (printed) read failed): with two pages known unmapped in sa0 and sa1 the stop faulted at sa1's, the lower, R's read and stop (E1253) a second time"
unit = "edm"
method = "r46-n3k-n15 (render/closing-r46-n3k-n15), stage r2 of the question-closing pass (round 46's addendum: row R2, closing29/n3k/design.md section 4.8 and 11.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 11.9: G=a, H=a, I=a, J=a, K=a; run after section 11.8's stop for the user (LFK and LFK2 disagreed), the user choosing N13-N16 and skipping N12), dataset render-closing-r46-n3k-n15; attempt out/20261126-080300 (08:03:22; stage r2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 and of its addendum on that one boot, no rebuild, install or boot since N4, post sa12 = V0 in every row of the addendum (the outcome E12); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK), K10's arm words pds=landr and pds=landp and K11's PAD control, armed in N12 only, which did not run (kit/ = resgx545 b4e31c76, branch r46-n3k2 on r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landr pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-46 and the mark, land, landr and landp images of the running module (round 46's build, E1234-E1245); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 564c9f6287a983f9dd26e1e983f2c0236bdef7e03df9e7425081084d1e69dbe8 (144 lines), PREDICTIONS.sha256 1409c9c415ec92ad46aa2343851714a1dd14fdab0e98877ae0914f1ac13e08da (2 files), pins in FROZEN.commits (the kit and the blob sources at b4e31c76; round 45's kept stages of r45-n3j-n2 to -n6, the scorer's fixtures, at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/r2.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n15-r2.txt) and again by hand on the kept directory (fold/reproduce-r2-20261126-080300.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-26"
data = ["render-closing-r46-n3k-n15:out/20261126-080300/r2/", "render-closing-r46-n3k-n15:fold/"]
terms = []
+++
**What ran.** landr (landq with its word to attribute 0 0x005d2000 changed to 0x04400000, the page
the BIF faulted at in LV, E1183, and nothing else: Ma and Mb to attributes 24 and 26, 0x04400000 to
attribute 0 and M1 to attribute 1, then land's `doutu` and `halt`; no `tim`, so the tick runs) right
after the plant W15 (E1256), with `begin_draws = "none"`: between the plant's emit and the image's
ran the plant's disarm and exit resets, this stage's begin reset with the register health (no draw)
and the arm [HW, the stages' kernel logs; DR and DK read ok, printed: KC begin delta 2]. Jobs: LM's
two (E1198): job 1 the emit on the tick pass, job 2 command 6 on the next tick pass. The question:
row R again (decision J (a)), byte for byte but its names: with 0x04400000 in sa0 (the page LV
faulted at, E1183) over M1 in sa1, both pages known unmapped, does the stop fault at the lower,
sa1's (R-LOW: the lowest faulting page kept), at sa0's (R-SA0: sa0 read first), or at sa0 + sa12 =
0x36404000 (R-SUM: C-E0+), with sa12 = V0 (R-E12)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n15-r2.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: r2: controls: r21-a:B: FAILED; r21-a:J2: FAILED
Q128-N3K-R2 RULE: R2-E12, R2-LOW, R2-WRITE
PREDICTION R2-E12: predicted held, read held: held
PREDICTION R2-LOW: predicted held, read held: held
PREDICTION R2-OTHER: predicted printed, read FAILED: printed
PREDICTION R2-SA0: predicted failed, read FAILED: held
PREDICTION R2-SERVE: predicted failed, read FAILED: held
PREDICTION R2-SUM: predicted failed, read FAILED: held
PREDICTION R2-WRITE: predicted held, read held: held
```

PG, E0, T0, J1 and SV passed, PLANT (W-SA1 of stage w15) too, printed only (landr writes sa0 and sa1
itself); DR and DK read ok (printed in the ROW line); B (BIF_FAULT 0 after the row) and J2 (job 2
done) failed, read by R2-LOW, R2-SA0, R2-SUM and R2-SERVE (the outcomes that name the stop). Every
prediction held: R2-WRITE, R2-LOW and R2-E12 held; R2-SA0, R2-SUM and R2-SERVE failed as predicted;
R2-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x04400000, sa1 = M1 0x005d1000, sa2 = V2 0x32002000 (the plant's, kept: sa02kind
  OTHER), sa12 = pa0 = V0, sa13 = pa1 = M13, sa24 = pa12 Ma and sa26 = pa14 Mb; the other post
  sa3-sa31 and pa equal W15's word for word.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x005d100f** (list 15, page
  0x005d1000; the scorer: job 1's post sa1), post the same; job 2 not done; the tick stopped; snap9
  and the stop dump the same fault. The kit's reset and both draws recovered it (health ok,
  closing29/r46-n3k-logs/health-r46-n3k-n15.log).
- The kernel: the arm with no draws "0 events seen"; KC begin N0 495, delta 2; the end KC cannot
  tell.

**What it shows.** Row R's read and stop came back in a session of their own: landr's words in sa0
and sa1, and the stop at M1's page, the lower of two unmapped pages, not at sa0's and not at sa0 +
sa12 **[HW, R E1253 and R2]**: two reads agree and none disagrees. R-SA0 is out for this bank on two
reads **[HW against the frozen alternative]**.

**What it does not show.** Which access of the tick pass read M1's page; what page 0 does on this
boot; one run of this stage.
