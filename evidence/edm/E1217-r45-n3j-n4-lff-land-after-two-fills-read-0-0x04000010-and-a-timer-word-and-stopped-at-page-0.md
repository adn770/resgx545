+++
id = "E1217"
claim = "r45-n3j-n4 stage lff (row LFF, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WI (E1216) and two stock fills as the begin draws: job 1 done with post sa0 0, sa1 0x04000010, sa2 0x0105fbea, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x0000000f (list 15, page 0; the scorer: job 1's post sa0), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3J-LFF RULE: LFF-PAGE'; LFF-SA1 FAILED against its prediction (held), LFF-SA0 FAILED against its prediction (held), LFF-PAGE held, LFF-V0 and LFF-HIST failed as predicted: two fills before land left 0x04000010 in attribute 1, not the planted M1, and sa0 0, not 2"
unit = "edm"
method = "r45-n3j-n4 (render/closing-r45-n3j-n4), stage lff of the question-closing pass (round 45: row LFF, closing29/n3j/design.md section 3.6; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n4; attempt out/20261124-210745 (21:08:06; stage lff exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot before round 45's sessions N1-N4; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists and K9's command count (the kernel's `loaded ... ccb_sent N` lines of the stage's kernel log, the control DK) (kit/ = resgx545 94f9e501, branch r45-n3j, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill,fill), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-44 and the mark, crumb3 and land images, unchanged on the running module (E1184-E1200); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 95bd1ba8548882eba95a31b4c6800ed24981e5c97812597e428e7dcbd4faaeba (64 lines), PREDICTIONS.sha256 469e58fdd1b1f1b4fef57d48c361c9f3235d6c484677e812c4d6052aa7198ebe (2 files), pins in FROZEN.commits (the kit and the blob sources at 94f9e501; round 44's kept stages of r44-n3i-n1 and r44-n3i-n3 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/lff.tsv, the rule score/score.py, scored after the session (closing29/r45-n3j-logs/score-r45-n3j-n4-lff.txt) and again by hand on the kept directory (fold/reproduce-lff-20261124-210745.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n4:out/20261124-210745/lff/", "render-closing-r45-n3j-n4:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM and LF byte for byte: Ma and Mb to
attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the plant
WI (E1216), with `begin_draws = "fill,fill"`: between the plant's emit and the image's ran the
plant's disarm and exit resets, this stage's begin reset with two stock fills and the arm [HW, the
stages' kernel logs; DR passed; DK passed: KC begin delta 6]. Jobs: LM's two (E1198): job 1 the emit
on the tick pass, job 2 command 6 on the next tick pass. The question: after two fills, does land
read sa1 M1 (LFF-SA1, as FF) and sa0 2 (LFF-SA0, as LF), or sa0 = V0 (LFF-V0), and where does its
stop fault (LFF-PAGE, LFF-HIST)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r45-n3j-logs/score-r45-n3j-n4-lff.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: lff: controls: lff1-a:B: FAILED; lff1-a:J2: FAILED
Q128-N3J-LFF RULE: LFF-PAGE
PREDICTION LFF-HIST: predicted failed, read FAILED: held
PREDICTION LFF-PAGE: predicted held, read held: held
PREDICTION LFF-SA0: predicted held, read FAILED: FAILED
PREDICTION LFF-SA1: predicted held, read FAILED: FAILED
PREDICTION LFF-V0: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage wi), PG, E0, T0, J1, DR and DK passed; B (BIF_FAULT 0 after the row) and J2
(job 2 done) failed, read by LFF-PAGE (the outcomes that name the stop). **LFF-SA1 failed against
its prediction (held): post sa1 was 0x04000010, not M1.** **LFF-SA0 failed against its prediction
(held): post sa0 was 0, not 2.** LFF-PAGE held as predicted; LFF-V0 and LFF-HIST failed as
predicted.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x00000000, sa1 0x04000010, sa2 0x0105fbea, sa13 = pa1 = M13; post sa3-sa31 and
  pa0-pa15 equal WI's word for word. The survey's pre read sa0 = V0, sa2 = V2.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0), post the
  same; job 2 not done; the tick stopped; snap9 and the stop dump the same fault. The kit's reset
  and both draws recovered it (health ok, closing29/r45-n3j-logs/health-r45-n3j-n4.log).
- The kernel: lff's arm after the two fills "2 events seen"; the begin KC 6, as two fills give; the
  end KC cannot tell. HKC (printed): 0x04000010 is H-KC's word for the second fill's 3:4 entry at K
  4.

**What it shows.** Two fills before land left sa0 0, sa1 0x04000010 and a timer word in sa2
**[HW]**, where crumb3 read M1 after two fills twice (FF E1191, FF2 E1202) and crumbz read sa0 2, M1
and a timer word (ZFF, E1227) **[HW]**: the reads of fill, fill disagree. 0x04000010 is X's word
after a fill and a triangle (E1174) and H-KC's for the second fill's own slot-3 entry at K 4; if so,
it is the first read of a fill's own entry word, against H-TRI's "a fill's entries never write"
**[infer]**. With sa0 0 the stop faulted at page 0 **[HW]**.

**What it does not show.** Why this read differs from FF, FF2 and ZFF (the image differs: land
leaves the tick running); one run of this stage.
