+++
id = "E1187"
claim = "r43-n3h-n2 stage f (row F, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after row W2 (E1186) and one stock fill as the begin draws (K7): job 1's post sa1 0x01000000 (neither M1 nor 0x04000010), sa13 = pa1 = M13 0x005d3000; job 2 a kick-only pass (K6): K5 pre BIF_FAULT 0, the GETMISCINFO kick answered, K5 mid (right after the reply) and post BIF_FAULT 0x005d300f (list 15, page 0x005d3000, the post sa13); job 3 command 6 on a kick: the kick not answered, the command not served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3H-F RULE: K-KICK, K-QUIET, K-REPLY, K-STALL'; F-FILL4 FAILED against its prediction (held), F-KEEP failed as predicted, F-OTHER (printed) held, every other prediction held, F-GATE not reached: one fill rewrote attribute 1, and the bare kick pass faults at the page in sa13, after which the EDM serves nothing"
unit = "edm"
method = "r43-n3h-n2 (render/closing-r43-n3h-n2), stage f of the question-closing pass (round 43: row F, closing29/n3h/design.md section 3.4; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r43-n3h-n2; attempt out/20261123-164448 (16:45:10; stage f exited 4 at its one row, the runner's stop K-STALL names, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 43; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it and, for a kicked job, right after the kick's reply (K5, K6's mid), K6's kick-only job and K7's per-stage draws (kit/ = resgx545 1f49335c, branch r43-n3h, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at 1f49335c; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill: one stock fill, no triangle), then one row of three jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); a kick-only job (K6: a GETMISCINFO kick with no command written, 50 ms, expect notdone); command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on a GETMISCINFO kick; the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the gate (fill, then triangle) not reached; the blob, images and form of round 42, unchanged on the running module (E1180, E1182, E1183); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 d4de03ee82e5369ceaef6e4d3eeaede11923baa3123e1218abfbe10ee41697e5 (62 files), PREDICTIONS.sha256 c5b5f9dbff28ee85902364f5dc7420fe285911cf0df6af926a281f22736165db (2 files), pins in FROZEN.commits (the kit and the blob sources at 1f49335c; round 42's kept stages G1 m and G3 lv at data fadfa30a; t30's source 42c4de7); the frozen predictions predictions/f.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-f-20261123-164448.out); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-23"
data = ["render-closing-r43-n3h-n2:out/20261123-164448/f/", "render-closing-r43-n3h-n2:fold/"]
terms = []
+++
**What ran.** X's emit (E1174: crumb3, sideband 0xc43, T3 stopping the tick) right after row W2,
with K7's `begin_draws = "fill"`: between W2's emit and F's emit ran W2's disarm and exit resets,
F's begin reset, one stock fill and F's arm [HW, the stages' kernel logs]. Then K6's kick-only job:
a GETMISCINFO kick with no command written (our entry 0 dispatches nothing and tail-calls the stock
code), with K5's BIF words read before it, right after its reply (mid) and after its poll; then
command 6 on a kick (M's job 2). The questions: does one fill rewrite attribute 1, and with what
word (H-EVT predicted its slot-3 event word, bits 23:0 = 0x000010)? Does the bare kick pass fault on
the rewritten bank, and does the EDM serve anything after?

**Frozen verdict (as printed).** The stage stopped, so the frozen scorer was run by hand on the kept
directory:

```
SUMMARY: f: controls: f1-a:B: FAILED; f1-a:J3: FAILED
Q128-N3H-F RULE: K-KICK, K-QUIET, K-REPLY, K-STALL
PREDICTION F-FILL4: predicted held, read FAILED: FAILED
PREDICTION F-GATE: predicted held if reached, read cannot tell: not reached (K-STALL)
PREDICTION F-KEEP: predicted failed, read FAILED: held
PREDICTION F-OTHER: predicted printed, read held: printed
PREDICTION K-KICK: predicted held, read held: held
PREDICTION K-KICKOK: predicted failed, read FAILED: held
PREDICTION K-QUIET: predicted held, read held: held
PREDICTION K-REPLY: predicted held, read held: held
PREDICTION K-SERVE: predicted failed, read FAILED: held
PREDICTION K-STALL: predicted held, read held: held
```

PG, E0, T0, J1 and J2 (job 2's own expected end, not done) passed; B and J3 failed, read by K-KICK
and K-STALL, which name the fault and the stall. The scorer's PLANT line read W-SA1 of stage w2 as a
pass. **F-FILL4 failed against its prediction (held).** F-KEEP failed as predicted and F-OTHER
(printed) held. K-QUIET, K-KICK, K-REPLY and K-STALL held, K-KICKOK and K-SERVE failed, all as
predicted; F-GATE was not reached.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 10 ticks; K5 BIF_FAULT 0 before and after. Its
  post sa: sa1 0x01000000; sa13 = pa1 = M13 0x005d3000; sa0 = V0, sa2 = V2; every other word of
  sa0-sa31 and pa0-pa15 equal to W2's.
- Job 2 (kick-only): K5 pre BIF_INT_STAT 0x00080000, BIF_FAULT 0; the kick answered (GETMISCINFO
  after 200 us, the reply in 3.6 ms); K5 mid BIF_INT_STAT 0x000d0400, BIF_FAULT 0x005d300f (list 15,
  page 0x005d3000 = M13 = the post sa13); post the same; not done, its expected end.
- Job 3 (command 6 on a kick): K5 pre, mid and post 0x005d300f; the kick not answered (the kernel:
  "no GETMISCINFO answer (-110)"); cmd_after 6, dwords 224-255 still 0xdeadc0de; the runner stopped
  (class hang). The tick count was the same at job 2's start and at the stop: T3 had stopped it at
  job 1, as designed. The kit's reset and both draws recovered it (health ok,
  closing29/r43-n3h-logs/health-r43-n3h-n2.log).
- The kernel: F's arm after the one fill "1 events seen" (W2's after both draws "3 events seen").

**What it shows.** One stock fill rewrote attribute 1: with the same boundary and no draw, V (E1185)
kept M1; with the fill, sa1 read 0x01000000 **[HW]**. It is not the word H-EVT predicted (bits 23:0
= 0x000010, the fill's slot-3 event bit), so F-FILL4 failed; that the top byte, 1, is a count is
**[infer]** and not claimed. So attribute 1 is rewritten by a client draw, and Q's 0x04400000
(E1182) after the draws between rows M and Q fits that **[infer]**: which draw left which word was
read only for one fill. The bare GETMISCINFO kick pass, with our task idle, faulted on the rewritten
bank at the page in sa13, by the time its reply returned (K5 mid), with the tick stopped since job
1, so on the kick's own pass **[HW]**: our after-read (command 6) is not needed for the fault. After
that fault the EDM answered no kick and served no command **[HW]**: it stalls after the first fault.
That the gate fills of rounds 41 and 42, which found BIF_FAULT already set, met an EDM stalled since
job 2 is **[infer]**.

**What it does not show.** What the fill's word means, and what the triangle writes there; which
access of the kick pass read sa13's page; whether the stall stops the tick (T3 had stopped it
already); one run.

**Correction 2026-11-24:** Round 44 read attribute 1 after other draw sequences. One fill after the
same plant and boundary left M1 in row LF (E1200), and two fills left it in row FF (E1191); one fill
with no plant after a fill-then-triangle stage left 0x05400000 in row F2 (E1196) **[HW]**. So this
record's "one fill rewrote attribute 1" holds for this row only: a fill does not always write
attribute 1, and one fill has left three outcomes (0x01000000, the word kept, 0x05400000) **[HW]**;
what decides it is **[open]**. A triangle alone left 0x02400000 and a triangle then a fill the same
(E1193, E1195) **[HW]**. This record's frozen verdict (F-FILL4 FAILED against its prediction) and
readings stand.

**Correction 2026-11-25:** Round 45 read one fill after the same kind of plant three more times: M1
kept with crumb3 (F3, E1210), with land (LF2, E1213) and with crumbz (ZF, E1225) **[HW]**. Of the
five reads of one fill after a plant, four kept the planted word and this record's read 0x01000000
**[HW]**: the reads disagree, so the one-fill word is not known, and what made this row's differ is
**[open]**. This record's frozen verdict and readings stand.
