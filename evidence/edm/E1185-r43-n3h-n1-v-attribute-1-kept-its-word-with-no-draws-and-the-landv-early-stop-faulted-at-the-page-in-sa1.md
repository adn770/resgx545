+++
id = "E1185"
claim = "r43-n3h-n1 stage v (row V, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image landv at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after row W (E1184) with no client draw between (only resets, the register health and the arm, K7): job 1 done with post sa1 = M1 0x005d1000, sa0 = V0, sa2 = V2, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000, the post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3H-V RULE: V-EARLY1, V-KEEP, V-V', every prediction held: attribute 1 keeps its word across a stage boundary without draws, and landv's early stop faults at the page in sa1"
unit = "edm"
method = "r43-n3h-n1 (render/closing-r43-n3h-n1), stage v of the question-closing pass (round 43: row V, closing29/n3h/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r43-n3h-n1; attempt out/20261123-164401 (16:44:23; stage v exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 43; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it and, for a kicked job, right after the kick's reply (K5, K6's mid), K6's kick-only job and K7's per-stage draws (kit/ = resgx545 1f49335c, branch r43-n3h, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at 1f49335c; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landv pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none: the register health, no draw), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob, images and form of round 42, unchanged on the running module (E1180, E1182, E1183); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 fbbf7a57893c9788baf89a68af93986be585bf2f83ff4ce1224a6d7a265c8bf7 (62 files), PREDICTIONS.sha256 bbe5cb12802f27ffdd4f7966181d7ec0810138026841cd73ffa4d371634038f0 (2 files), pins in FROZEN.commits (the kit and the blob sources at 1f49335c; round 42's kept stages G1 m and G3 lv at data fadfa30a; t30's source 42c4de7); the frozen predictions predictions/v.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-v-20261123-164401.out); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-23"
data = ["render-closing-r43-n3h-n1:out/20261123-164401/v/", "render-closing-r43-n3h-n1:fold/"]
terms = []
+++
**What ran.** LV's row (E1183: landv, land plus V0 and V2 to attributes 0 and 2, no `tim`, so the
tick runs) right after row W, with K7's `begin_draws = "none"`: between W's emit and V's emit ran
only W's disarm and exit resets, V's begin reset with the register health and V's arm (boot,
GETMISCINFO, ticks), no client draw [HW, the stages' kernel logs]. Job 2 command 6 on the next tick
pass. The questions: does attribute 1 keep W's M1 with no draws (H-EVT, design section 0.1), and
does the early stop's fault page follow sa1?

**Frozen verdict (as printed).** The stage stopped, so the frozen scorer was run by hand on the kept
directory:

```
SUMMARY: v: controls: v1-a:B: FAILED; v1-a:J2: FAILED
Q128-N3H-V RULE: V-EARLY1, V-KEEP, V-V
PREDICTION V-EARLY0: predicted failed, read FAILED: held
PREDICTION V-EARLY1: predicted held, read held: held
PREDICTION V-EARLY13: predicted failed, read FAILED: held
PREDICTION V-EVT: predicted failed, read FAILED: held
PREDICTION V-KEEP: predicted held, read held: held
PREDICTION V-OTHER: predicted printed, read FAILED: printed
PREDICTION V-SERVE: predicted failed, read FAILED: held
PREDICTION V-V: predicted held, read held: held
PREDICTION V-V1: predicted failed, read FAILED: held
```

PG, E0, T0 and J1 passed; B (BIF_FAULT 0 after the row) and J2 (job 2 done) failed, read by
V-EARLY1, which names the stop (the frozen rule of X, LC2 and LV). The scorer's PLANT line read
W-SA1 of stage w as a pass. Every prediction held: V-KEEP, V-V and V-EARLY1 held; V-EVT, V-V1,
V-EARLY13, V-EARLY0 and V-SERVE failed; V-OTHER (printed) failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa equal to W's (E1184) word for word: sa1 = M1 0x005d1000, sa0 = V0, sa2 = V2, sa13
  = pa1 = M13, sa12-sa27 = pa0-pa15, pa12 and pa14 landv's markers.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x005d100f (list 15, page 0x005d1000 =
  M1 = the post sa1), post the same; job 2 not done (cmd_after 6, dwords 224-255 still 0xdeadc0de);
  the tick stopped (the runner's alive check; landv writes no `tim`); snap9 and the stop dump the
  same fault. The kit's reset and both draws recovered it (health ok,
  closing29/r43-n3h-logs/health-r43-n3h-n1.log).
- The kernel: V's arm "0 events seen" (no draws since the last reset), the recovery's reset after
  both draws "3 events seen".

**What it shows.** Attribute 1 kept the word W sent to it across a stage boundary of three resets,
the register health, a firmware boot, GETMISCINFO kicks and tick passes, with no client draw
**[HW]**: none of those write attribute 1, so V-EVT and V-V1 (H-BOOT) fail and the writer that
changed sa1 between rows M and Q (E1180, E1182) is among the draws or M's fault path (row F, E1187).
With landv the EDM stopped after the emit's pass with a fault at the page of the word in sa1, M1, as
LV's at 0x04400000, LV's sa1 **[HW]**: the early stop's fault page follows sa1, with sa0 valid and
sa13 another unmapped word (M13). That a tick pass reads through sa1 (the HostCtl pointer of E002)
is **[infer]**. LC's page 0 (E1176, E1178, with sa1 0x04400000 in LC2) is not explained by that.

**What it does not show.** Which access of the tick pass read sa1's page; why land (sa0 0) faults at
page 0; whether a mapped sa1 would let the EDM survive; one run.
