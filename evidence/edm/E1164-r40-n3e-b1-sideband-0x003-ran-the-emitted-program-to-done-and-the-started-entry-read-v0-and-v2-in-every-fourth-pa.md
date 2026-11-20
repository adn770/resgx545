+++
id = "E1164"
claim = "r40-n3e-b1 stage own (row B1, module 83FBFD86, fork 423b436e7f80, emitsb_sb003, image crumb3 at fw14, form=sb003, sideband 0x003, s2 0, flagged, user present): B0's job with bits 6 and 11 of the sideband cleared: T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2: every control passed, 'Q128-B1 RULE: B1-DONE' (H-DM predicted RUN: held; H-ALL predicted NEVER: failed), so bits 6 and 11 are not needed for the start with bits 1:0 = 3; sa0-sa31 read the same before the emit and after; the started entry read V0 (0x32004000) in pa0, pa4, pa8 and pa12 and V2 (0x32002000) in pa2, pa6, pa10 and pa14, where the rows with 0x843 read neither (E1161, E1162); post exact"
unit = "edm"
method = "r40-n3e-b1 (render/closing-r40-n3e-b1), stage own and post of the question-closing pass (round 40: row B1, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b1; attempt out/20261119-230535 (23:05:35, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sb003.blob (asm/fwtask/emitsb_sb003.s, sha256 44ed1d2e865ed0a4f223dfe7c2d8bfe7fe8c88a5c146d604d50ef59e51e24188, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b00000c08184, sideband 0x003) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb003` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 05b1d5814ae228ddafbc2073df92a1b09435717c5aaf64253535b63c5c26ba0a (49 files), PREDICTIONS.sha256 a7294fb2f8901bd67210aaf42bf6e6a8e0f41ae4df44b9c045c0d5440051aab1 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sb003.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-b1:out/20261119-230535/own/", "render-closing-r40-n3e-b1:out/20261119-230535/post/", "render-closing-r40-n3e-b1:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_003 (emitsb14d with only
the word changed), armed at `form=sb003`, sideband 0x003.

**Frozen verdict (as printed).**

```
SUMMARY: own: controls: every control passed
Q128-B1 RULE: B1-DONE: all ran (sideband 0x003 reads RUN; H-DM predicts RUN; H-ALL predicts NEVER)
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0 and B passed; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2, T 0x005a3305.
- SURVEY: sa0-sa31 identical before and after. pa0-pa15 of the started entry: pa0, pa4, pa8 and
  pa12 read 0x32004000 (V0), pa2, pa6, pa10 and pa14 0x32002000 (V2), the odd pa the words B0 read
  there (pa1 0x00043000, pa3 0x01555620, ...); the LANDING line 'pa0 = V0 yes, pa2 = V2 yes'.
- The owntask gate passed; post exact.

**What it shows.** Bits 6 and 11 are not needed to start the program when bits 1:0 are 3 **[HW]**. With this sideband the started entry reads crumb3's `douta` values
where 0x843's rows (D0, B0) read none: V0 (attribute 0) in every fourth pa from pa0 and V2
(attribute 2) in every fourth from pa2 **[HW]**; that these are crumb3's `douta` values and not
copies of sa0 and sa2 (which hold the same words) is **[infer]**.

**What it does not show.** Why the landing differs from 0x843's; what bits 6 and 11 do; one job
only.
