+++
id = "E1223"
claim = "r45-n3j-n5 stage zft (row ZFT, module EC553F41, fork b1089172b2e7, emitsb_sbc43s, image crumbz at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WL (E1222) and the begin draws fill, tri: job 1's post sa0 0, sa1 0x04400000, sa2 0x010201bd, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, PLANT, DR, DK, SV and ZN passed, 'Q128-N3J-ZFT RULE: Z-QUIET, ZFT-SA1, ZFT-TRIPLE', every prediction held (ZFT-ONE failed as predicted): a fill then a triangle left (0, 0x04400000, a timer word)"
unit = "edm"
method = "r45-n3j-n5 (render/closing-r45-n3j-n5), stage zft of the question-closing pass (round 45: row ZFT, closing29/n3j/design.md section 9.4; flagged class, the user present with a reset ready; the user's decisions of the design A=a, B=a, C=a, D=b, E=c, F=a), dataset render-closing-r45-n3j-n5; attempt out/20261125-092017 (09:22:32; stage zft ended rc 0 and the driver scored it, score-zft.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion EC553F41FD8324BB6BF1764 installed and loaded alike (control SV), linux fork r45-kernel b1089172b2e7, r42-kernel plus the crumbz and landq images, built on cachix 2026-11-24 (closing29/kernel39c/deliver/b1089172b2e7/manifest, closing29/kernel39c/r45-kernel-check.pass, closing29/r45-n3j-fork-logs/cachix-wait.log), the second one-shot boot of 2026-11-25 (closing29/r45-n3j-z-logs/boot2.log; the first ended in a hard hang of the laptop, unexplained, render-closing-r45-n3j-n5's fold/FOLD-NOTES.md); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and the arm words pds=crumbz and pds=landq (kit/ = resgx545 cf20aa87, branch r45-n3j-z, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at b1089172b2e7 on the Mac shim, 48 of 48 (closing29/r45-n3j-fork-logs/shim-r45-green-fork.log; r45-red 45 of 48, shim-r45-red-fork.log), with the round's own suite 50 of 50 (shim-r45-green.log; r45-red 46 of 50, shim-r45-red.log; a wrong expected word fails, 49 of 50, shim-r45-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumbz pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill,tri, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-44 and the mark image, their bytes unchanged in the rebuild, and our own crumbz and landq images (asm/fwtask/pds/crumbz.s and landq.s at cf20aa87, assembled with pds-asm, no firmware bytes), their first runs; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 d36b375b4ab794bc369c31a4a026d26ca4c501e717415ca30d53c47523e5cef6 (89 lines), PREDICTIONS.sha256 e63ce70fab0cdf56007c6055002646d98c85778270dc68840131f09f97ab3a8a (14 files), pins in FROZEN.commits (the kit and the blob sources at cf20aa87; round 44's kept stages of r44-n3i-n1 and r44-n3i-n2 at data ebfeaa775; t30's source 42c4de7); the frozen predictions predictions/zft.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-zft-20261125-092017.out, the same bytes as score-zft.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r45-n3j-n5:out/20261125-092017/zft/", "render-closing-r45-n3j-n5:fold/"]
terms = []
+++
**What ran.** crumbz (17 dwords: crumb3's 12 data dwords and its program without the two douta of V0
and V2, so it writes no attribute; T1-T3 stop the tick as crumb3's) with sideband 0xc43 as one quiet
job, no kick, no command after it and no gate, right after the plant WL (E1222), with the begin
draws fill,tri (K8). Between the plant's emit and this one ran the plant's disarm and exit resets,
this stage's begin reset, one stock fill, then one 64x64 triangle and this stage's arm (a firmware
reload) [HW, the stages' kernel logs; DR passed: the declared list at try 1, each draw exact; DK
passed: KC begin delta 10, as K9 expects]. The question: after a fill then a triangle, does crumbz
read LC's triple shape, sa0 0, sa1 0x04400000 (or X's 0x04000010) and a timer word (ZFT-SA1,
ZFT-TRIPLE), on this module?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: zft: controls: every control passed
Q128-N3J-ZFT RULE: Z-QUIET, ZFT-SA1, ZFT-TRIPLE
PREDICTION Z-FAULT: predicted failed, read FAILED: held
PREDICTION Z-QUIET: predicted held, read held: held
PREDICTION ZFT-AOTHER: predicted printed, read FAILED: printed
PREDICTION ZFT-ONE: predicted failed, read FAILED: held
PREDICTION ZFT-SA1: predicted held, read held: held
PREDICTION ZFT-TRIPLE: predicted held, read held: held
```

Every control passed, PLANT (W-SA1 of stage wl), DR, DK, SV and ZN (stage zn's ZN-SAME) included.
Every prediction held: ZFT-SA1, ZFT-TRIPLE and Z-QUIET held, ZFT-ONE and Z-FAULT failed as
predicted; ZFT-AOTHER (printed) read failed.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 **0x04400000**; sa0 0x00000000 and sa2 0x010201bd (crumbz writes
neither); sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal its plant stage's word for
word. The kernel: the arm after the begin draws "3 events seen" (printed, not scored).

The sa2 word has an EVENT_TIMER sample's shape (bit 24 alone in 31:24, bits 23:0 below 400000, not
the tick's grid word 0x061a70, E1133): the scorer's timer rule.

**What it shows.** A fill then a triangle after a plant left sa0 0, sa1 0x04400000 and a timer word
**[HW]**: the triple LC and LC2 read with land and no plant (E1176, E1178), and sa1 the word of FT
(E1189) and the six unplanted rows of n3i's section 0.1 **[HW]**. X's 0x04000010 (E1174) remains the
one read of this list that disagrees, so the list's sa1 is not known by the two-read rule, while its
sa0, 0 in ZFT, LC and LC2, is.

**What it does not show.** Why X read 0x04000010; one run of this stage.
