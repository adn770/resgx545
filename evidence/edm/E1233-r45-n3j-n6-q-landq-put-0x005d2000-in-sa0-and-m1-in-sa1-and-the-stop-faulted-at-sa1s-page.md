+++
id = "E1233"
claim = "r45-n3j-n6 stage q (row Q, module EC553F41, fork b1089172b2e7, emitsb_sbc43s, image landq at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WQ (E1232) and no draws: landq wrote Q0 0x005d2000 to attribute 0 and M1 0x005d1000 to attribute 1; job 1 done with post sa0 = Q0, sa1 = M1, sa2 = V2 0x32002000, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3J-Q RULE: Q-WRITE'; Q-WRITE held, Q-SA0 FAILED against its prediction (held), Q-LOW (predicted failed) read held and was scored cannot tell by its frozen rule, Q-SERVE failed as predicted: with sa0 0x005d2000 and sa1 0x005d1000 the stop faulted at sa1's page, not sa0's"
unit = "edm"
method = "r45-n3j-n6 (render/closing-r45-n3j-n6), stage q of the question-closing pass (round 45: row Q, closing29/n3j/design.md section 9.5; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n6; attempt out/20261125-092604 (09:26:25; stage q exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion EC553F41FD8324BB6BF1764 installed and loaded alike (control SV), linux fork r45-kernel b1089172b2e7, r42-kernel plus the crumbz and landq images, built on cachix 2026-11-24 (closing29/kernel39c/deliver/b1089172b2e7/manifest, closing29/kernel39c/r45-kernel-check.pass, closing29/r45-n3j-fork-logs/cachix-wait.log), the second one-shot boot of 2026-11-25 (closing29/r45-n3j-z-logs/boot2.log; the first ended in a hard hang of the laptop, unexplained, render-closing-r45-n3j-n5's fold/FOLD-NOTES.md); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and the arm words pds=crumbz and pds=landq (kit/ = resgx545 cf20aa87, branch r45-n3j-z, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at b1089172b2e7 on the Mac shim, 48 of 48 (closing29/r45-n3j-fork-logs/shim-r45-green-fork.log; r45-red 45 of 48, shim-r45-red-fork.log), with the round's own suite 50 of 50 (shim-r45-green.log; r45-red 46 of 50, shim-r45-red.log; a wrong expected word fails, 49 of 50, shim-r45-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landq pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-44 and the mark image, their bytes unchanged in the rebuild, and our own crumbz and landq images (asm/fwtask/pds/crumbz.s and landq.s at cf20aa87, assembled with pds-asm, no firmware bytes), their first runs; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 7fdb99db8211fe47209740b4a3298fa20978c02fef559fe780c08802f39c3668 (65 lines), PREDICTIONS.sha256 db2e3119b241fc03c3fed1dc0b1c3b9cc2e594528cf641c69698dd61559d74fc (2 files), pins in FROZEN.commits (the kit and the blob sources at cf20aa87; round 44's kept stages of r44-n3i-n1 and r44-n3i-n2 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/q.tsv, the rule score/score.py, scored after the session (closing29/r45-n3j-z-logs/score-r45-n3j-n6-q.txt) and again by hand on the kept directory (fold/reproduce-q-20261125-092604.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n6:out/20261125-092604/q/", "render-closing-r45-n3j-n6:fold/"]
terms = []
+++
**What ran.** landq (18 dwords: land's 12 data dwords with its third row holding Q0 0x005d2000, M1
0x005d1000 and their `douta` controls; land's two marker `douta`, then Q0 to attribute 0 and M1 to
attribute 1, then land's `doutu` and `halt`; no `tim`, so the tick runs) right after the plant WQ
(E1232), with `begin_draws = "none"`: between the plant's emit and the image's ran the plant's
disarm and exit resets, this stage's begin reset with the register health (no draw) and the arm [HW,
the stages' kernel logs; DR passed; DK passed: KC begin delta 2]. Jobs: LM's two (E1198): job 1 the
emit on the tick pass, job 2 command 6 on the next tick pass. The question: with two words our rows
never saw mapped in sa0 and sa1, sa0 the higher, does the stop fault at sa0's page (Q-SA0: H-SA0,
the pass reads sa0, then sa1) or at the lower page, sa1's (Q-LOW)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r45-n3j-z-logs/score-r45-n3j-n6-q.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: q: controls: q1-a:B: FAILED; q1-a:J2: FAILED
Q128-N3J-Q RULE: Q-WRITE
PREDICTION Q-LOW: predicted failed, read held: cannot tell (a fault at 0x005d1000 with Q-WRITE held cannot tell 'lowest page' from 'sa0 mapped'; printed)
PREDICTION Q-OTHER: predicted printed, read FAILED: printed
PREDICTION Q-SA0: predicted held, read FAILED: FAILED
PREDICTION Q-SERVE: predicted failed, read FAILED: held
PREDICTION Q-WRITE: predicted held, read held: held
```

PG, E0, T0, J1, DR, DK and SV passed (no PLANT: Q reads none); B (BIF_FAULT 0 after the row) and J2
(job 2 done) failed, read by Q-SA0 and Q-LOW (the outcomes that name the stop). Q-WRITE held as
predicted. **Q-SA0 failed against its prediction (held): the fault is at 0x005d1000, sa1's page.**
Q-LOW (predicted failed) read held and is scored `cannot tell` by its frozen rule (a fault at
0x005d1000 with Q-WRITE held cannot tell 'lowest page' from 'sa0 mapped'). Q-SERVE failed as
predicted; Q-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 0x005d2000 = Q0, sa1 0x005d1000 = M1, sa2 0x32002000 = V2 (WQ's plant kept), sa13
  = pa1 = M13, sa24 = pa12 Ma 0x5a5a3a18 and sa26 = pa14 Mb 0x5a5a3a1a (landq's markers); the other
  post sa3-sa31 and pa equal WQ's word for word.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x005d100f (list 15, page 0x005d1000),
  post the same; job 2 not done; the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r45-n3j-z-logs/health-r45-n3j-n6.log).
- The kernel: q's arm with no draws "0 events seen"; KC begin 2; the end KC cannot tell.

**What it shows.** A word our image sends to attribute 0 with 0xc43 is sa0 in the same row, as for
attribute 1 (Q-WRITE) **[HW]**. With Q0 in sa0 and M1 in sa1 the early stop faulted at M1's page,
sa1's, the lower one **[HW]**. So H-SA0 as "the tick pass reads sa0 first and faults at the first
unmapped word" is falsified unless 0x005d2000 is mapped **[HW against Q-SA0; infer for the
mapping]**, and so is "sa1 first, the BIF keeps the last fault". Two readings survive and Q does not
tell them apart: the lowest faulting page is kept, or sa0 is read first and 0x005d2000 is mapped
**[infer]**. Every early stop read so far fits both: page 0 with sa0 below one page (LC, LC2, LF,
LF2, LT, LFF), sa1's page with sa0 = V0 (LV, V, LM) and here **[HW pages; infer reading]**.

**What it does not show.** Whether 0x005d2000 is mapped; one run of this stage.
