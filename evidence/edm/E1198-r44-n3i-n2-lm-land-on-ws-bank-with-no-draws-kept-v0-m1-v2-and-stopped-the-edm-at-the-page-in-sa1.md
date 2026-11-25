+++
id = "E1198"
claim = "r44-n3i-n2 stage lm (row LM, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WL (E1197) with no client draw between (only resets, the register health and the arm, K7): job 1 done with post sa0 = V0 0x32004000, sa1 = M1 0x005d1000, sa2 = V2 0x32002000, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d100f (list 15, page 0x005d1000, the post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3I-LM RULE: LM-EARLY1, LM-KEEP, LM-V0', every prediction held: on W's bank land stops at the page in sa1 as landv did, not at page 0"
unit = "edm"
method = "r44-n3i-n2 (render/closing-r44-n3i-n2), stage lm of the question-closing pass (round 44: row LM, closing29/n3i/design.md section 3.4; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r44-n3i-n2; attempt out/20261124-010001 (01:00:22; stage lm exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 44; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws and K8's draw lists (begin_draws a comma list of fill and tri, run once in order, each draw kept and exact) (kit/ = resgx545 ce01a0c4, branch r44-n3i, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at ce01a0c4; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none: the register health, no draw), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-43, unchanged on the running module (E1184-E1187), and the land image of rounds 40-41 (E1176, E1178), its first run on this module; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 2703a95fd7a7ee8e3f0d9ed371fcffe7703264ba2004865bd541435049f89344 (66 lines), PREDICTIONS.sha256 b8862f8fb1181dda015dda98001425c716e4549313d01544df61dee0d6b96889 (2 files), pins in FROZEN.commits (the kit and the blob sources at ce01a0c4; round 43's kept stages N1 w, N1 v and N2 f at data b3df8fc21; t30's source 42c4de7); the frozen predictions predictions/lm.tsv, the rule score/score.py, scored after the session (closing29/r44-n3i-logs/score-r44-n3i-n2-lm.txt) and again by hand on the kept directory (fold/reproduce-lm-20261124-010001.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-24"
data = ["render-closing-r44-n3i-n2:out/20261124-010001/lm/", "render-closing-r44-n3i-n2:fold/"]
terms = []
+++
**What ran.** land (rows L, H3 and LC2's 16 dwords byte for byte: Ma and Mb to attributes 24 and 26,
the doutu, no V0 or V2 and no `tim`, so the tick runs) right after the plant WL (E1197), with
`begin_draws = "none"`: between the plant's emit and land's ran the plant's disarm and exit resets,
this stage's begin reset with the register health (no draw) and the arm [HW, the stages' kernel
logs; DR passed]. Jobs: V's two (E1185): job 1 the emit on the tick pass, job 2 command 6 on the
next tick pass. The question: with land on the bank V had (sa0 = V0, sa1 = M1), does the early stop
fault at M1's page (LM-EARLY1, H-SA0) or at page 0 as LC's (LM-EARLY0, H-IMG)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r44-n3i-logs/score-r44-n3i-n2-lm.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: lm: controls: lm1-a:B: FAILED; lm1-a:J2: FAILED
Q128-N3I-LM RULE: LM-EARLY1, LM-KEEP, LM-V0
PREDICTION LM-EARLY0: predicted failed, read FAILED: held
PREDICTION LM-EARLY1: predicted held, read held: held
PREDICTION LM-EARLY13: predicted failed, read FAILED: held
PREDICTION LM-KEEP: predicted held, read held: held
PREDICTION LM-OTHER: predicted printed, read FAILED: printed
PREDICTION LM-SERVE: predicted failed, read FAILED: held
PREDICTION LM-V0: predicted held, read held: held
```

PLANT (W-SA1 of stage wl), PG, E0, T0, J1 and DR passed; B (BIF_FAULT 0 after the row) and J2 (job 2
done) failed, read by LM-EARLY1, which names the stop (the frozen rule of X, LC2, LV, V and F).
Every prediction held: LM-V0, LM-KEEP and LM-EARLY1 held; LM-EARLY0, LM-EARLY13 and LM-SERVE failed
as predicted; LM-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 = V0 0x32004000, sa1 = M1 0x005d1000, sa2 = V2 0x32002000, sa13 = pa1 = M13; post
  sa3-sa31 and pa0-pa15 equal WL's word for word.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT 0x005d100f (list 15, page 0x005d1000 =
  M1 = the post sa1), post the same; job 2 not done (cmd_after 6, dwords 224-255 still 0xdeadc0de);
  the tick stopped (the runner's alive check); snap9 and the stop dump the same fault. The kit's
  reset and both draws recovered it (health ok, closing29/r44-n3i-logs/health-r44-n3i-n2.log).
- The kernel: lm's arm with no draws "0 events seen"; the recovery's reset after both draws "3
  events seen".

**What it shows.** With no client draw after W's plant, land's rewrite left sa0 = V0, sa1 = M1 and
sa2 = V2 **[HW]**, the bank V had (E1185), though land writes none of attributes 0-2. On that bank
land stopped after the emit's pass exactly as landv did: at the page in sa1 (M1) **[HW]**. So H-IMG
fails: land's image did not cause LC's page 0 (E1176, E1178); LC's bank did **[HW for land on this
bank; infer for LC's]**. That the post sa0 and sa2 are attributes 0 and 2 kept from W's `douta`
across the boundary, as attribute 1 is (E1185), and not words the rewrite leaves alone, is
**[infer]**: W wrote the same V0 and V2 the EDM held before.

**What it does not show.** Which access of the tick pass read sa1's page; why the stop does not
fault at sa0's page here (sa0 = V0 is a page the kernel maps, **[infer]**); one run.

**Correction 2026-11-25:** Round 45's row ZN (E1219) read the same bank with crumbz, which writes no
attribute: sa0 = V0, sa1 = M1, sa2 = V2 after W's plant and no draws **[HW]**. So this record's
**[infer]** that the post sa0 and sa2 are attributes 0 and 2 kept from W's `douta` across the
boundary is now measured twice. Row Q (E1233) faulted at sa1's page with sa0 holding 0x005d2000, so
"why the stop does not fault at sa0's page here" has two readings: sa0's word is mapped, or the
lowest faulting page is kept **[infer]**. This record's frozen verdict and readings stand.

**Correction 2026-11-25 (round 46):** Round 46's land rows on module 10BBF3BF (fork r46-kernel
c5094783eb88) stopped with sa0 2 and M1 in sa1 at 0x005d1000, sa1's page, not at page 0: after two
fills twice (LFF2 E1239, LFF3 E1241) and after three (LF3F E1243), the PAGE0 outcome FAILED against
its prediction (held) each time **[HW]**. So the stop does not fault at page 0 whenever sa0 holds a
word below one page, and the two readings row Q left (the lowest faulting page kept; sa0 read first
with 0x005d2000 mapped) both predicted page 0 there **[HW against the frozen predictions]**. The
earlier page-0 stops ran on modules 83FBFD86 and 079DD0D1, and the two with the bank (2, M1), LF and
LF2, after one fill: the module and the number of fills changed together, and no row splits them
**[infer]**. Row Q's stop at sa1's page with 0x005d2000 in sa0 repeated on 10BBF3BF (Q2, E1245)
**[HW]**. This record's stop at sa1's page with sa0 = V0 is not contradicted; the two readings the
2026-11-25 correction gave for why it was not at sa0's page both fail on round 46's (2, M1) bank, so
neither is carried as the rule **[infer]**. This record's frozen verdict and readings stand.
