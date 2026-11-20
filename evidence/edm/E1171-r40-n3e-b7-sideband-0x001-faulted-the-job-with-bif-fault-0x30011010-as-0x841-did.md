+++
id = "E1171"
claim = "r40-n3e-b7 stage own (row B7, module 83FBFD86, fork 423b436e7f80, emitsb_sb001, image crumb3 at fw14, form=sb001, sideband 0x001, s2 0, flagged, user present): B0's job with only bit 0 of the sideband set: BIF_FAULT 0x30011010 in snap9 and in the stop dump, as B2's (E1165), X0, S1 and M4 the host's fill, state 0, T running (0x0100c33d, 0x0105481f): control B failed, 'Q128-B7 RULE: FAULT'; the runner stopped (class hang, rc 4) and the kit's reset and health recovered it; with E1158 and E1162-E1172, bits 1:0 of the sideband decide the start from our task: 0 never starts, 1 faults at #14's page + 0x10, 2 or 3 runs"
unit = "edm"
method = "r40-n3e-b7 (render/closing-r40-n3e-b7), stage own of the question-closing pass (round 40: row B7, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b7; attempt out/20261120-073957 (07:39:57, stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sb001.blob (asm/fwtask/emitsb_sb001.s, sha256 d888f0f64c2a3d9eb7dc4140512863dc196dff396f52101d0e17892f7dcc1cb9, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b00000408184, sideband 0x001) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb001` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9, the runner stop dump) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 d914b7c04ab1d0fab17cb375cfab99e4262b840cc102e1b527e340bee71feb74 (49 files), PREDICTIONS.sha256 d49f4a6d3c20bc2e818582bfe6dc2014ef16d0352f03ec309a22165177509cb3 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sb001.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-own*.out: the stage stopped, so the driver did not score it); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-20"
data = ["render-closing-r40-n3e-b7:out/20261120-073957/own/", "render-closing-r40-n3e-b7:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_001, armed at
`form=sb001`, sideband 0x001.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out; the stage
stopped at its one row, rc 4):

```
SUMMARY: own: controls: c1-a:B: FAILED
Q128-B7 RULE: FAULT: BIF_FAULT is not 0 after the job: its own outcome (the kept files are the reading)
X0 qualifier: 0xdeadc0de (the fill: the issuer did not store past the emit)
```

**Results [HW].**

- Controls PG, E0 and T0 passed, B failed: BIF_FAULT (0x0c08) 0x30011010 in snap9 and in the
  runner's stop dump.
- X0, S1, M4 and the survey slots the host's fill (0xdeadc0de); state 0; T 0x0100c33d and 0x0105481f, counting.
- No done within 200 ms, class `hang`, stage rc 4; the kit's reset and health pair after the
  stop were ok (fill and triangle) (closing29/r40-n3e-logs/health-after-b7.log). Post not run.
- The arm line named the emit image 0x30011100; 0x30011010 is the base of #14's page
  (0x30011000) + 0x10, 0xf0 below our image.

**What it shows.** With bits 1:0 of the sideband 1 the job faults on the bus at #14's page +
0x10 and our task does not store past the emit **[HW]**. Over the eleven sidebands run from our task (E1158 and
E1162-E1172: 0x000, 0x001, 0x002, 0x003, 0x040, 0x800, 0x840, 0x841, 0x842, 0x843, 0xc43), bits
1:0 decide the start: 0 never starts it (0x000, 0x040, 0x800, 0x840), 1 faults at #14's page +
0x10 (0x001, 0x841), 2 or 3 run it to done (0x002, 0x842, 0x003, 0x843, 0xc43); bits 6, 10 and 11
are not needed, bits 6 and 11 neither with 2 (0x002, 0x842) nor with 3 (0x003, 0x843) **[HW]**.
That this holds for the combinations not run (0x042, 0x043, 0x802, 0x803, bits 12-13) is
**[infer]**. H-DM (3 = the event data master, needed) fails on 0x002 and 0x842.

**What it does not show.** What is read or written at 0x30011010, or by whom; whether the program
started; one job only.
