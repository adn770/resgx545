+++
id = "E1237"
claim = "r46-n3k-n1 stage zff2 (row ZFF2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image crumbz at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WA (E1236, M1 in attribute 1) and the begin draws fill, fill: job 1's post sa0 0x00040000, sa1 = M1 0x005d1000, sa2 0x010204c4, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, PLANT, DR, DK and SV included, 'Q128-N3K-ZFF2 RULE: ZFF2-QUIET'; ZFF2-KEEP FAILED against its prediction (held: sa0 was 0x00040000, not 2), ZFF2-FILL2 failed as predicted, ZFF2-OTHER (printed) read held: two fills kept M1 a fourth time with crumb3 or crumbz, and left in sa0 a word no read had shown"
unit = "edm"
method = "r46-n3k-n1 (render/closing-r46-n3k-n1), stage zff2 of the question-closing pass (round 46: row ZFF2, closing29/n3k/design.md section 4.3; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-n1; attempt out/20261125-160752 (16:08:13; stage zff2 ended rc 0 and the driver scored it, score-zff2.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumbz pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill,fill, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-45 and the mark, crumbz, land and landq images, their bytes unchanged in the r46 rebuild, which added landr and landp only; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 7dba4dade3969cefedfa07512de743d5933f41963d85b8bab803fbd73f4b90a2 (109 lines), PREDICTIONS.sha256 870969762787c6fba3f3b3aef8d6cb46c7dc56be3ee4a022eaa8e3f3c108dc9c (4 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/zff2.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-zff2-20261125-160752.out, the same bytes as score-zff2.txt and as closing29/r46-n3k-logs/score-r46-n3k-n1-zff2.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-n1:out/20261125-160752/zff2/", "render-closing-r46-n3k-n1:fold/"]
terms = []
+++
**What ran.** crumbz (17 dwords: crumb3's 12 data dwords and its program without the two douta of V0
and V2, so it writes no attribute; T1-T3 stop the tick as crumb3's) with sideband 0xc43 as one quiet
job, no kick, no command after it and no gate, right after the plant WA (E1236), with the begin
draws fill, fill (K8). Between the plant's emit and this one ran the plant's disarm and exit resets,
this stage's begin reset, two stock fills and this stage's arm (a firmware reload) [HW, the stages'
kernel logs; DR passed: the declared list at try 1, each draw exact; DK passed: KC begin delta 6, as
K9 expects]. The question: do two fills read ZFF's (2, M1, a timer word) a second time with crumbz
(ZFF2-KEEP: H-TRI, three reads of M1), or LFF's (0, 0x04000010, a timer word) (ZFF2-FILL2: held
under H-RACE)? With LFF2 in the same session (E1239): an image effect or none.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: zff2: controls: every control passed
Q128-N3K-ZFF2 RULE: ZFF2-QUIET
PREDICTION ZFF2-FAULT: predicted failed, read FAILED: held
PREDICTION ZFF2-FILL2: predicted failed, read FAILED: held
PREDICTION ZFF2-KEEP: predicted held, read FAILED: FAILED
PREDICTION ZFF2-OTHER: predicted printed, read held: printed
PREDICTION ZFF2-QUIET: predicted held, read held: held
```

Every control passed, PLANT (W-SA1 of stage wa), DR, DK and SV included. **ZFF2-KEEP failed against
its prediction (held): sa1 was M1 and sa2 a timer word, but sa0 was 0x00040000, not 2.** ZFF2-QUIET
held as predicted; ZFF2-FILL2 and ZFF2-FAULT failed as predicted; ZFF2-OTHER (printed) read held.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa0 **0x00040000**, sa1 **0x005d1000 = M1**, sa2 0x010204c4 (an
EVENT_TIMER sample's shape: bit 24 alone in 31:24, bits 23:0 below 400000, the scorer's timer rule),
sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal WA's word for word (sa3-sa12
0x3f800000, V0, 0xbec00000, V2, 0x3f800000, V0, 0x3f400000, V2, 0x3f800000, V0, the plant's words,
printed). The kernel: the arm after the two fills "2 events seen"; KC begin 6 and end 10; HKC
(printed): 0x02000010 and 0x04000010 are H-KC's words for the fills' 3:4 entries at K 2 and 4.

**What it shows.** Two stock fills after a plant left M1 in attribute 1 with crumbz a second time
and with any crumb image a fourth (FF E1191, FF2 E1202, ZFF E1227, ZFF2) **[HW]**, and with land
twice more in this round (LFF2, LFF3: E1239, E1241) **[HW]**; LFF's 0x04000010 (E1217) is the one
read of the list that disagrees. sa2 was a timer word, as in ZFF. sa0 was 0x00040000, where ZFF,
LFF2 and LFF3 read 2 and LFF 0 **[HW]**: the reads of sa0 after two fills now disagree three ways,
and 0x00040000 is neither a fill's slot-0 word nor a word H-KC names for the list **[infer]**.

**What it does not show.** Where 0x00040000 comes from (one read); whether the module, the boot or
the image decides it; one run of this stage.
