+++
id = "E1174"
claim = "r41-n3f-h1 stage x (row X, module 83FBFD86, fork 423b436e7f80, emitsb_sbc43s, image crumb3 at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): row C's two jobs with bit 10 of the sideband set: job 2's after-read of the EDM's own sa0-sa31 equal to the started entry's post in all 32: sa12-sa27 equal to the started entry's pa0-pa15, sa1 0x04000010, sa3-sa5 and sa7-sa9 float words, sa0 and sa2 unchanged; BIF_FAULT 0x0004300f (list 15, page 0x00043000, the post sa13) in snap9 before the gate and the gate's fill faulting at 0x4300f, the triangle after the recovery exact; 'Q128-N3F-X RULE: X-FILL, X-REBASE; FAULT: BIF_FAULT is not 0 after the row and no outcome names it', every prediction held; that the fault page is sa13 because the hardware takes it as a page base is inferred"
unit = "edm"
method = "r41-n3f-h1 (render/closing-r41-n3f-h1), stage x of the question-closing pass (round 41: row X, closing29/n3f/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-20), dataset render-closing-r41-n3f-h1; attempt out/20261120-161456 (16:15:22; stage x ended at the gate, rc 16, its planned end (on_gate_fail = \"score\"), and the driver scored it, score-x.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row, the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 e516a7aa, branch r41-n3f, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at e516a7aa; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (`\"kick\": \"miscinfo\"`); the results page, the registers (snap0, snap9) and, after an ok end, the gate (fill, then triangle) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 9c0f4ecbbb1dbdcab0055423075007ac7d02cee61b719208888683ff57f1b7de (69 files), PREDICTIONS.sha256 f9dd397b8522828a3e5a5d41f2a661f9d30c786ac953c4df9018a5bf79563f9a (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at e516a7aa; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/x.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-x-20261120-161456.out, the same bytes as score-x.txt); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-20"
data = ["render-closing-r41-n3f-h1:out/20261120-161456/x/", "render-closing-r41-n3f-h1:fold/"]
terms = []
+++
**What ran.** Row C's two jobs (E1173) with one change, the emit word: blob emitsb_sbc43s, armed at
`form=sbc43`, sideband 0xc43 (bit 10 with 0x843's bits, B11's word, E1172). Job 2's after-read is
entry 0 of our own task reading the EDM's secondaries itself, after the emit.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: x: controls: x1-a:B: FAILED
Q128-N3F-X RULE: X-FILL, X-REBASE; FAULT: BIF_FAULT is not 0 after the row and no outcome names it
```

Control B (BIF_FAULT 0 in snap9) is read by the outcomes that name a fault (the frozen rule); PG,
E0, T0 and J1 passed. Every prediction held: X-REBASE and X-FILL held, X-HIGH, X-NONE, X-OTHER,
X-KICKFAULT and X-NOKICK failed.

**Results [HW].**

- Job 1 as B11's: X0 0x5a5a3303, S1 and M4 with run id 1, state 2, T 0x005a3305, 8 ticks.
- Job 2 done on the kick (GETMISCINFO answered after 139 us), slot 6 0x5a5a3306, run id 2. Its
  after-read of sa0-sa31 equals job 1's post (the started entry's sa) in all 32 and differs from the
  pre at sa1 (0x32005000 -> 0x04000010), sa3-sa5 and sa7-sa9 (0x3f800000, 0x3f400000, 0xbec00000,
  0x3f800000, 0xbec00000, 0x3f400000) and sa12-sa31 but sa17 (0 before and after); sa0 0x32004000
  and sa2 0x32002000 unchanged.
- sa12-sa27 read the started entry's pa0-pa15 word for word (sa12 0x00000003, sa13 0x00043000, sa14
  0x32411000, sa15 0x01555620, ..., sa27 0x11b5d77a); sa28-sa31 go on in that pattern.
- snap9 (after the row, before the gate): BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0004300f, list 15,
  page 0x00043000 = post sa13.
- The gate: the fill's kernel line `BIF fault 0xd0400 at 0x4300f (PD 0x0) stalls job 117,
  recovering`, the devcoredump's BIF words alike; the triangle after the watchdog's recovery reset
  exact; fill and triangle ok after the kit's reset (closing29/r41-n3f-logs/health-r41-n3f-h1.log).

**What it shows.** Bit 10 of the emit's sideband rewrites the EDM's own secondaries, the bank entry
0 reads: sa12-sa27 take the started entry's pa0-pa15, and sa1 and words of sa3-sa10 change too
**[HW]**. The rewritten bank stays: job 2's kick and command 6 were served and read it. Afterwards
the EDM's list faults at the page sa13 holds (0x43000), here already by the end of the row and then
with the gate's fill, until a reset **[HW]**. That the fault page is sa13 because the hardware or
the firmware takes sa13 as a page base (the firmware's transfer queue head, design section 0.3) is
**[infer]**.

**What it does not show.** Where sa1 and sa3-sa10 come from (B11 read sa1 0x04400000, this row
0x04000010); which access faulted before the gate (after job 1, by the end of job 2's kick and
command 6; B11, one job and no kick, read BIF_FAULT 0 there); the sa past sa31; what bit 10 means.
