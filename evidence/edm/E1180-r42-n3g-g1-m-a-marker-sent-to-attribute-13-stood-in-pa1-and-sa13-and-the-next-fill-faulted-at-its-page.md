+++
id = "E1180"
claim = "r42-n3g-g1 stage m (row M, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image mark at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): crumb3 with two douta more, M13 0x005d3000 to attribute 13 and M1 0x005d1000 to attribute 1, then X's two jobs (E1174): job 1's post pa1 = M13, job 2's after-read equal to job 1's post in all 32 with sa13 = M13 and sa1 = M1; K5: BIF_FAULT 0 after job 1, 0x005d300f (list 15, page 0x005d3000) after job 2; the gate's fill faulting at 0x5d300f, the triangle after the recovery exact; 'Q128-N3G-M RULE: M-FILL, M-PA, M-REBASE, M-SA1, M-SA13; FAULT: BIF_FAULT is not 0 after the row and no outcome names it', every prediction held: the fault page follows the word in attribute 13"
unit = "edm"
method = "r42-n3g-g1 (render/closing-r42-n3g-g1), stage m of the question-closing pass (round 42: row M, closing29/n3g/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-21), dataset render-closing-r42-n3g-g1; attempt out/20261122-160857 (16:09:47; stage m ended at the gate, rc 16, its planned end (on_gate_fail = score), and the driver scored it, score-m.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest, closing29/r42-n3g-logs/cachix-wait.log), the one-shot boot of 2026-11-22; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 c0e2dc36, branch r42-n3g, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at c0e2dc36; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=mark pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (kick miscinfo); the results page, the registers (snap0, snap9), the record and the gate (fill, then triangle) kept; the round's blobs and arm lines accepted by the module's verifier unchanged: the fork's KUnit suite at ec6511d5de87 on the Mac shim with a suite of their own, 48 of 48 (closing29/r42-n3g-logs/shim-r42.log; r42-red 46 of 48, shim-r42-red.log; a wrong form fails, shim-r42-neg.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 06cfa6bc6691dcd1890da3c1d91d91f520fc50a7656986a242031b90e734d47a (86 files), PREDICTIONS.sha256 20b5b99ba57b65eaef7b682917008a60525a393aae9bc9ca92f80c1869b0cd3f (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at c0e2dc36; r35-sa's and round 41's kept files at data 5e9c84b2; t30's source 42c4de7); the frozen predictions predictions/m.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-m-20261122-160857.out, the same bytes as score-m.txt); the SURVEY, JOB, BIF, GATE and RBOOT lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-22"
data = ["render-closing-r42-n3g-g1:out/20261122-160857/m/", "render-closing-r42-n3g-g1:fold/"]
terms = []
+++
**What ran.** Row X's two jobs and gate (E1174: emitsb_sbc43s, sideband 0xc43, job 2 command 6 on a
GETMISCINFO kick, the fill first) with a new image, mark: crumb3 plus two `douta` from its unused
third row, M13 0x005d3000 to attribute 13 and M1 0x005d1000 to attribute 1, pages below every heap
and in no kept page (design section 2). The question: is the page the fill faults at (0x00043000 in
rounds 40 and 41) the word in attribute 13, and does sa1 read attribute 1 (H-BLOCK) or not (H-COPY)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: m: controls: m1-a:B: FAILED
Q128-N3G-M RULE: M-FILL, M-PA, M-REBASE, M-SA1, M-SA13; FAULT: BIF_FAULT is not 0 after the row and no outcome names it
```

Control B (BIF_FAULT 0 in snap9) is read by the outcomes that name a fault (the frozen rule, as in
X); PG, E0, T0, J1 and J2 passed. Every prediction held: M-PA, M-SA13, M-SA1, M-REBASE and M-FILL
held; M-FILL43, M-FILLM1, M-FILLOK and M-NOKICK failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, state 2, T 0x005a3305, 9 ticks. Its post pa1 = M13
  0x005d3000; the other fifteen post pa as stage c's (E1179).
- Job 2 done on the kick (GETMISCINFO answered after 288 us), slot 6 0x5a5a3306, run id 2; its
  after-read equals job 1's post in all 32: sa1 = M1 0x005d1000, sa13 = pa1 = M13, sa12-sa27 =
  pa0-pa15, sa0 0x32004000 and sa2 0x32002000 kept, sa3-sa10 0x3f800000, 0x32004000, 0xbec00000,
  0x32002000, 0x3f800000, 0x32004000, 0x3f400000, 0x32002000.
- K5: job 1 BIF_FAULT 0 before and after; job 2 BIF_FAULT 0 before and BIF_INT_STAT 0x000d0400,
  BIF_FAULT 0x005d300f after. snap9 the same.
- The gate: the fill's kernel line `BIF fault 0xd0400 at 0x5d300f (PD 0x0) stalls job 11,
  recovering`, every pixel 0xdeadbeef; devcd2 (detector manual) there before the gate, devcd3
  (detector bif-fault, BIF_FAULT 0x005d300f) new during the fill; the triangle after the watchdog's
  recovery reset exact; fill and triangle ok after the kit's reset
  (closing29/r42-n3g-logs/health-r42-n3g-g1.log).

**What it shows.** A word a program our task emitted with 0xc43 sent to attribute 13 stood in the
started entry's pa1 (attribute 13 at pa 13 - 12, as attributes 24 and 26 at pa12 and pa14 with
0x843, E1163), the issuer's sa13 took it, and the EDM's list faulted at its page **[HW]**: the fault
page is the word in attribute 13. With E1179 and E1181 this says that 0x00043000, the page of E1172
and E1174-E1178, was a stale word in attribute 13 that none of our rows wrote **[HW]**. The fault
arose in job 2, by the end of the kick and command 6 served on the rewritten bank, not on job 1's
pass **[HW]**. sa1 took M1, the word sent to attribute 1 **[HW]**, as H-BLOCK (bit 10 makes the
issuer's sa n read attribute n of one block) predicts and H-COPY does not; row Q (E1182) then read
sa1 0x04400000 with no write to attribute 1, so H-BLOCK is supported only weakly and stays
**[infer]** (either attribute 1 was rewritten between the rows, or sa1 is not attribute 1 in every
case).

**What it does not show.** Which access of job 2 (the kick, command 6 or a stock pass between) read
attribute 13's page; that the gate's fill faulted afresh: BIF_FAULT already held 0x005d300f from job
2 when the fill was sent, so although devcd3 appeared during the fill, the fill's fault reading
alone cannot tell a fresh fault from the latched one; where sa3-sa10 come from; whether sa1 is
attribute 1; that the hardware or the firmware takes sa13 as a page base (**[infer]**, as in E1174);
the sa past sa31; one run.
