+++
id = "E1210"
claim = "r45-n3j-n1 stage f3 (row F3, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WE (E1209, M1 in attribute 1) and the begin draws fill (one stock fill): job 1's post sa1 0x005d1000 = M1, sa0 = V0, sa2 = V2, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, PLANT, DR and DK passed, 'Q128-N3J-F3 RULE: F3-KEEP, X-QUIET', every prediction held (F3-TICK and F3-FILL failed as predicted): one fill kept the planted word, not row F's 0x01000000"
unit = "edm"
method = "r45-n3j-n1 (render/closing-r45-n3j-n1), stage f3 of the question-closing pass (round 45: row F3, closing29/n3j/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n1; attempt out/20261124-210141 (21:05:02; stage f3 ended rc 0 and the driver scored it, score-f3.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot before round 45's sessions N1-N4; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists and K9's command count (the kernel's `loaded ... ccb_sent N` lines of the stage's kernel log, the control DK) (kit/ = resgx545 94f9e501, branch r45-n3j, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-44 and the mark, crumb3 and land images, unchanged on the running module (E1184-E1200); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 9a33a7b190f271fdcddffdfea0442466f802745401fc717ff673b0362ec7b6bc (82 lines), PREDICTIONS.sha256 020b3ac5558ef89d6cb3ecc5d6e4c7bbe8f624e99597e5689966e5036f257059 (11 files), pins in FROZEN.commits (the kit and the blob sources at 94f9e501; round 44's kept stages of r44-n3i-n1 and r44-n3i-n3 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/f3.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-f3-20261124-210141.out, the same bytes as score-f3.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n1:out/20261124-210141/f3/", "render-closing-r45-n3j-n1:fold/"]
terms = []
+++
**What ran.** X's emit (E1174: crumb3, sideband 0xc43, T3 stopping the tick; the 19 dwords of rows
G2 q, F and round 44's reads) as one quiet job, no kick, no command after it and no gate, right
after the plant WE (E1209), with the begin draws fill (K8). Between the plant's emit and this one
ran the plant's disarm and exit resets, this stage's begin reset, one stock fill and this stage's
arm (a firmware reload) [HW, the stages' kernel logs; DR passed: the declared list at try 1, each
draw exact; DK passed: KC begin delta 4, as K9 expects]. The question: does one fill after a plant
keep M1, as LF (E1200) and FF (F3-KEEP), or leave F's 0x01000000 (F3-TICK, E1187) or the fill's 3:4
entry word 0x02000010 (F3-FILL)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: f3: controls: every control passed
Q128-N3J-F3 RULE: F3-KEEP, X-QUIET
PREDICTION F3-FILL: predicted failed, read FAILED: held
PREDICTION F3-KEEP: predicted held, read held: held
PREDICTION F3-OTHER: predicted printed, read FAILED: printed
PREDICTION F3-TICK: predicted failed, read FAILED: held
PREDICTION X-QUIET: predicted held, read held: held
```

Every control passed, PLANT (W-SA1 of stage we), DR and DK included. Every prediction held: F3-KEEP
and X-QUIET held, F3-TICK and F3-FILL failed as predicted; F3-OTHER (printed) read failed.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 **0x005d1000 = M1**; sa0 = V0 0x32004000 and sa2 = V2 0x32002000
(crumb3 writes both); sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal its plant
stage's word for word. The kernel: the arm after the begin draws "1 events seen" (printed, not
scored).

**What it shows.** One stock fill after a plant and a firmware load left M1 in attribute 1 **[HW]**.
Reads of one fill after a plant now stand at four that kept M1 (LF E1200 and LF2 E1213 with land, F3
with crumb3, ZF E1225 with crumbz) and one that read 0x01000000 (F, E1187) **[HW]**: they disagree,
so the one-fill list's word is not known by the two-read rule. That F's word was a stray tick
(H-KC's K 1) is **[infer]**.

**What it does not show.** Why F read 0x01000000; one run of this stage.
