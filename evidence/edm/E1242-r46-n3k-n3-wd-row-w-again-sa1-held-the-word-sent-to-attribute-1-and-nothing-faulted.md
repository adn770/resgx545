+++
id = "E1242"
claim = "r46-n3k-n3 stage wd (row W, the plant before LF3F, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): row W (E1184) byte for byte, one job, no gate and no end draws: job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0, sa2 = V2; K5 BIF_FAULT 0 before and after and in snap9; every control passed, 'Q128-N3K-WD RULE: W-QUIET, W-SA1, W-SA13', every prediction held: W reproduced, its 28th run"
unit = "edm"
method = "r46-n3k-n3 (render/closing-r46-n3k-n3), stage wd of the question-closing pass (round 46: row W, closing29/n3k/design.md section 4.2; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-n3; attempt out/20261125-161049 (16:10:49; stage wd ended rc 0 and the driver scored it, score-wd.txt; stage lf3f followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and its begin health (fill and triangle), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none) and no end draws (end_draws none): the disarm reset and the register health only; the blob and form of rounds 42-45 and the mark, crumbz, land and landq images, their bytes unchanged in the r46 rebuild, which added landr and landp only; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 76957096e54fb63bf52f18e7efef62c1d7f1ef209f7a1981a3f23874d043ae31 (105 lines), PREDICTIONS.sha256 89aa15228f28baa61b16f8d9c1d3dcffa28c97b242698aad7d052a71d299cd12 (2 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/wd.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-wd-20261125-161049.out, the same bytes as score-wd.txt and as closing29/r46-n3k-logs/score-r46-n3k-n3-wd.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-n3:out/20261125-161049/wd/", "render-closing-r46-n3k-n3:fold/"]
terms = []
+++
**What ran.** Row W (E1184, E1186) byte for byte: the mark image (crumb3, which sends V0 to
attribute 0 and V2 to attribute 2, plus M13 0x005d3000 to attribute 13 and M1 0x005d1000 to
attribute 1, with T3 stopping the tick) as one job, no kick and no command after it, no gate and no
end draws (K7), so that the next stage, LF3F, starts from M1 in attribute 1. The first stage of N3,
after N2's stop and the recovery's two draws.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: wd: controls: every control passed
Q128-N3K-WD RULE: W-QUIET, W-SA1, W-SA13
PREDICTION W-FAULT: predicted failed, read FAILED: held
PREDICTION W-QUIET: predicted held, read held: held
PREDICTION W-SA1: predicted held, read held: held
PREDICTION W-SA13: predicted held, read held: held
```

Every control passed (PG, E0, T0, B, J1, SV). Every prediction held: W-QUIET, W-SA1 and W-SA13 held,
W-FAULT failed as predicted.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0 0x32004000,
sa2 = V2 0x32002000; post sa3-sa31 and pa0-pa15 equal the session's land read's word for word, sa24
and sa26 (pa12, pa14) holding land's markers Ma and Mb from the session before (fold/FOLD-NOTES.md,
printed). The kernel: the arm after the begin draws, fill and triangle, "3 events seen"; KC begin 10
and end 2, as K9 expects; no fault line.

**What it shows.** Row W reproduces: the word sent to attribute 1 with 0xc43 is sa1 in the row that
sends it, and with no pass after the emit nothing faults **[HW]** (its 28th run, every one quiet).

**What it does not show.** What the next stage's draws do to the word (that stage's record); one run
of this stage.
