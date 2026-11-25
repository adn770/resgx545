+++
id = "E1213"
claim = "r45-n3j-n2 stage lf2 (row LF2, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WG (E1212) and one stock fill as the begin draws: job 1 done with post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0105bab1, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x0000000f (list 15, page 0; the scorer: job 1's post sa0), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3J-LF2 RULE: LF2-EARLY0, LF2-PAGE, LF2-SA0, LF2-SA1, LF2-SA2', every prediction held: LF's triple and page-0 stop (E1200) read a second time"
unit = "edm"
method = "r45-n3j-n2 (render/closing-r45-n3j-n2), stage lf2 of the question-closing pass (round 45: row LF2, closing29/n3j/design.md section 3.4; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n2; attempt out/20261124-210558 (21:06:19; stage lf2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot before round 45's sessions N1-N4; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists and K9's command count (the kernel's `loaded ... ccb_sent N` lines of the stage's kernel log, the control DK) (kit/ = resgx545 94f9e501, branch r45-n3j, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-44 and the mark, crumb3 and land images, unchanged on the running module (E1184-E1200); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 b06140561e16841e7beb4f0cdd38e99535bc3f408318f493cd26e5e62fd16137 (64 lines), PREDICTIONS.sha256 c4b0e5498d23b8de2de02d63fe4b1e433031957ca6613d5548f5d3399c163a5e (2 files), pins in FROZEN.commits (the kit and the blob sources at 94f9e501; round 44's kept stages of r44-n3i-n1 and r44-n3i-n3 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/lf2.tsv, the rule score/score.py, scored after the session (closing29/r45-n3j-logs/score-r45-n3j-n2-lf2.txt) and again by hand on the kept directory (fold/reproduce-lf2-20261124-210558.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n2:out/20261124-210558/lf2/", "render-closing-r45-n3j-n2:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM and LF byte for byte: Ma and Mb to
attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the plant
WG (E1212), with `begin_draws = "fill"`: between the plant's emit and the image's ran the plant's
disarm and exit resets, this stage's begin reset with one stock fill and the arm [HW, the stages'
kernel logs; DR passed; DK passed: KC begin delta 4]. Jobs: LM's two (E1198): job 1 the emit on the
tick pass, job 2 command 6 on the next tick pass. The question: does land after one fill read LF's
triple again, sa0 2, sa1 M1 and a timer word (LF2-SA0, LF2-SA1, LF2-SA2), and stop at page 0 again
(LF2-EARLY0, LF2-PAGE)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r45-n3j-logs/score-r45-n3j-n2-lf2.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: lf2: controls: lf21-a:B: FAILED; lf21-a:J2: FAILED
Q128-N3J-LF2 RULE: LF2-EARLY0, LF2-PAGE, LF2-SA0, LF2-SA1, LF2-SA2
PREDICTION LF2-AOTHER: predicted printed, read FAILED: printed
PREDICTION LF2-EARLY0: predicted held, read held: held
PREDICTION LF2-EARLY1: predicted failed, read FAILED: held
PREDICTION LF2-PAGE: predicted held, read held: held
PREDICTION LF2-SA0: predicted held, read held: held
PREDICTION LF2-SA1: predicted held, read held: held
PREDICTION LF2-SA2: predicted held, read held: held
PREDICTION LF2-SERVE: predicted failed, read FAILED: held
PREDICTION LF2-TICK: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage wg), PG, E0, T0, J1, DR and DK passed; B (BIF_FAULT 0 after the row) and J2
(job 2 done) failed, read by LF2-EARLY0 and LF2-PAGE (the outcomes that name the stop). Every
prediction held: LF2-SA1, LF2-SA0, LF2-SA2, LF2-PAGE and LF2-EARLY0 held; LF2-TICK, LF2-EARLY1 and
LF2-SERVE failed as predicted; LF2-AOTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000002, sa1 = M1 0x005d1000, sa2 0x0105bab1, sa13 = pa1 = M13; post sa3-sa31
  and pa0-pa15 equal WG's word for word. The survey's pre read sa0 = V0, sa2 = V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0), post the
  same; job 2 not done (cmd_after 6, dwords 224-255 still 0xdeadc0de); the tick stopped; snap9 and
  the stop dump the same fault. The kit's reset and both draws recovered it (health ok,
  closing29/r45-n3j-logs/health-r45-n3j-n2.log).
- The kernel: lf2's arm after the one fill "1 events seen"; the end KC cannot tell (no exit load
  after the stop).

**What it shows.** Land after a plant and one fill read sa0 2, sa1 = M1 and a timer word in sa2, and
stopped at page 0, a second time **[HW, LF E1200 and LF2]**: LF's triple and stop meet the two-read
rule. crumbz read the same shape after one fill with the tick stopped (ZF, E1225), so the fill's
events wrote sa0 and sa2 **[HW]**. That the stop's page is sa0's is **[infer]**: row Q (E1233)
faulted at sa1's page with sa0 holding a higher word.

**What it does not show.** Which access of the tick pass read page 0; one run of this stage.
