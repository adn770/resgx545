+++
id = "E1159"
claim = "r40-s-pass stage own (row S-PASS, the design's row S, module 0CDFCDB7, fork f9453424bf71, emitsb14, image crumb3 at fw14, pds2=req form=fw14, flagged, user present): Z's word and s2 (E1156) emitted by emitsb14 on the first tick pass that saw the command, no kick; T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, done: every control passed, 'Q128-SP RULE: SP-DONE: all ran (SP-RUN: the kick pass is not needed: #14's word and s2 suffice on a tick)'; post's triangle and fill exact"
unit = "edm"
method = "r40-s-pass (render/closing-r40-s-pass), stage own and post of the question-closing pass (round 40: row S-PASS of the splits of r39-n3d-z, closing29/n3d/design.md, the timer pass against Z, the design's row S; flagged class, the user present with a reset ready), dataset render-closing-r40-s-pass; attempt out/20261119-170734 (17:07:34, rc 0; stages own and post; right after r40-s-s2's stop and reset); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest), the one-shot boot of r39-n3d-z (E1156), no rebuild and no boot for the session; stock firmware), the kit's owntask job kind (kit/ = resgx545 c3f9f67, its fwtask_run.py byte for byte): our task owntask/emitsb14.blob (asm/fwtask/emitsb14.s, sha256 25b572585ca7950909c86469027eded9eff4c2c2d3b6737e4b7ec5717e5ecbea, asm/fwtask/fwtask.map at c3f9f67) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 pds2=req form=fw14` after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 24f371a36f35e77505bcca7e6b596fe962251ba00a7574baf1f9616814413195 (48 files), PREDICTIONS.sha256 f77107770b80305531ee1c5b8818ac59ad72e41cdb7f87c0dc348e294b381a1f (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14.s and fwtask.map at c3f9f67; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; the sideband 0x843 and s2 0x00020000 are facts of the data-private reads of the firmware's emits, no firmware byte; the module's verifier accepts emitsb14 unchanged (the fork's KUnit on the Mac shim, 34 of 34, closing29/r40-s-logs/shim-emitsb14.log)"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-s-pass:out/20261119-170734/own/", "render-closing-r40-s-pass:out/20261119-170734/post/", "render-closing-r40-s-pass:fold/"]
terms = []
+++
**What ran.** E1156's job (Z) with one change: the pass. emitsb14 (resgx545 c3f9f67) is
emitsb (E1149, E1154) with #14's emit word 0xfb20b10800c08184 and nothing else, so it emits on
the first pass that sees command 1, a tick, as R4 (E1154) did; the row has no kick. The arm was
Z's (`pds2=req form=fw14`: `s2` 0x00020000) and the image crumb3 in #14's page, with emitsb's
entry 1 in its U0 (0x080401ef, R4's). The arm logged `own_code: 644 bytes accepted`; health ok
(201, 230, 258).

**Frozen verdict (as printed).** By the driver and again by hand:

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14 pds2=req form=fw14
Q128-SP RULE: SP-DONE: all ran (SP-RUN: the kick pass is not needed: #14's word and s2 suffice on a tick)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 9 from the command write to 30 ms after the window (38.3 ms; printed, not scored; no kick in this row)
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0 (snap0's 0x0acc 0x01050794, running) and B all passed.
- c1-a: done after 0.6 ms, echo 1; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2; T 0x005a3305 in snap9; alive false by design (crumb3's first `tim`).
- The gate and stage post exact; the disarm's reset brought the tick back (297, 326, 353).
- LANDING (printed, not scored): as Z's; pa0 and pa2 are not V0 and V2.

**What it shows.** With #14's word and `s2`, the emit from our task's tick pass runs the program
and its entry to done: the kick pass is not needed. R4 (E1154) differed from this row only in
the word and `s2`, and never started.

**What it does not show.** Whether `s2` is needed on a tick pass (E1160); the sideband's bits;
where the `douta` land; one job only.
