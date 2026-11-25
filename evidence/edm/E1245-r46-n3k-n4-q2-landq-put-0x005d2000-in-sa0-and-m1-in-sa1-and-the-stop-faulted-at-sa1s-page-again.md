+++
id = "E1245"
claim = "r46-n3k-n4 stage q2 (row Q2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image landq at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WE (E1244) and no draws: landq wrote Q0 0x005d2000 to attribute 0 and M1 0x005d1000 to attribute 1; job 1 done with post sa0 = Q0, sa1 = M1, sa2 = V2 0x32002000, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-Q2 RULE: Q2-SAME, Q2-WRITE'; every prediction held: row Q's read and stop (E1233) a second time, on another module"
unit = "edm"
method = "r46-n3k-n4 (render/closing-r46-n3k-n4), stage q2 of the question-closing pass (round 46: row Q2, closing29/n3k/design.md section 4.7; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-n4; attempt out/20261125-161145 (16:12:06; stage q2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landq pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-45 and the mark, crumbz, land and landq images, their bytes unchanged in the r46 rebuild, which added landr and landp only; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 2bd1afb798f97b9c7d99c4cbb4d6352d6bd2794201f0e72cb0c08e72727906dd (105 lines), PREDICTIONS.sha256 49eb21b522a280c9d39df099b5c39308d018d29c2bd7c68904af66764dcfa87f (2 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/q2.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n4-q2.txt) and again by hand on the kept directory (fold/reproduce-q2-20261125-161145.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-n4:out/20261125-161145/q2/", "render-closing-r46-n3k-n4:fold/"]
terms = []
+++
**What ran.** landq (18 dwords: land's 12 data dwords with its third row holding Q0 0x005d2000, M1
0x005d1000 and their `douta` controls; land's two marker `douta`, then Q0 to attribute 0 and M1 to
attribute 1, then land's `doutu` and `halt`; no `tim`, so the tick runs) right after the plant WE
(E1244), with `begin_draws = "none"`: between the plant's emit and the image's ran the plant's
disarm and exit resets, this stage's begin reset with the register health (no draw) and the arm [HW,
the stages' kernel logs; DR passed; DK passed: KC begin delta 2]. Jobs: LM's two (E1198): job 1 the
emit on the tick pass, job 2 command 6 on the next tick pass. The question: row Q again (E1233),
byte for byte: landq's words read back (Q2-WRITE), and the stop at 0x005d1000 (Q2-SAME) or at
0x005d2000 (Q2-SA0)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n4-q2.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: q2: controls: q21-a:B: FAILED; q21-a:J2: FAILED
Q128-N3K-Q2 RULE: Q2-SAME, Q2-WRITE
PREDICTION Q2-OTHER: predicted printed, read FAILED: printed
PREDICTION Q2-SA0: predicted failed, read FAILED: held
PREDICTION Q2-SAME: predicted held, read held: held
PREDICTION Q2-SERVE: predicted failed, read FAILED: held
PREDICTION Q2-WRITE: predicted held, read held: held
```

PG, E0, T0, J1, SV and PLANT (W-SA1 of stage we, printed only: landq writes sa0 and sa1 itself)
passed; DR and DK read ok (printed in the ROW line); B (BIF_FAULT 0 after the row) and J2 (job 2
done) failed, read by Q2-SAME, Q2-SA0 and Q2-SERVE (the outcomes that name the stop). Every
prediction held: Q2-WRITE and Q2-SAME held; Q2-SA0 and Q2-SERVE failed as predicted; Q2-OTHER
(printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x005d2000 = Q0, sa1 0x005d1000 = M1, sa2 0x32002000 = V2 (WE's plant kept), sa13
  = pa1 = M13, sa24 = pa12 Ma 0x5a5a3a18 and sa26 = pa14 Mb 0x5a5a3a1a; the other post sa3-sa31 and
  pa equal WE's word for word (WE's sa24 and sa26 already held Ma and Mb, from N3's land read).
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x005d100f (list 15, page 0x005d1000),
  post the same; job 2 not done; the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r46-n3k-logs/health-r46-n3k-n4.log).
- The kernel: q2's arm with no draws "0 events seen"; KC begin 2; the end KC cannot tell.

**What it shows.** Row Q reproduces on another module: landq's words are sa0 and sa1 in the same
row, and with Q0 in sa0 and M1 in sa1 the early stop faulted at M1's page **[HW, Q E1233 on EC553F41
and Q2 on 10BBF3BF]**: two reads agree and none disagrees. Whether 0x005d2000 is mapped stays unread
(rows P and P2 of the design were not run) **[open]**.

**What it does not show.** Whether 0x005d2000 is mapped; why this bank's stop page held across two
modules while the (2, M1) bank's did not; one run of this stage.
