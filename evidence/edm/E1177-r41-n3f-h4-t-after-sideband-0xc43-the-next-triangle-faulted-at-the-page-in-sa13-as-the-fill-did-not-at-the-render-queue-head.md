+++
id = "E1177"
claim = "r41-n3f-h4 stage t (row T, module 83FBFD86, fork 423b436e7f80, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): B11's one job, then the gate triangle first: every control passed (BIF_FAULT 0 in snap9), the triangle faulted with BIF_FAULT 0x0004300f (list 15, page 0x00043000, the post sa13, the fills' page), not at the render queue's head 0x01555000; the fill after the recovery exact; 'Q128-N3F-T RULE: T-OTHER', the prediction T-HEAD failed"
unit = "edm"
method = "r41-n3f-h4 (render/closing-r41-n3f-h4), stage t of the question-closing pass (round 41: row T, closing29/n3f/design.md section 3.5; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-20), dataset render-closing-r41-n3f-h4; attempt out/20261120-161718 (16:17:18; stage t ended at the gate, rc 16, its planned end, and the driver scored it, score-t.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row, the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 e516a7aa, branch r41-n3f, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at e516a7aa; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of one job, command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223); the results page, the registers (snap0, snap9) and the gate in the order triangle, then fill (`gate_order = \"tri,fill\"`) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 bbe74aa0ca7024f2e622bf2a850b3b36ff408f3e077b825893587bfe847ed488 (64 files), PREDICTIONS.sha256 bbe85123c2578b2004c61061345e623c2f28a382aa36850dfb352ce1a594b52a (1 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at e516a7aa; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/t.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-t-20261120-161718.out, the same bytes as score-t.txt); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-20"
data = ["render-closing-r41-n3f-h4:out/20261120-161718/t/", "render-closing-r41-n3f-h4:fold/"]
terms = []
+++
**What ran.** B11's job (E1172: emitsb_sbc43s's command 1, sideband 0xc43, crumb3), one job, and the
gate with the triangle first, so the first job after the emit is a render (a TA and 3D kick) rather
than a transfer.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: t: controls: every control passed
Q128-N3F-T RULE: T-OTHER
```

The design's prediction T-HEAD (the triangle faults at page 0x01555000, the render queue's head
sa15) failed; T-OTHER (a fault at another page) held; T-HANG and T-OK failed.

**Results [HW].**

- Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); snap9 BIF_FAULT 0.
- The gate's triangle: `BIF fault 0xd0400 at 0x4300f (PD 0x0) stalls job 139, recovering`, the
  devcoredump alike: list 15, page 0x00043000, the post sa13, the page of the fills after bit 10
  (E1172, E1174, E1175). The fill after the watchdog's recovery reset was exact (`diff: 0 of 2048
  pixels`); health ok after the kit's reset (closing29/r41-n3f-logs/health-r41-n3f-h4.log).
- Post sa as E1175's (sa1 0x04400000, sa3-sa10, sa12-sa27 = pa0-pa15, sa13 0x00043000), pa12 and
  pa14 holding land's markers from H3's row LC, run before this session.

**What it shows.** After bit 10 the next render faults at the same page as the next transfer, the
page in sa13, not at the render queue's head **[HW]**. Why a render reaches sa13 is **[infer]**:
whatever reads sa13 as a page is on both paths.

**What it does not show.** Which access of the render faulted; whether a second render without a
reset would fault again (the recovery reset came first); one run.
