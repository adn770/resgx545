+++
id = "E1165"
claim = "r40-n3e-b2 stage own (row B2, module 83FBFD86, fork 423b436e7f80, emitsb_sb841, image crumb3 at fw14, form=sb841, sideband 0x841, s2 0, flagged, user present): B0's job with bit 1 of the sideband cleared: BIF_FAULT (0x0c08) read 0x30011010 in snap9 and in the runner's stop dump, X0, S1 and M4 kept the host's fill (0xdeadc0de), state 0, T running (0x01053cd1, 0x010607af): control B failed, 'Q128-B2 RULE: FAULT'; the runner stopped (class hang, rc 4) and the kit's reset and health recovered it (fill and triangle ok); 0x30011010 is the base of #14's page (0x30011000) + 0x10, 0xf0 below our image at 0x30011100"
unit = "edm"
method = "r40-n3e-b2 (render/closing-r40-n3e-b2), stage own of the question-closing pass (round 40: row B2, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b2; attempt out/20261119-230639 (23:06:39, stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sb841.blob (asm/fwtask/emitsb_sb841.s, sha256 9ea0e7a1c3bef0afa799685ad23261253338ae7c39ac2035c92ba92fdfdade18, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b10800408184, sideband 0x841) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb841` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9, the runner stop dump) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 010292be4d090e1b8c80d0265c55ef76f3a87d67ac1b7823f03941f78088fcd4 (49 files), PREDICTIONS.sha256 a07bbdceefaa4315d633a6dac641c48445a0bb0753016c8759787fad6807d616 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sb841.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-own*.out: the stage stopped, so the driver did not score it); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-b2:out/20261119-230639/own/", "render-closing-r40-n3e-b2:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_841, armed at
`form=sb841`, sideband 0x841.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out; the stage
stopped at its one row, rc 4):

```
SUMMARY: own: controls: c1-a:B: FAILED
Q128-B2 RULE: FAULT: BIF_FAULT is not 0 after the job: its own outcome (the kept files are the reading)
X0 qualifier: 0xdeadc0de (the fill: the issuer did not store past the emit)
```

**Results [HW].**

- Controls PG, E0 and T0 passed, B failed: BIF_FAULT (0x0c08) 0x30011010 in snap9 and in the
  runner's stop dump.
- X0, S1, M4 and the survey slots the host's fill (0xdeadc0de); state 0; T 0x01053cd1 and 0x010607af, counting.
- No done within 200 ms, class `hang`, stage rc 4; the kit's reset and health pair after the
  stop were ok (fill and triangle). Post not run.
- The arm line named the emit image 0x30011100; 0x30011010 is the base of #14's page
  (0x30011000) + 0x10, 0xf0 below our image.

**What it shows.** With bits 1:0 of the sideband 1 the job faults on the bus at #14's page +
0x10 and our task does not store past the emit **[HW]**.

**What it does not show.** What is read or written at 0x30011010, or by whom; whether the program
started; one job only.
