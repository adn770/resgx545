+++
id = "E1215"
claim = "r45-n3j-n3 stage lt (row LT, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WH (E1214) and one 64x64 triangle as the begin draws: job 1 done with post sa0 0, sa1 0x02400000, sa2 0x01048c28, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x0000000f (list 15, page 0; the scorer: job 1's post sa0), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3J-LT RULE: LT-PAGE, LT-SA1, LT-TRIPLE', every prediction held (LT-ONE, LT-HIST and LT-SERVE failed as predicted): a triangle alone left (0, 0x02400000, a timer word) and land stopped at page 0"
unit = "edm"
method = "r45-n3j-n3 (render/closing-r45-n3j-n3), stage lt of the question-closing pass (round 45: row LT, closing29/n3j/design.md section 3.5; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n3; attempt out/20261124-210651 (21:07:12; stage lt exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot before round 45's sessions N1-N4; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists and K9's command count (the kernel's `loaded ... ccb_sent N` lines of the stage's kernel log, the control DK) (kit/ = resgx545 94f9e501, branch r45-n3j, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws tri), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-44 and the mark, crumb3 and land images, unchanged on the running module (E1184-E1200); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 578d34fd133cdc131aa4d6ccba5a921190b9a00d87a293d2dd5f1f74c7ed29f2 (64 lines), PREDICTIONS.sha256 90e9eff6c9cc263d8da66f122b21464f7badf505ab523c891e9f8c601aa67a67 (2 files), pins in FROZEN.commits (the kit and the blob sources at 94f9e501; round 44's kept stages of r44-n3i-n1 and r44-n3i-n3 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/lt.tsv, the rule score/score.py, scored after the session (closing29/r45-n3j-logs/score-r45-n3j-n3-lt.txt) and again by hand on the kept directory (fold/reproduce-lt-20261124-210651.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n3:out/20261124-210651/lt/", "render-closing-r45-n3j-n3:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM and LF byte for byte: Ma and Mb to
attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the plant
WH (E1214), with `begin_draws = "tri"`: between the plant's emit and the image's ran the plant's
disarm and exit resets, this stage's begin reset with one 64x64 triangle and the arm [HW, the
stages' kernel logs; DR passed; DK passed: KC begin delta 8]. Jobs: LM's two (E1198): job 1 the emit
on the tick pass, job 2 command 6 on the next tick pass. The question: what does a triangle alone
leave in sa0-sa2 (LT-TRIPLE: 0, 0x02400000, a timer word; LT-ONE: attribute 1 alone), and where does
land's stop fault (LT-PAGE: the H-SA0 rule's page; LT-HIST: page 0 with sa0 = V0)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r45-n3j-logs/score-r45-n3j-n3-lt.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: lt: controls: lt1-a:B: FAILED; lt1-a:J2: FAILED
Q128-N3J-LT RULE: LT-PAGE, LT-SA1, LT-TRIPLE
PREDICTION LT-AOTHER: predicted printed, read FAILED: printed
PREDICTION LT-HIST: predicted failed, read FAILED: held
PREDICTION LT-ONE: predicted failed, read FAILED: held
PREDICTION LT-PAGE: predicted held, read held: held
PREDICTION LT-SA1: predicted held, read held: held
PREDICTION LT-SERVE: predicted failed, read FAILED: held
PREDICTION LT-TRIPLE: predicted held, read held: held
```

PLANT (W-SA1 of stage wh), PG, E0, T0, J1, DR and DK passed; B (BIF_FAULT 0 after the row) and J2
(job 2 done) failed, read by LT-PAGE (the outcomes that name the stop). Every prediction held:
LT-SA1, LT-TRIPLE and LT-PAGE held; LT-ONE, LT-HIST and LT-SERVE failed as predicted; LT-AOTHER
(printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000000, sa1 0x02400000, sa2 0x01048c28, sa13 = pa1 = M13; post sa3-sa31 and
  pa0-pa15 equal WH's word for word. The survey's pre read sa0 = V0, sa2 = V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0), post the
  same; job 2 not done; the tick stopped; snap9 and the stop dump the same fault. The kit's reset
  and both draws recovered it (health ok, closing29/r45-n3j-logs/health-r45-n3j-n3.log).
- The kernel: lt's arm after the triangle "2 events seen"; the end KC cannot tell.

**What it shows.** A triangle alone after a plant left sa0 0, sa1 0x02400000 and a timer word in sa2
**[HW]**, the triple crumbz read after it (ZT, E1221) and the sa1 of T and T2 (E1193, E1204). So a
triangle writes attributes 0-2 together, not attribute 1 alone (LT-ONE failed) **[HW]**, and LC's
sa0 0 and page 0 (E1176, E1178) fit a triangle's write **[infer]**. With sa0 0 the stop faulted at
page 0 **[HW]**; LT-PAGE and LT-HIST both named page 0, so this row does not split H-SA0 from
H-HIST.

**What it does not show.** Which access of the tick pass read page 0; one run of this stage.
