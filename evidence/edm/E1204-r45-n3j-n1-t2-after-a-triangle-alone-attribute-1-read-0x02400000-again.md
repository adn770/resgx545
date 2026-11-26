+++
id = "E1204"
claim = "r45-n3j-n1 stage t2 (row T2, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WB (E1203, M1 in attribute 1) and the begin draws tri (one triangle alone): job 1's post sa1 0x02400000, sa0 = V0, sa2 = V2, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, PLANT, DR and DK passed, 'Q128-N3J-T2 RULE: T2-SAME, X-QUIET', every prediction held (T2-34 and T2-KEEP failed as predicted): a triangle alone left 0x02400000 a second time, as T (E1193)"
unit = "edm"
method = "r45-n3j-n1 (render/closing-r45-n3j-n1), stage t2 of the question-closing pass (round 45: row T2, closing29/n3j/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n1; attempt out/20261124-210141 (21:02:48; stage t2 ended rc 0 and the driver scored it, score-t2.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot before round 45's sessions N1-N4; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists and K9's command count (the kernel's `loaded ... ccb_sent N` lines of the stage's kernel log, the control DK) (kit/ = resgx545 94f9e501, branch r45-n3j, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws tri, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-44 and the mark, crumb3 and land images, unchanged on the running module (E1184-E1200); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 9a33a7b190f271fdcddffdfea0442466f802745401fc717ff673b0362ec7b6bc (82 lines), PREDICTIONS.sha256 020b3ac5558ef89d6cb3ecc5d6e4c7bbe8f624e99597e5689966e5036f257059 (11 files), pins in FROZEN.commits (the kit and the blob sources at 94f9e501; round 44's kept stages of r44-n3i-n1 and r44-n3i-n3 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/t2.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-t2-20261124-210141.out, the same bytes as score-t2.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n1:out/20261124-210141/t2/", "render-closing-r45-n3j-n1:fold/"]
terms = []
+++
**What ran.** X's emit (E1174: crumb3, sideband 0xc43, T3 stopping the tick; the 19 dwords of rows
G2 q, F and round 44's reads) as one quiet job, no kick, no command after it and no gate, right
after the plant WB (E1203), with the begin draws tri (K8). Between the plant's emit and this one ran
the plant's disarm and exit resets, this stage's begin reset, one 64x64 triangle alone and this
stage's arm (a firmware reload) [HW, the stages' kernel logs; DR passed: the declared list at try 1,
each draw exact; DK passed: KC begin delta 8, as K9 expects]. The question: does a triangle alone
leave 0x02400000 a second time (T2-SAME, T's read, E1193), its 3:4 variant 0x02000010 (T2-34) or the
planted word (T2-KEEP)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: t2: controls: every control passed
Q128-N3J-T2 RULE: T2-SAME, X-QUIET
PREDICTION T2-34: predicted failed, read FAILED: held
PREDICTION T2-KEEP: predicted failed, read FAILED: held
PREDICTION T2-OTHER: predicted printed, read FAILED: printed
PREDICTION T2-SAME: predicted held, read held: held
PREDICTION X-QUIET: predicted held, read held: held
```

Every control passed, PLANT (W-SA1 of stage wb), DR and DK included. Every prediction held: T2-SAME
and X-QUIET held, T2-34 and T2-KEEP failed as predicted; T2-OTHER (printed) read failed.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 10 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 **0x02400000**; sa0 = V0 0x32004000 and sa2 = V2 0x32002000 (crumb3
writes both); sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal its plant stage's word
for word. The kernel: the arm after the begin draws "2 events seen" (printed, not scored).

**What it shows.** A triangle alone after a plant and a firmware load left 0x02400000 in attribute 1
a second time **[HW, T E1193 and T2]**; crumbz and land read the same word after it (ZT E1221, LT
E1215): four reads agree and none disagrees. That 0x02400000 is the pa1 of the triangle's slot-3
entry 3:22 with the count byte K 2, the CCB commands since the load (H-KC, E768), is **[infer]**.

**What it does not show.** What the word's bit 22 means; one run of this stage.

**Correction 2026-11-26 (round 46 addendum):** Row LTK (E1249), LT's stage on module 10BBF3BF (fork
r46-kernel c5094783eb88) after a plant and one stock triangle, read post sa0 2, sa1 0x01000000 and a
timer word, and stopped at 0x01000000, sa1's page, not at page 0; LTK-SA (sa0 0, sa1 0x02400000)
FAILED against its prediction (held) **[HW]**, while the kernel's HKC line printed the triangle's
3:22 entry with 0x02400000 at K 2 as before. So the reads of a triangle alone after a plant
disagree: 0x02400000 in T, T2, LT and ZT (E1193, E1204, E1215, E1221), 0x01000000 in LTK; sa0 0 in
LT and ZT, 2 in LTK **[HW]**. One fill on the same boot read the same pair (2, 0x01000000) once and
(2, M1) once (LFK E1247, LFK2 E1251) **[HW]**; that the word read depends on timing (H-RACE) is
**[infer]**. This record's "four reads agree and none disagrees" no longer holds: the triangle's sa1
is not known by the two-read rule. This record's frozen verdict and readings stand.
