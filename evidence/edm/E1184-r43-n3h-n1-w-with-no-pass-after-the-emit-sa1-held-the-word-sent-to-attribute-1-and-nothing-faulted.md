+++
id = "E1184"
claim = "r43-n3h-n1 stage w (row W, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): row M's image (E1180) as one job, T3 stopping the tick, no gate and no end draws: job 1's post sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0, sa2 = V2, sa12-sa27 = pa0-pa15; K5 BIF_FAULT 0 before and after and in snap9; every control passed, 'Q128-N3H-W RULE: W-QUIET, W-SA1, W-SA13', every prediction held: sa1 holds the word sent to attribute 1 and, with no pass after the emit, nothing faults"
unit = "edm"
method = "r43-n3h-n1 (render/closing-r43-n3h-n1), stage w of the question-closing pass (round 43: row W, closing29/n3h/design.md section 3.1; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r43-n3h-n1; attempt out/20261123-164401 (16:44:01; stage w ended rc 0 and the driver scored it, score-w.txt; stage v followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 43; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it and, for a kicked job, right after the kick's reply (K5, K6's mid), K6's kick-only job and K7's per-stage draws (kit/ = resgx545 1f49335c, branch r43-n3h, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at 1f49335c; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and its begin health (fill and triangle, the session's first stage), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none) and no end draws (end_draws none): the disarm reset and the register health only; the blob, images and form of round 42, unchanged on the running module (E1180, E1182, E1183); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 fbbf7a57893c9788baf89a68af93986be585bf2f83ff4ce1224a6d7a265c8bf7 (62 files), PREDICTIONS.sha256 bbe5cb12802f27ffdd4f7966181d7ec0810138026841cd73ffa4d371634038f0 (2 files), pins in FROZEN.commits (the kit and the blob sources at 1f49335c; round 42's kept stages G1 m and G3 lv at data fadfa30a; t30's source 42c4de7); the frozen predictions predictions/w.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-w-20261123-164401.out, the same bytes as score-w.txt); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-23"
data = ["render-closing-r43-n3h-n1:out/20261123-164401/w/", "render-closing-r43-n3h-n1:fold/"]
terms = []
+++
**What ran.** Row M's image (E1180: mark, crumb3 plus M13 0x005d3000 to attribute 13 and M1
0x005d1000 to attribute 1, with T3 stopping the tick) and its emit, as one job with no kick and no
command after it, so that no pass runs on the rewritten bank before the disarm reset (the one-job
shape of B11 and T, E1172, E1177). K7: no gate and no end draws, so that the next stage's emit
follows only resets, the register health and its arm. The question: does sa1 read the word sent to
attribute 1 in the row that sends it, with no fault?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: w: controls: every control passed
Q128-N3H-W RULE: W-QUIET, W-SA1, W-SA13
PREDICTION W-FAULT: predicted failed, read FAILED: held
PREDICTION W-QUIET: predicted held, read held: held
PREDICTION W-SA1: predicted held, read held: held
PREDICTION W-SA13: predicted held, read held: held
```

Every control passed (PG, E0, T0, B, J1). Every prediction held: W-QUIET, W-SA1 and W-SA13 held,
W-FAULT failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, state 2, T 0x005a3305, 9 ticks. K5: BIF_INT_STAT 0x00080000
  and BIF_FAULT 0 before and after; snap9 BIF_FAULT 0.
- Job 1's post sa: sa1 = M1 0x005d1000, sa13 = pa1 = M13 0x005d3000, sa0 = V0 0x32004000, sa2 = V2
  0x32002000, sa12-sa27 = pa0-pa15 (pa0 3, pa12 and pa14 0x5a5a3a18 and 0x5a5a3a1a, the odd pa the
  words of E1179), sa3-sa10 0x3f800000, V0, 0xbec00000, V2, 0x3f800000, V0, 0x3f400000, V2, as in M,
  Q and LV.
- The kernel: the arm after the begin draws, fill and triangle, "SGX stopped, 3 events seen"; the
  disarm and exit resets "0 events seen"; no fault line.

**What it shows.** With bit 10 the word our program sends to attribute 1 is the issuer's sa1 in the
same row, as in M (E1180), and the word sent to attribute 13 its sa13 and the started entry's pa1
**[HW]**: for attributes 1 and 13, sa n reads attribute n (H-BLOCK at those two points). With no
pass after the emit nothing faults: the fault of M, X and Q needs a later pass on the rewritten bank
**[HW]**, as B11's and T's single jobs read. That H-BLOCK holds for every n of one block is
**[infer]**.

**What it does not show.** Where sa3-sa10 come from; whether the plant stays across a stage boundary
(row V, E1185); one run.
