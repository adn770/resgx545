+++
id = "E1160"
claim = "r40-s-sbt stage own (row S-SBT, module 0CDFCDB7, fork f9453424bf71, emitsb14, image crumb3 at fw14, form=fw14, s2 0, flagged, user present): r40-s-pass's job (E1159) with s2 0: our EDM task emitted the word with #14's 14-bit sideband 0x843 on the first tick pass that saw the command, no kick; T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, done: every control passed, 'Q128-ST RULE: ST-DONE: all ran (ST-RUN: #14's sideband alone suffices, on a tick, with s2 = 0)'; post's triangle and fill exact; with E1158, the sideband is what decides whether our emitted program runs"
unit = "edm"
method = "r40-s-sbt (render/closing-r40-s-sbt), stage own and post of the question-closing pass (round 40: row S-SBT of the splits of r39-n3d-z, closing29/n3d/design.md, s2 0 against r40-s-pass, built after SB, S2 and S-PASS; flagged class, the user present with a reset ready), dataset render-closing-r40-s-sbt; attempt out/20261119-174746 (17:47:46, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest), the one-shot boot of r39-n3d-z (E1156), no rebuild and no boot for the session; stock firmware), the kit's owntask job kind (kit/ = resgx545 c3f9f67, its fwtask_run.py byte for byte): our task owntask/emitsb14.blob (asm/fwtask/emitsb14.s, sha256 25b572585ca7950909c86469027eded9eff4c2c2d3b6737e4b7ec5717e5ecbea, asm/fwtask/fwtask.map at c3f9f67) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 0e2853c95a042a87934f8d936cc1bc62cef13c12292e5dbddfc99db618467a16 (48 files), PREDICTIONS.sha256 869d217b4d467bc6dc4b437cea48c1b901528e97fb2d3524fdfb4a5f29ef5847 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14.s and fwtask.map at c3f9f67; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; the sideband 0x843 is a fact of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-s-sbt:out/20261119-174746/own/", "render-closing-r40-s-sbt:out/20261119-174746/post/", "render-closing-r40-s-sbt:fold/"]
terms = []
+++
**What ran.** E1159's job (r40-s-pass) with one change at the arm: no `pds2=req`, so `s2` was
0 (the kernel's arm line: `pds2=0 form=fw14`). Blob emitsb14 (#14's word, sideband 0x843), the
tick pass (no kick), crumb3 in #14's page with U0 0x080401ef. So against R4 (E1154: never
started) only the word's sideband differs. The arm logged `own_code: 644 bytes accepted`; health
ok (204, 234, 262).

**Frozen verdict (as printed).** By the driver and again by hand:

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14 pds2=0 form=fw14
Q128-ST RULE: ST-DONE: all ran (ST-RUN: #14's sideband alone suffices, on a tick, with s2 = 0)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 9 from the command write to 30 ms after the window (37.6 ms; printed, not scored; no kick in this row)
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0 (snap0's 0x0acc 0x010541ae, running) and B all passed.
- c1-a: done after 0.2 ms, echo 1; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2; T 0x005a3305 in snap9; alive false by design.
- The gate and stage post exact; the disarm's reset brought the tick back (299, 328, 355).
- LANDING (printed, not scored): as Z's; pa0 and pa2 are not V0 and V2.

**What it shows.** The sideband alone suffices: from a tick pass with `s2` 0, the row that
differs from R4 (E1154) only in the 14-bit sideband (0x843 for 0) ran the program and our entry
to done. With E1158 (sideband 0, `s2` 0x00020000, kick pass: never started), the sideband is
necessary as well, in these rows: of the six emits from our task with crumb3 in #14's page, the
four with 0x843 ran (E1156, E1157, E1159, E1160, from either pass, `s2` 0 or the request bit)
and the two with 0 never started (E1154, E1158; E1155 read the same, CANNOT TELL by its band).
So the stop after our earlier emits (E1148-E1150, E1153-E1155, E1158) came with sideband 0.

**What it does not show.** Which of the sideband's bits matter, or what they mean (#11's emit
carries 0x0c43, #12's and #14's 0x0843: facts of the data-private read); whether another nonzero
value would do; where the `douta` land; what stops the tick with sideband 0; one job only.
