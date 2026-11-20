+++
id = "E1162"
claim = "r40-n3e-b0 stage own (row B0, module 83FBFD86, fork 423b436e7f80, emitsb14d, image crumb3 at fw14, form=fw14, sideband 0x843, s2 0, flagged, user present): D0's job (E1161) on the r40-kernel build, the control of the sideband rows: our EDM task emitted #14's word on the first tick pass; T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2: every control passed (PG, E0, T0, B), 'Q128-B0 RULE: B0-DONE' as predicted, so the build reproduces ST and D0; sa0-sa31 read the same before the emit and after, and pa0-pa15 of the started entry held no V0 or V2, as D0's (E1161); post's triangle and fill exact"
unit = "edm"
method = "r40-n3e-b0 (render/closing-r40-n3e-b0), stage own and post of the question-closing pass (round 40: row B0, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b0; attempt out/20261119-230303 (23:03:03, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb14d.blob (asm/fwtask/emitsb14d.s, sha256 52c6c8a23db4540d338799ac2b73438f5a0b92dbc68a2b51e8fb0119990867d1, asm/fwtask/fwtask.map at b8528c0; emit word 0xfb20b10800c08184, sideband 0x843) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 e17a2514bc15b602f70776be76e77a2adcc56a6066c6ef3bba78a1c4a859f04a (48 files), PREDICTIONS.sha256 dc41d45471ac0d48099975c9d532e031a2dd08b407ce955701ae89c2531ef845 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-b0:out/20261119-230303/own/", "render-closing-r40-n3e-b0:out/20261119-230303/post/", "render-closing-r40-n3e-b0:fold/"]
terms = []
+++
**What ran.** D0's job (E1161: emitsb14d, #14's word 0xfb20b10800c08184 with sideband 0x843,
`s2` 0, crumb3 at #14's buffer + 0x100, a tick pass, no kick) on the r40-kernel build, the control
row of the sideband ladder (closing29/n3e/design.md section 3.3, B0). The build lets own_arm take
a closed list of emit words, each only with the `form=` that names it, and the `land` image.

**Frozen verdict (as printed).**

```
SUMMARY: own: controls: every control passed
Q128-B0 RULE: B0-DONE: all ran (sideband 0x843 reads RUN; H-DM predicts RUN; H-ALL predicts RUN)
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0 and B passed; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2, T 0x005a3305; 9 ticks from the command write (38.8 ms).
- SURVEY: sa0-sa31 identical before and after (sa0-sa2 0x32004000 0x32005000 0x32002000, sa22
  0x32000000, the rest zero but sa23); pa0-pa15 of the started entry the same 16 words as D0's,
  no V0 or V2.
- The owntask gate after the ok end passed; post exact.

**What it shows.** The new module and boot run ST's and D0's job as before, so the rows that
change one thing against it read the change.

**What it does not show.** Anything about another sideband; where crumb3's `douta` land (L).
