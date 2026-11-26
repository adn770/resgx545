+++
id = "E1258"
claim = "r46-n3k-n16 stage w16 (row W, the plant before P2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): row W (E1184) byte for byte, one job, no gate and no end draws: job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0, sa2 = V2; K5 BIF_FAULT 0 before and after and in snap9; every control passed, 'Q128-N3K-W16 RULE: W-QUIET, W-SA1, W-SA13', every prediction held: W reproduced, its 36th run"
unit = "edm"
method = "r46-n3k-n16 (render/closing-r46-n3k-n16), stage w16 of the question-closing pass (round 46's addendum: row W, closing29/n3k/design.md section 11.3 and 11.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 11.9: G=a, H=a, I=a, J=a, K=a; run after section 11.8's stop for the user (LFK and LFK2 disagreed), the user choosing N13-N16 and skipping N12), dataset render-closing-r46-n3k-n16; attempt out/20261126-080355 (08:03:56; stage w16 ended rc 0 and the driver scored it, score-w16.txt; stage p2 followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 and of its addendum on that one boot, no rebuild, install or boot since N4, post sa12 = V0 in every row of the addendum (the outcome E12); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK), K10's arm words pds=landr and pds=landp and K11's PAD control, armed in N12 only, which did not run (kit/ = resgx545 b4e31c76, branch r46-n3k2 on r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and its begin health (fill and triangle), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none) and no end draws (end_draws none): the disarm reset and the register health only; the blob and form of rounds 42-46 and the mark, land, landr and landp images of the running module (round 46's build, E1234-E1245); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 de917b873928dca0894e4254be31e873d5853940dcfd845d157b7c7f9d116929 (144 lines), PREDICTIONS.sha256 0fa7de8bf45b5ce6723fa338a5cb2238e25d3bcf55283fced589ae5249ae9196 (2 files), pins in FROZEN.commits (the kit and the blob sources at b4e31c76; round 45's kept stages of r45-n3j-n2 to -n6, the scorer's fixtures, at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/w16.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-w16-20261126-080355.out, the same bytes as score-w16.txt and as closing29/r46-n3k-logs/score-r46-n3k-n16-w16.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW"]
date = "2026-11-26"
data = ["render-closing-r46-n3k-n16:out/20261126-080355/w16/", "render-closing-r46-n3k-n16:fold/"]
terms = []
+++
**What ran.** Row W (E1184, E1186) byte for byte: the mark image (crumb3, which sends V0 to
attribute 0 and V2 to attribute 2, plus M13 0x005d3000 to attribute 13 and M1 0x005d1000 to
attribute 1, with T3 stopping the tick) as one job, no kick and no command after it, no gate and no
end draws (K7), so that the next stage, P2, starts from M1 in attribute 1. The first stage of N16,
after N15's stop and the recovery's two draws.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: w16: controls: every control passed
Q128-N3K-W16 RULE: W-QUIET, W-SA1, W-SA13
PREDICTION W-FAULT: predicted failed, read FAILED: held
PREDICTION W-QUIET: predicted held, read held: held
PREDICTION W-SA1: predicted held, read held: held
PREDICTION W-SA13: predicted held, read held: held
```

Every control passed (PG, E0, T0, B, J1, SV). Every prediction held: W-QUIET, W-SA1 and W-SA13 held,
W-FAULT failed as predicted.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 8 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0 0x32004000,
sa2 = V2 0x32002000, sa12 = pa0 = V0; post sa3-sa31 and pa0-pa15 equal the session's land read's
word for word, and every stage's of the addendum, and N4's q2's (E1245): sa24 and sa26 (pa12, pa14)
still hold land's markers Ma and Mb (fold/FOLD-NOTES.md, printed). The kernel: the arm after the
begin draws, fill and triangle; KC begin N0 517, delta 10, and end delta 2, as K9 expects; no fault
line.

**What it shows.** Row W reproduces: the word sent to attribute 1 with 0xc43 is sa1 in the row that
sends it, and with no pass after the emit nothing faults **[HW]** (its 36th run, every one quiet).

**What it does not show.** What the next stage's draws do to the word (that stage's record); one run
of this stage.
