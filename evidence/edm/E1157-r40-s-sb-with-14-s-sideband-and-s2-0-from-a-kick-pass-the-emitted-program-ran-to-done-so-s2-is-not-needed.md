+++
id = "E1157"
claim = "r40-s-sb stage own (row S-SB, module 0CDFCDB7, fork f9453424bf71, emitsk14, image crumb3 at fw14, form=fw14, s2 0, flagged, user present): Z's job (E1156) with s2 0 instead of 0x00020000: our EDM task emitted the word with #14's 14-bit sideband 0x843 on the pass of a host GETMISCINFO kick; T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, done: every control passed, 'Q128-SB RULE: SB-DONE: all ran (SB-RUN: s2 is not needed: #14's sideband with the kick pass suffices)'; post's triangle and fill exact"
unit = "edm"
method = "r40-s-sb (render/closing-r40-s-sb), stage own and post of the question-closing pass (round 40: row S-SB of the splits of r39-n3d-z, closing29/n3d/design.md, s2 0 against Z; flagged class, the user present with a reset ready), dataset render-closing-r40-s-sb; attempt out/20261119-170536 (17:05:36, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest), the one-shot boot of r39-n3d-z (E1156), no rebuild and no boot for the session; stock firmware), the kit's owntask job kind (kit/ = resgx545 a8724ca, its fwtask_run.py byte for byte): our task owntask/emitsk14.blob (asm/fwtask/emitsk14.s, sha256 d3c2ab1e056d03f871581223eaecfff71861cd7ccc49783709d35c3d2d3c5a45, asm/fwtask/fwtask.map at a8724ca) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, `\"kick\": \"miscinfo\"`, timeout 200 ms counted from the kick, `ticks` on; K0 read right after the command write, then one debugfs `miscinfo` read, a GETMISCINFO kick; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 81f48c38be3062ed7d9b2eeeac3c806464ab7672aaaf589c00086d7b5e799acc (48 files), PREDICTIONS.sha256 b2fa82d4340ac41de6c792b85f2879c7b48fccab3cf3b5fc946e06b4993d2c97 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsk14.s and fwtask.map at a8724ca; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; the sideband 0x843 and s2 0x00020000 are facts of the data-private reads of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-s-sb:out/20261119-170536/own/", "render-closing-r40-s-sb:out/20261119-170536/post/", "render-closing-r40-s-sb:fold/"]
terms = []
+++
**What ran.** E1156's job (Z) with one change at the arm: no `pds2=req`, so the kernel wrote 0
into the blob's `pds2` limm and the emit's `s2` was 0 (the kernel's arm line: `pds2=0
form=fw14`). The word stayed Z's, 0xfb20b10800c08184 (sideband 0x843), and so did the kick pass
(one GETMISCINFO read, answered after 206 us), the image crumb3 (3 data rows, control 0x01800100)
and its place (0x30011100, offset 0x100 of the firmware's PDS #14 page). The arm logged
`own_code: 684 bytes accepted`, and the arm's health was ok (ticks 201, 230, 257).

**Frozen verdict (as printed).** By the driver and again by hand:

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14 pds2=0 form=fw14
Q128-SB RULE: SB-DONE: all ran (SB-RUN: s2 is not needed: #14's sideband with the kick pass suffices)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 7 from the kick (K0) to 30 ms after the window; 15 from the command write (48.5 ms); 8 between the command write and K0
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, K0 (no tick pass emitted), K1, T0 (snap0's 0x0acc 0x01007265, running) and B
  (BIF_FAULT 0) all passed.
- c1-a: done after 10.6 ms, echo 1; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2; T 0x005a3305 in snap9; alive false, as crumb3's first `tim` (a stopped 0) stops the
  tick by design.
- The gate (tick stopped) and stage post drew the triangle and the fill exactly; the disarm's
  reset brought the tick back (290, 319, 347).
- LANDING (printed, not scored): as Z's; pa0 and pa2 are not V0 and V2.

**What it shows.** With #14's sideband and a kick pass, `s2` 0 is enough: the emitted program
ran and started our entry to done. `s2` = 0x00020000 is not needed.

**What it does not show.** Whether the sideband is needed (E1158) or the kick pass (E1159,
E1160); what the sideband's bits mean; where the `douta` land; one job only.
