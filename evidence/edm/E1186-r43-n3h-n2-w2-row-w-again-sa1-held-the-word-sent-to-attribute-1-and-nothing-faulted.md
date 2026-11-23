+++
id = "E1186"
claim = "r43-n3h-n2 stage w2 (row W2, row W again, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after N1's recovery draws, row W (E1184) byte for byte: job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13, the post sa0-sa31 equal to W's; K5 BIF_FAULT 0 before and after and in snap9; every control passed, 'Q128-N3H-W2 RULE: W-QUIET, W-SA1, W-SA13', every prediction held: W reproduced"
unit = "edm"
method = "r43-n3h-n2 (render/closing-r43-n3h-n2), stage w2 of the question-closing pass (round 43: row W2, closing29/n3h/design.md section 3.3; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r43-n3h-n2; attempt out/20261123-164448 (16:44:48; stage w2 ended rc 0 and the driver scored it, score-w2.txt; stage f followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 43; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it and, for a kicked job, right after the kick's reply (K5, K6's mid), K6's kick-only job and K7's per-stage draws (kit/ = resgx545 1f49335c, branch r43-n3h, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at 1f49335c; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and its begin health (fill and triangle, the session's first stage), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none) and no end draws (end_draws none): the disarm reset and the register health only; the blob, images and form of round 42, unchanged on the running module (E1180, E1182, E1183); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 d4de03ee82e5369ceaef6e4d3eeaede11923baa3123e1218abfbe10ee41697e5 (62 files), PREDICTIONS.sha256 c5b5f9dbff28ee85902364f5dc7420fe285911cf0df6af926a281f22736165db (2 files), pins in FROZEN.commits (the kit and the blob sources at 1f49335c; round 42's kept stages G1 m and G3 lv at data fadfa30a; t30's source 42c4de7); the frozen predictions predictions/w2.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-w2-20261123-164448.out, the same bytes as score-w2.txt); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW"]
date = "2026-11-23"
data = ["render-closing-r43-n3h-n2:out/20261123-164448/w2/", "render-closing-r43-n3h-n2:fold/"]
terms = []
+++
**What ran.** Row W (E1184) byte for byte, first in session N2, after N1's last stage had ended in
its stop and the recovery's two draws. Needed again so that row F's sa1 reading starts from a
planted M1.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: w2: controls: every control passed
Q128-N3H-W2 RULE: W-QUIET, W-SA1, W-SA13
PREDICTION W-FAULT: predicted failed, read FAILED: held
PREDICTION W-QUIET: predicted held, read held: held
PREDICTION W-SA1: predicted held, read held: held
PREDICTION W-SA13: predicted held, read held: held
```

Every control passed. Every prediction held; W-FAULT failed as predicted.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa0-sa31 and pa0-pa15 equal W's word for word: sa1 = M1, sa13 = pa1 =
M13. The kernel: the arm after both begin draws "3 events seen"; no fault line.

**What it shows.** W reproduces: the word sent to attribute 1 is sa1 in the row that sends it, and
with no pass after the emit nothing faults **[HW]**, now 2 of 2 (with M, E1180, 3 rows read sa1 =
M1).

**What it does not show.** As E1184.
