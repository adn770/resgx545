+++
id = "E1167"
claim = "r40-n3e-b4 stage own (row B4, module 83FBFD86, fork 423b436e7f80, emitsb_sb840, image crumb3 at fw14, form=sb840, sideband 0x840, s2 0, flagged, user present): B0's job with bits 1:0 of the sideband cleared: X0 0x5a5a3303 (the issuer went on past the emit), S1 and M4 the host's fill, state 0, T running (0x0104aad3, 0x01001169), BIF_FAULT 0: every control passed, 'Q128-B4 RULE: B4-NEVER' as predicted; the runner stopped (class hang, rc 4) and the kit's reset and health recovered it"
unit = "edm"
method = "r40-n3e-b4 (render/closing-r40-n3e-b4), stage own of the question-closing pass (round 40: row B4, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b4; attempt out/20261119-230834 (23:08:34, stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sb840.blob (asm/fwtask/emitsb_sb840.s, sha256 ec7d4429ad27185b304650b84a3aabaf4ad673a994014ed61240140019a3c62c, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b10800008184, sideband 0x840) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb840` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9, the runner stop dump) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 971123e59a5e081ba97e34a06c6bcc008019668c6e1fe55c31d3bb7c53fa90ac (49 files), PREDICTIONS.sha256 e813c8d9c524cc34ba6785313435f9892c342f5f16353aafa294825cf6d7a68c (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sb840.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-own*.out: the stage stopped, so the driver did not score it); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-b4:out/20261119-230834/own/", "render-closing-r40-n3e-b4:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_840, armed at
`form=sb840`, sideband 0x840.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out; the stage
stopped at its one row, rc 4, so the driver did not score it):

```
SUMMARY: own: controls: every control passed
Q128-B4 RULE: B4-NEVER: the program never started (T running, S1 fill) (sideband 0x840 reads NEVER; H-DM predicts NEVER; H-ALL predicts NEVER)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
```

**Results [HW].**

- Controls PG, E0, T0 and B passed; X0 0x5a5a3303; S1, M4 and the survey slots the host's fill
  (0xdeadc0de); state 0; T 0x0104aad3 and 0x01001169 in snap9 and the stop dump, bit 24 set and counting: none of
  crumb3's markers.
- No done within 200 ms, class `hang`, stage rc 4; BIF_FAULT 0; the kit's reset and health pair
  after the stop were ok (fill and triangle). Post not run.

**What it shows.** With bits 1:0 of the sideband 0 the program does not start, as with our old
sideband 0 (E1158) **[HW]**; that it never ran its first instruction rests on its first `tim`
not reaching 0x0acc **[infer, as E1158]**.

**What it does not show.** What stops the tick; one job only.
