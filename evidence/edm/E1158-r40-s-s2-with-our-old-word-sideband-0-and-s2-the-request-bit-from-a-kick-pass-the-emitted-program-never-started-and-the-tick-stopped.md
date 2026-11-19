+++
id = "E1158"
claim = "r40-s-s2 stage own (row S-S2, module 0CDFCDB7, fork f9453424bf71, emitsk, image crumb3 at fw14, pds2=req, flagged, user present): Z's job (E1156) with our old emit word, sideband 0, instead of #14's: our EDM task emitted with s2 0x00020000 on the pass of a host GETMISCINFO kick; X0 0x5a5a3303 was written, T (0x0acc) kept counting, S1, M4 and state the host's fill and 0, and the EDM's tick stopped 7 ticks from the kick with no BIF fault: every control passed, 'Q128-S2 RULE: S2-NEVER: the program never started (T running, S1 fill): with the kick and s2 = 0x00020000, #14's sideband is needed'; the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r40-s-s2 (render/closing-r40-s-s2), stage own of the question-closing pass (round 40: row S-S2 of the splits of r39-n3d-z, closing29/n3d/design.md, our old word against Z; flagged class, the user present with a reset ready), dataset render-closing-r40-s-s2; attempt out/20261119-170645 (17:06:45; stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest), the one-shot boot of r39-n3d-z (E1156), no rebuild and no boot for the session; stock firmware), the kit's owntask job kind (kit/ = resgx545 a8724ca, its fwtask_run.py byte for byte): our task owntask/emitsk.blob (asm/fwtask/emitsk.s, sha256 75fb66a60316e7e33ce87a68f711ffa6cc78f22991b881c40d5baf252b1b2647, asm/fwtask/fwtask.map at a8724ca) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 pds2=req` after the stage's reset and health pair, then one row c1-a of tester command 1 (`fwtask_run.py run`, `\"kick\": \"miscinfo\"`, timeout 200 ms counted from the kick, `ticks` on; K0 read right after the command write, then one debugfs `miscinfo` read, a GETMISCINFO kick; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 3197ef33a4bd1183696f2775ea3e40fc6284fa1ce001b020e56c1f970099d94c (48 files), PREDICTIONS.sha256 c6aaa8f1fbe59fb4d8e3239d4e0a627800e9ac3721963e7b73f7c846d15b76f0 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsk.s and fwtask.map at a8724ca; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; s2 0x00020000 is a fact of the data-private read of the firmware's #14 emit, no firmware byte; the next session (r40-s-pass, E1159) ran clean on the same boot"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r40-s-s2:out/20261119-170645/own/", "render-closing-r40-s-s2:fold/"]
terms = []
+++
**What ran.** E1156's job (Z) with one change: the emit word. The blob is emitsk (K's, E1155),
whose emit is our old word 0xfb20b00000008184 (`emitpds.tasks.taske #0, r2, r3, r4, #0x0`,
sideband 0), armed without `form=fw14` (the kernel pairs the word with `form=`) and with
`pds2=req`, so `s2` was 0x00020000 as in Z (the kernel's arm line: `pds2=req form=own`). The kick
pass (GETMISCINFO, answered after 202 us), the image crumb3 and its place in #14's page were
Z's. The arm logged `own_code: 684 bytes accepted`; health ok (207, 237, 264).

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14 pds2=req form=own
Q128-S2 RULE: S2-NEVER: the program never started (T running, S1 fill): with the kick and s2 = 0x00020000, #14's sideband is needed
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 7 from the kick (K0) to 30 ms after the window; 16 from the command write (252.5 ms); 9 between the command write and K0
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 6; stop0-regs: bit 16 1, count - tick 6
```

**Results [HW].**

- Controls PG, K0, K1, T0 (snap0's 0x0acc 0x0102c5df, running) and B all passed.
- c1-a: no done within 200 ms (`firmware hung: the tick stopped`), class `hang`, stage rc 4.
- The page: X0 0x5a5a3303; S1, M4 and slots 2-4 0xdeadc0de; state 0.
- T: 0x0104f772 in snap9 and 0x01037967 in the stop dump, bit 24 set and counting: none of
  crumb3's markers.
- The tick: 7 from the kick; `alive_at_stop` false (2127 three times).
- BIF_FAULT 0 throughout; the kit's reset and health pair after the stop were exact (triangle
  `diff: 0 of 4096`, fill `diff: 0 of 2048`), and the next session ran clean.

**What it shows.** With `s2` = 0x00020000 and the kick pass, our word with sideband 0 does not
start the program and the tick stops, as with `s2` 0 from a tick pass (E1148-E1150, E1153,
E1154): #14's sideband is needed **[HW]**; that the program never ran its first instruction
rests, as E1150's, on its first `tim` write reaching 0x0acc, which E1156 now measured for an
emitted program **[infer]**. K's readings (E1155, CANNOT TELL by its band) recur here as a scored
NEVER, with the same 7 ticks from the kick.

**What it does not show.** What stops the tick; what the sideband's bits mean; one job only.
