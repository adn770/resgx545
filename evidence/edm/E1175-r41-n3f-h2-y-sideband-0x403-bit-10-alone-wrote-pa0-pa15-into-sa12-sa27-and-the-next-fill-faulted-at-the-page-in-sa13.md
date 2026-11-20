+++
id = "E1175"
claim = "r41-n3f-h2 stage y (row Y, module 83FBFD86, fork 423b436e7f80, emitsb_sb403s, image crumb3 at fw14, form=sb403, sideband 0x403, s2 0, flagged, user present): row X's two jobs with bit 10 and bits 1:0 only (no bits 6 and 11): job 2's after-read equal to the started entry's post, sa12-sa27 equal to its pa0-pa15, sa1 0x04400000, sa3-sa10 changed, sa0 and sa2 unchanged; BIF_FAULT 0x0004300f (page 0x00043000 = post sa13) in snap9 and the gate's fill faulting at 0x4300f, the triangle after the recovery exact; 'Q128-N3F-Y RULE: Y-FILL, Y-REBASE; FAULT: BIF_FAULT is not 0 after the row and no outcome names it', every prediction held: bit 10 alone is enough"
unit = "edm"
method = "r41-n3f-h2 (render/closing-r41-n3f-h2), stage y of the question-closing pass (round 41: row Y, closing29/n3f/design.md section 3.3; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-20), dataset render-closing-r41-n3f-h2; attempt out/20261120-161558 (16:15:58; stage y ended at the gate, rc 16, its planned end, and the driver scored it, score-y.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row, the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 e516a7aa, branch r41-n3f, its fwtask_run.py byte for byte): our task owntask/emitsb_sb403s.blob (asm/fwtask/emitsb_sb403s.s, sha256 cb6af3a60fec1c6bd8a3b183533dd3207bb31fad6783b8e18831907ce3bd0318, asm/fwtask/fwtask.map at e516a7aa; emitsb14s with only the emit word changed, emit word 0xfb20b08000c08184, sideband 0x403) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb403` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (`\"kick\": \"miscinfo\"`); the results page, the registers (snap0, snap9) and, after an ok end, the gate (fill, then triangle) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 ea545cf5dcbf3573beaef7d3de2ee53bfaf14d3c6022d51c3ad2e033d271f1c6 (64 files), PREDICTIONS.sha256 3164f80875e492d371826c16833eed99783c50fa3dc67f8d4b6176f9f269c1ad (1 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at e516a7aa; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/y.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-y-20261120-161558.out, the same bytes as score-y.txt); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-20"
data = ["render-closing-r41-n3f-h2:out/20261120-161558/y/", "render-closing-r41-n3f-h2:fold/"]
terms = []
+++
**What ran.** Row X (E1174) with the sideband 0x403: bit 10 with bits 1:0 = 3, without bits 6 and 11
(0x003, which ran and passed the gate in E1164, plus bit 10).

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: y: controls: y1-a:B: FAILED
Q128-N3F-Y RULE: Y-FILL, Y-REBASE; FAULT: BIF_FAULT is not 0 after the row and no outcome names it
```

PG, E0, T0 and J1 passed; B is read by the outcomes, as in X. Every prediction held.

**Results [HW].**

- Job 1 done (run id 1, state 2, T 0x005a3305, 10 ticks); job 2 done on the kick (answered after 196
  us). Its after-read equals job 1's post in all 32: sa1 0x04400000; sa3 0x3f800000, sa4 0x32004000,
  sa5 0xbec00000, sa6 0x32002000, sa7 0x3f800000, sa8 0x32004000, sa9 0x3f400000, sa10 0x32002000,
  sa11 0; sa12-sa27 the started entry's pa0-pa15 word for word (sa13 = pa1 = 0x00043000); sa0 and
  sa2 unchanged.
- snap9: BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0004300f, before the gate. The gate's fill: `BIF fault
  0xd0400 at 0x4300f (PD 0x0) stalls job 125, recovering`, the devcoredump alike; the triangle after
  the recovery exact; health ok after the kit's reset
  (closing29/r41-n3f-logs/health-r41-n3f-h2.log).

**What it shows.** Bit 10 alone, without bits 6 and 11, gives X's rewrite of sa12-sa27 from pa0-pa15
and X's fault at the page in sa13 **[HW]**; 0x003 without bit 10 left the gate's fill exact (E1164).

**What it does not show.** Where sa1 and sa3-sa10 come from (they differ from X's); which access
faulted before the gate; one run.
