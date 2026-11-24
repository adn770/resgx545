+++
id = "E1176"
claim = "r41-n3f-h3 stage lc (row LC, module 83FBFD86, fork 423b436e7f80, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): job 1 done, then BIF_FAULT 0x0000000f (list 15, page 0) in snap9, the tick stopped and job 2 (command 6) was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3F-LC RULE: CANNOT TELL (control E0 FAILED)', E0 failing by a design slip of the scorer (it reads the cmd word at the row's end, 6 for the unserved job 2); the readings, printed only, are LC-EARLY-like: post sa0 0, sa2 0x0104b95b, sa12-sa27 = pa0-pa15"
unit = "edm"
method = "r41-n3f-h3 (render/closing-r41-n3f-h3), stage lc of the question-closing pass (round 41: row LC, closing29/n3f/design.md section 3.4; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-20), dataset render-closing-r41-n3f-h3; attempt out/20261120-161633 (16:16:33; stage lc exited 4 at its one row, a runner stop, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row, the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 e516a7aa, branch r41-n3f, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at e516a7aa; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of three jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on the next tick pass, and command 6 again after `sleep_ms` 2000; the results page, the registers (snap0, snap9, the runner stop dump) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 f2ada3ff161870b95457009e0ad97aefd14df2aa30d54636f1f4211957283279 (64 files), PREDICTIONS.sha256 eab206c4bb06c2cdaf4108fc30e1b80e504a8eb132a233f44bc24b9f7800702c (1 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at e516a7aa; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/lc.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-lc-20261120-161633.out); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-20"
data = ["render-closing-r41-n3f-h3:out/20261120-161633/lc/", "render-closing-r41-n3f-h3:fold/"]
terms = []
+++
**What ran.** Sideband 0xc43 with the land image (E1163's image: `douta` of markers to attributes 24
and 26, the timer left running, no V0 or V2), three jobs: the emit (command 1), the after-read
(command 6) on the next tick pass and again 2 s later, then the gate. The question: does bit 10's
state heal on later stock passes, and is the timer stop of crumb3 needed for the fill to fail.

**Frozen verdict (as printed).** The stage stopped, so the frozen scorer was run by hand on the kept
directory:

```
SUMMARY: lc: controls: lc1-a:E0: FAILED; lc1-a:B: FAILED
Q128-N3F-LC RULE: CANNOT TELL (control E0 FAILED)
```

**A design slip, named, not rescored.** E0 wants the page's cmd word (dword 1) 0 at the row's end,
as a row of one job leaves it. In a row of several jobs it holds the last command the host wrote:
job 2's command 6 was written and never served, since the firmware had stopped, so dword 1 read 6.
E0 fails whenever a later job of a row is not served, which is the LC-EARLY end the design
predicted; it does not say that entry 0 did not run job 1 (J1 passed). The frozen rule and its
CANNOT TELL stand.

**Readings [HW], printed, not scored.**

- Job 1 done: X0 0x5a5a3303, S1 and M4 with run id 1, 9 ticks.
- Post (the started entry's) sa: sa0 0x32004000 -> 0x00000000, sa1 0x04400000, sa2 0x32002000 ->
  0x0104b95b, sa3-sa10 as E1175's, sa12-sa27 the started entry's pa0-pa15 (sa13 0x00043000; pa12 and
  pa14 land's markers 0x5a5a3a18 and 0x5a5a3a1a).
- snap9 and the stop dump: BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0); the tick
  stopped (the runner's alive check: the tick count 2129 three times, not advancing); job 2 not done
  (dwords 224-255 still 0xdeadc0de); no gate ran. The kit's reset and health recovered it
  (closing29/r41-n3f-logs/health-r41-n3f-h3.log).

**What it shows.** Nothing frozen: CANNOT TELL. The readings fit LC-EARLY, the design's prediction
(a): with land, which writes no V0 or V2, sa0 and sa2 lost TA3DCtl and the kernel CCB control and
the EDM stopped after the next pass with a fault at page 0 through its list **[infer]**; that a
stale sa0 or sa2 was the faulting pointer is not read.

**What it does not show.** Whether the rewrite heals on later stock passes (no after-read ran);
whether the fill fails with the timer running; why sa0 became 0 and sa2 0x0104b95b.

**Correction 2026-11-21:** Row LC now has a scored outcome: its rerun r41-n3f-lc2 (E1178), the same
blob, image, arm, jobs and predictions with control E0 read in job 1's record, read 'Q128-N3F-LC
RULE: LC-EARLY', the prediction held (PG, E0, T0 and J1 passed; B read by LC-EARLY): job 1 done,
then BIF_FAULT 0x0000000f, the tick stopped and job 2 was never served, as here [HW]. This record's
kept stage rescored with that scorer reads E0 PASS and LC-EARLY too, for information only
(closing29/r41-lc2-logs/rescore-h3-under-lc2.txt). This record's frozen verdict, CANNOT TELL, and
its readings stand; the rerun read post sa2 0x01030b00 where this one read 0x0104b95b.

**Correction 2026-11-23:** Row LV of round 42 (E1183) ran this row with V0 and V2 sent to attributes
0 and 2 (the landv image): the started entry's sa0 and sa2 read V0 and V2, and the EDM still stopped
after job 1, BIF_FAULT 0x0440000f, at page 0x04400000, the post sa1 **[HW]**. This record's
inference that sa0 and sa2 losing TA3DCtl and the CCB control word led to the stop is weakened:
restoring them does not prevent it. That the early stop follows a pointer through the first
secondaries (page 0 with sa0 0 here and in E1178, sa1's word with sa0 valid in LV) is **[infer]**.
The 0x00043000 in this record's sa13 was a stale word of attribute 13 (E1180, E1181). This record's
frozen verdict, CANNOT TELL, and its readings stand.

**Correction 2026-11-23:** Row V of round 43 (E1185), landv with M1 planted in attribute 1, stopped
early at the page in sa1 (0x005d1000), as LV at its sa1 0x04400000 **[HW]**: with sa0 valid the
early stop follows sa1. This record's page 0, and LC2's with sa1 0x04400000 (E1178), are not
explained by that; the reading of a stop through sa0 = 0 in this record's earlier correction stays
**[infer]**, not supported by a row. This record's frozen verdict, CANNOT TELL, and its readings
stand.

**Correction 2026-11-24:** Round 44 ran land itself on the bank V had: row LM (E1198), W's plant and
no draws, read post sa0 = V0, sa1 = M1, sa2 = V2 and stopped at the page in sa1 (M1); row LF
(E1200), W's plant and one fill, read post sa0 0x00000002, sa1 = M1, sa2 0x01049b60 and stopped at
page 0 **[HW]**. So land's image does not cause a page-0 stop (H-IMG fails), and the stop faults at
page 0 when sa0 holds a word below one page and at sa1's page when sa0 is V0 **[HW, rows LM and
LF]**. This record's page 0 with post sa0 0 fits that: a stop through sa0, then sa1, is **[infer]**,
now supported by two rows of round 44. This record's frozen verdict, CANNOT TELL, and its readings
stand.
