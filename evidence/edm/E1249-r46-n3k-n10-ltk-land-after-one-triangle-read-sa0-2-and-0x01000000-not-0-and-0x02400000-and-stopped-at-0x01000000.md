+++
id = "E1249"
claim = "r46-n3k-n10 stage ltk (row LTK, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant W10 (E1248) and one stock triangle as the begin draws: job 1 done with post sa0 0x00000002, sa1 0x01000000, sa2 0x01061a74, sa12 = V0, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x0100000f (list 15, page 0x01000000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-LTK RULE: LTK-E12, LTK-PAST'; LTK-E12 held, LTK-SA and LTK-SA1 FAILED against their predictions (held), LTK-PAST read held against its prediction (failed), LTK-PAGE0 and LTK-SERVE failed as predicted: after a triangle land read sa0 2 and 0x01000000, not LT's 0 and 0x02400000, and stopped at 0x01000000"
unit = "edm"
method = "r46-n3k-n10 (render/closing-r46-n3k-n10), stage ltk of the question-closing pass (round 46's addendum: row LTK, closing29/n3k/design.md section 11.3 and 11.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 11.9: G=a, H=a, I=a, J=a, K=a), dataset render-closing-r46-n3k-n10; attempt out/20261125-231217 (23:12:39; stage ltk exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 and of its addendum on that one boot, no rebuild, install or boot since N4, post sa12 = V0 in every row of the addendum (the outcome E12); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK), K10's arm words pds=landr and pds=landp and K11's PAD control, armed in N12 only, which did not run (kit/ = resgx545 b4e31c76, branch r46-n3k2 on r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws tri), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-46 and the mark, land, landr and landp images of the running module (round 46's build, E1234-E1245); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 e2964a1917ef4f16afd706345498324960de0e0323304d2d8b273ac94f5d49b3 (144 lines), PREDICTIONS.sha256 e2a8423779d4a5bdb46858aec7a7ce20240fd877d67fecbe0dcc189c1ab8c945 (2 files), pins in FROZEN.commits (the kit and the blob sources at b4e31c76; round 45's kept stages of r45-n3j-n2 to -n6, the scorer's fixtures, at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/ltk.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n10-ltk.txt) and again by hand on the kept directory (fold/reproduce-ltk-20261125-231217.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-26"
data = ["render-closing-r46-n3k-n10:out/20261125-231217/ltk/", "render-closing-r46-n3k-n10:fold/"]
terms = []
+++
**What ran.** land (the 16 dwords of rows L, H3, LC2, LM, LF, LF2, LT, LFF and LFF2 byte for byte:
Ma and Mb to attributes 24 and 26, the doutu, no V0 or V2 and no `tim`, so the tick runs) right
after the plant W10 (E1248), with `begin_draws = "tri"`: between the plant's emit and the image's
ran the plant's disarm and exit resets, this stage's begin reset with one stock triangle and the arm
[HW, the stages' kernel logs; DR passed; DK passed: KC begin delta 8]. Jobs: LM's two (E1198): job 1
the emit on the tick pass, job 2 command 6 on the next tick pass. The question: LT's stage (E1215)
on this module and boot: does a triangle leave (0, 0x02400000, a timer word) again (LTK-SA), and
does land with sa0 0 stop at page 0 (LTK-PAGE0: C-FILL) or at 0x02400000, sa1's page (LTK-SA1: C-E0,
C-E0+, C-MOD), or past both (LTK-PAST)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n10-ltk.txt) and again by
hand on the kept directory, the same bytes:

```
SUMMARY: ltk: controls: ltk1-a:B: FAILED; ltk1-a:J2: FAILED
Q128-N3K-LTK RULE: LTK-E12, LTK-PAST
PREDICTION LTK-E12: predicted held, read held: held
PREDICTION LTK-PAGE0: predicted failed, read FAILED: held
PREDICTION LTK-PAST: predicted failed, read held: FAILED
PREDICTION LTK-SA: predicted held, read FAILED: FAILED
PREDICTION LTK-SA1: predicted held, read FAILED: FAILED
PREDICTION LTK-SERVE: predicted failed, read FAILED: held
```

PLANT (W-SA1 of stage w10), PG, E0, T0, J1, DR, DK and SV passed; B (BIF_FAULT 0 after the row) and
J2 (job 2 done) failed, read by LTK-SA1, LTK-PAGE0, LTK-PAST and LTK-SERVE (the outcomes that name
the stop). LTK-E12 held as predicted. **LTK-SA failed against its prediction (held): sa0 2, not 0,
and sa1 0x01000000, not 0x02400000 (sa2 a timer word). LTK-SA1 failed against its prediction (held):
no fault at 0x02400000. LTK-PAST read held against its prediction (failed): the stop faulted at
neither page 0 nor 0x02400000,** but at 0x01000000, the post sa1. LTK-PAGE0 and LTK-SERVE failed as
predicted.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 **0x00000002**, sa1 **0x01000000**, sa2 0x01061a74 (an EVENT_TIMER sample's
  shape, sa02kind LF; not LFK's 0x0103cb65), sa12 = pa0 = V0 0x32004000, sa13 = pa1 = M13; post
  sa3-sa31 and pa0-pa15 equal W10's word for word (sa24 and sa26, pa12 and pa14, already held land's
  markers Ma and Mb).
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x0100000f** (list 15, page
  0x01000000; the scorer: job 1's post sa1), post the same; job 2 not done (cmd_after 6, dwords
  224-255 still 0xdeadc0de); the tick stopped; snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r46-n3k-logs/health-r46-n3k-n10.log).
- The kernel: the arm's stop line "2 events seen"; KC begin N0 339, delta 8, as one triangle gives;
  HKC (printed): tri 1: 3:22 K 2 0x02400000; 3:4 K 2 0x02000010; the end KC cannot tell (no exit
  load after the stop).

**What it shows.** After one triangle land read sa0 2, sa1 0x01000000 and a timer word, LFK's shape
after one fill (E1247), where T and T2 (E1193, E1204) read sa1 0x02400000 after a triangle and LT
and ZT (E1215, E1221) read (0, 0x02400000) **[HW]**. The reads of a triangle alone now disagree in
sa0 and sa1 **[HW]**: "a triangle writes attributes 0-2 together, 0 and its word" (E1215, E1221) and
the four agreeing reads of 0x02400000 (E1204) do not hold on every read **[HW against LTK-SA]**. The
HKC line printed the triangle's 3:22 entry with 0x02400000 at K 2, as H-KC names it for T, LT and
ZT, so the event H-KC reads as sa1's source was logged and sa1 did not read it **[HW printed; infer
that the entry is that source]**. With sa0 2 the stop faulted at sa1's page, not page 0 and not
0x02400000 **[HW]**; 0x01000000 is a page the stop faults at, a second time (LFK) **[HW]**. C-FILL
named page 0 here too and failed **[HW]**; but sa0 read 2, not 0, so this row did not read whether
sa0 0 misses page 0 on this boot, the design's question for LTK-SA1 **[open]**.

**What it does not show.** What wrote 2 and 0x01000000 after a triangle; whether the draw's words
and the emit's read race (H-RACE) **[infer]**; whether 0x02400000 is mapped; one run of this stage.
