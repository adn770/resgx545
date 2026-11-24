+++
id = "E1197"
claim = "r44-n3i-n2 stage wl (row W, the plant before LM, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): row W (E1184) byte for byte, one job, no gate and no end draws: job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, the post sa0-sa31 equal to W's; K5 BIF_FAULT 0 before and after and in snap9; every control passed, 'Q128-N3I-WL RULE: W-QUIET, W-SA1, W-SA13', every prediction held: W reproduced, its 7th run"
unit = "edm"
method = "r44-n3i-n2 (render/closing-r44-n3i-n2), stage wl of the question-closing pass (round 44: row W, closing29/n3i/design.md section 3.1; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r44-n3i-n2; attempt out/20261124-010001 (01:00:01; stage wl ended rc 0 and the driver scored it, score-wl.txt; stage lm followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 44; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws and K8's draw lists (begin_draws a comma list of fill and tri, run once in order, each draw kept and exact) (kit/ = resgx545 ce01a0c4, branch r44-n3i, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at ce01a0c4; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and its begin health (fill and triangle, the session's first stage, after N1), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none) and no end draws (end_draws none): the disarm reset and the register health only; the blob and form of rounds 42-43 and the mark and crumb3 images, unchanged on the running module (E1180, E1184-E1187); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 2703a95fd7a7ee8e3f0d9ed371fcffe7703264ba2004865bd541435049f89344 (66 lines), PREDICTIONS.sha256 b8862f8fb1181dda015dda98001425c716e4549313d01544df61dee0d6b96889 (2 files), pins in FROZEN.commits (the kit and the blob sources at ce01a0c4; round 43's kept stages N1 w, N1 v and N2 f at data b3df8fc21; t30's source 42c4de7); the frozen predictions predictions/wl.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-wl-20261124-010001.out, the same bytes as score-wl.txt); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW"]
date = "2026-11-24"
data = ["render-closing-r44-n3i-n2:out/20261124-010001/wl/", "render-closing-r44-n3i-n2:fold/"]
terms = []
+++
**What ran.** Row W (E1184, E1186) byte for byte: the mark image (crumb3 plus M13 0x005d3000 to
attribute 13 and M1 0x005d1000 to attribute 1, with T3 stopping the tick) as one job, no kick and no
command after it, no gate and no end draws (K7), so that the next stage, LM, starts from M1 in
attribute 1. The first stage of N2, after N1's last stage and its end draws.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: wl: controls: every control passed
Q128-N3I-WL RULE: W-QUIET, W-SA1, W-SA13
PREDICTION W-FAULT: predicted failed, read FAILED: held
PREDICTION W-QUIET: predicted held, read held: held
PREDICTION W-SA1: predicted held, read held: held
PREDICTION W-SA13: predicted held, read held: held
```

Every control passed (PG, E0, T0, B, J1). Every prediction held: W-QUIET, W-SA1 and W-SA13 held,
W-FAULT failed as predicted.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0 0x32004000,
sa2 = V2 0x32002000; post sa0-sa31 and pa0-pa15 equal W's (E1184) word for word. The kernel: the arm
after the begin draws, fill and triangle, "3 events seen"; no fault line.

**What it shows.** Row W reproduces: the word sent to attribute 1 with 0xc43 is sa1 in the row that
sends it, and with no pass after the emit nothing faults **[HW]** (its 7th run, every one quiet).

**What it does not show.** What the next stage's draws do to the word (that stage's record); one run
of this stage.
