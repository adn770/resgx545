+++
id = "E1193"
claim = "r44-n3i-n1 stage t (row T, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant WC (E1192, M1 in attribute 1) and the begin draws tri (one triangle alone): job 1's post sa1 0x02400000, sa0 = V0, sa2 = V2, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, PLANT and DR passed, 'Q128-N3I-T RULE: T-K, X-QUIET'; T-N FAILED against its prediction (held), T-K FAILED against its prediction (failed; read held), T-LAST and X-KEEP failed as predicted: a triangle alone rewrote attribute 1 to 0x02400000"
unit = "edm"
method = "r44-n3i-n1 (render/closing-r44-n3i-n1), stage t of the question-closing pass (round 44: row T, closing29/n3i/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r44-n3i-n1; attempt out/20261124-005624 (00:58:16; stage t ended rc 0 and the driver scored it, score-t.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 44; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws and K8's draw lists (begin_draws a comma list of fill and tri, run once in order, each draw kept and exact) (kit/ = resgx545 ce01a0c4, branch r44-n3i, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at ce01a0c4; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws tri, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-43 and the mark and crumb3 images, unchanged on the running module (E1180, E1184-E1187); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 8c0e8c34fa55dedf1966d90c614c5694fb7427b073ef8f4c0fd541936601c1b1 (80 lines), PREDICTIONS.sha256 62369452e1d74405034c92d37d77962994537c042499185f09ebf28f2a59001f (9 files), pins in FROZEN.commits (the kit and the blob sources at ce01a0c4; round 43's kept stages N1 w, N1 v and N2 f at data b3df8fc21; t30's source 42c4de7); the frozen predictions predictions/t.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-t-20261124-005624.out, the same bytes as score-t.txt); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-24"
data = ["render-closing-r44-n3i-n1:out/20261124-005624/t/", "render-closing-r44-n3i-n1:fold/"]
terms = []
+++
**What ran.** X's emit (E1174: crumb3, sideband 0xc43, T3 stopping the tick; G2 q's and F's 19
dwords) as one quiet job, no kick, no command after it and no gate, right after the plant WC
(E1192), with the begin draws tri (K8). Between the plant's emit and this one ran the plant's disarm
and exit resets, this stage's begin reset, one 64x64 triangle alone and this stage's arm (a firmware
reload) [HW, the stages' kernel logs; DR passed: the declared list at try 1, each draw exact]. The
question: does a triangle alone leave a count of 3 (T-N), the fill-then-triangle word (T-LAST) or
the kick count (T-K, 0x02400000 or 0x02000010)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: t: controls: every control passed
Q128-N3I-T RULE: T-K, X-QUIET
PREDICTION T-K: predicted failed, read held: FAILED
PREDICTION T-LAST: predicted failed, read FAILED: held
PREDICTION T-N: predicted held, read FAILED: FAILED
PREDICTION X-KEEP: predicted failed, read FAILED: held
PREDICTION X-OTHER: predicted printed, read FAILED: printed
PREDICTION X-QUIET: predicted held, read held: held
```

Every control passed, PLANT (W-SA1 of stage wc) and DR included. **T-N failed against its prediction
(held).** **T-K failed against its prediction (failed): it read held.** T-LAST and X-KEEP failed as
predicted, X-QUIET held; X-OTHER (printed) read failed.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 **0x02400000**; sa0 = V0 0x32004000 and sa2 = V2 0x32002000 (crumb3
writes both), sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal the plant stages' word
for word: only sa1 differs. The kernel: the arm after the begin draws "2 events seen" (printed, not
scored).

**What it shows.** A triangle alone after a firmware load rewrote attribute 1 from M1 to 0x02400000
**[HW]**: top byte 2, not H-N's 3 or the fill-then-triangle word's 4, low bits bit 22 as after a
fill then a triangle. The word is the one H-K named, but H-K's words for FF and TF failed (E1191,
E1195), so the match is not taken as H-K holding **[infer]**. That the top byte counts something
(the kernel's events, 2 here, 3 with fill then triangle, do not equal it) is **[infer]** and not
claimed.

**What it does not show.** What the word means; whether a second triangle changes it; one run.
