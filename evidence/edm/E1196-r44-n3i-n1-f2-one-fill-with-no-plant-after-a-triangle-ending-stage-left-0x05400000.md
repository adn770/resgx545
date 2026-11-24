+++
id = "E1196"
claim = "r44-n3i-n1 stage f2 (row F2, no plant, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after TF (E1195) and its default end draws (fill, then triangle, exact at their one try) and the begin draws fill (one stock fill): job 1's post sa1 0x05400000, sa0 = V0, sa2 = V2, sa13 = pa1 = M13; K5 BIF_FAULT 0 before and after and in snap9; every control passed, DR passed, 'Q128-N3I-F2 RULE: F2-QUIET'; F2-N FAILED against its prediction (held), F2-ACC, F2-K and F2-PRIOR failed as predicted, F2-OTHER (printed) held: one fill with no plant left 0x05400000, not row F's 0x01000000"
unit = "edm"
method = "r44-n3i-n1 (render/closing-r44-n3i-n1), stage f2 of the question-closing pass (round 44: row F2, closing29/n3i/design.md section 3.3; flagged class, the user present with a reset ready; the user's decisions A-E of the design all (a), 2026-11-23), dataset render-closing-r44-n3i-n1; attempt out/20261124-005624 (00:59:23; stage f2 ended rc 0 and the driver scored it, score-f2.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest), the one-shot boot of 2026-11-22, no rebuild or boot for round 44; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws and K8's draw lists (begin_draws a comma list of fill and tri, run once in order, each draw kept and exact) (kit/ = resgx545 ce01a0c4, branch r44-n3i, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at ce01a0c4; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws fill, K8), then one row of one job: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the record kept; no gate (own_gate none); the default end draws (fill, then triangle); the blob and form of rounds 42-43 and the mark and crumb3 images, unchanged on the running module (E1180, E1184-E1187); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 8c0e8c34fa55dedf1966d90c614c5694fb7427b073ef8f4c0fd541936601c1b1 (80 lines), PREDICTIONS.sha256 62369452e1d74405034c92d37d77962994537c042499185f09ebf28f2a59001f (9 files), pins in FROZEN.commits (the kit and the blob sources at ce01a0c4; round 43's kept stages N1 w, N1 v and N2 f at data b3df8fc21; t30's source 42c4de7); the frozen predictions predictions/f2.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-f2-20261124-005624.out, the same bytes as score-f2.txt); the JOB, BIF, FAULT, SURVEY, ATTR and EVENTS lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-24"
data = ["render-closing-r44-n3i-n1:out/20261124-005624/f2/", "render-closing-r44-n3i-n1:fold/"]
terms = []
+++
**What ran.** X's emit (E1174: crumb3, sideband 0xc43, T3 stopping the tick) as one quiet job, no
kick, no command after it and no gate, with no plant: right after TF (E1195), whose default end
draws (fill, then triangle) ran after its emit, then TF's disarm and exit resets, this stage's begin
reset, the begin draws fill, one stock fill (K7), and this stage's arm [HW, the stages' kernel logs;
DR passed]. The question: after a stage that ended in a fill then a triangle (TF's default end
draws), does one fill leave F's 0x01000000 (F2-N), an accumulated 0x09000000 (F2-ACC), the kick
count (F2-K) or the word before (F2-PRIOR)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: f2: controls: every control passed
Q128-N3I-F2 RULE: F2-QUIET
PREDICTION F2-ACC: predicted failed, read FAILED: held
PREDICTION F2-K: predicted failed, read FAILED: held
PREDICTION F2-N: predicted held, read FAILED: FAILED
PREDICTION F2-OTHER: predicted printed, read held: printed
PREDICTION F2-PRIOR: predicted failed, read FAILED: held
PREDICTION F2-QUIET: predicted held, read held: held
```

Every control passed, DR included (no PLANT: the design's one unplanted read). **F2-N failed against
its prediction (held).** F2-ACC, F2-K and F2-PRIOR failed as predicted, F2-QUIET held; F2-OTHER
(printed) read held: no frozen outcome names the word. TF's end health drew at its one try (the mark
`health end try 2 fill,tri` counts the stage's health calls, not retries), so F2's cannot-tell rule
on it is not met.

**Results [HW].** Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0 before and
after, snap9 0. Job 1's post sa1 **0x05400000**; sa0 = V0 0x32004000 and sa2 = V2 0x32002000 (crumb3
writes both), sa13 = pa1 = M13 0x005d3000; post sa3-sa31 and pa0-pa15 equal the plant stages' word
for word: only sa1 differs. The kernel: the arm after the begin draws "1 events seen" (printed, not
scored).

The session's last stage; its end draws and the health draw after the session were exact
(closing29/r44-n3i-logs/health-r44-n3i-n1.log).

**What it shows.** One stock fill after a firmware load, with no plant, left 0x05400000 in attribute
1 **[HW]**, not the 0x01000000 one fill left after a plant in row F (E1187), and not M1 kept as in
LF (E1200): one fill has left three different outcomes. The word before the fill was not read; if it
was the 0x04400000 a fill then a triangle leave (E1189), 0x05400000 is that word with 1 added to its
top byte, which no frozen outcome named **[infer]**, not claimed.

**What it does not show.** The word before the fill; what decides a fill's outcome; one run.
