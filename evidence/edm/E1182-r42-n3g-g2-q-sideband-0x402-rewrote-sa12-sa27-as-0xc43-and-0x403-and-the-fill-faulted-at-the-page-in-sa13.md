+++
id = "E1182"
claim = "r42-n3g-g2 stage q (row Q, module 079DD0D1, fork ec6511d5de87, emitsb_sb402s, image crumb3 at fw14, form=sb402, sideband 0x402, s2 0, flagged, user present): bit 10 with bits 1:0 = 2: job 1's post pa0, pa4, pa8, pa12 = V0 and pa2, pa6, pa10, pa14 = V2, pa1 = M13 0x005d3000; job 2's after-read equal to job 1's post in all 32, sa12-sa27 = pa0-pa15, sa13 = M13, sa1 0x04400000 (not row M's M1); K5: BIF_FAULT 0 after job 1, 0x005d300f after job 2; the gate's fill faulting at 0x5d300f, the triangle after the recovery exact; 'Q128-N3G-Q RULE: Q-FILL, Q-REBASE, Q-REP; FAULT: BIF_FAULT is not 0 after the row and no outcome names it', every prediction held: sb402 behaves as 0xc43 and 0x403"
unit = "edm"
method = "r42-n3g-g2 (render/closing-r42-n3g-g2), stage q of the question-closing pass (round 42: row Q, closing29/n3g/design.md section 3.4; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-21), dataset render-closing-r42-n3g-g2; attempt out/20261122-163902 (16:39:27; stage q ended at the gate, rc 16, its planned end, and the driver scored it, score-q.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest, closing29/r42-n3g-logs/cachix-wait.log), the one-shot boot of 2026-11-22; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 c0e2dc36, branch r42-n3g, its fwtask_run.py byte for byte): our task owntask/emitsb_sb402s.blob (asm/fwtask/emitsb_sb402s.s, sha256 3b66cfda6ea082c61da7478f5f67fafd0ec990695b4b1d6084c7215036539ba7, asm/fwtask/fwtask.map at c0e2dc36; emitsb14s with only the emit word changed, emit word 0xfb20b08000808184, sideband 0x402) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb402` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (kick miscinfo); the results page, the registers (snap0, snap9), the record and the gate (fill, then triangle) kept; the round's blobs and arm lines accepted by the module's verifier unchanged: the fork's KUnit suite at ec6511d5de87 on the Mac shim with a suite of their own, 48 of 48 (closing29/r42-n3g-logs/shim-r42.log; r42-red 46 of 48, shim-r42-red.log; a wrong form fails, shim-r42-neg.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 2a31df2e5945735a83363ea52855e6a0dc6f08bd50345a69e6380a7cf8354e61 (86 files), PREDICTIONS.sha256 effaec4333424aa9eb28ec078d230dfa502ae4354af3aa17246bf4d2b92933cb (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at c0e2dc36; r35-sa's and round 41's kept files at data 5e9c84b2; t30's source 42c4de7); the frozen predictions predictions/q.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-q-20261122-163902.out, the same bytes as score-q.txt); the SURVEY, JOB, BIF, GATE and RBOOT lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-22"
data = ["render-closing-r42-n3g-g2:out/20261122-163902/q/", "render-closing-r42-n3g-g2:fold/"]
terms = []
+++
**What ran.** Row Y's two jobs and gate (E1175) with the sideband 0x402: bit 10 with bits 1:0 = 2
(0x002, which ran and passed the gate in E1168, plus bit 10), a word never run before. Run after
rows M and S, so attribute 13 held M13 (E1181).

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: q: controls: q1-a:B: FAILED
Q128-N3G-Q RULE: Q-FILL, Q-REBASE, Q-REP; FAULT: BIF_FAULT is not 0 after the row and no outcome names it
```

PG, E0, T0, J1 and J2 passed; B is read by the outcomes, as in X, Y and M. Every prediction held:
Q-REBASE, Q-REP and Q-FILL held, Q-NONE failed, Q-OTHER (printed) failed.

**Results [HW].**

- Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks). Its post pa: pa0, pa4, pa8, pa12 = V0
  0x32004000, pa2, pa6, pa10, pa14 = V2 0x32002000 (row S's post held 3, 0x32411000, 0x5a5a3a18 and
  0x5a5a3a1a at pa0, pa4, pa12 and pa14), pa1 = M13, the other odd pa as in E1179.
- Job 2 done on the kick (answered after 202 us), run id 2; its after-read equals job 1's post in
  all 32: sa12-sa27 = pa0-pa15 (sa12 V0, sa13 M13, sa14 V2), sa4 = sa8 = V0 and sa6 = sa10 = V2 (as
  M's and LV's), sa3, sa5, sa7, sa9 the float words of M, sa1 0x04400000, sa0 and sa2 kept.
- K5: job 1 BIF_FAULT 0 before and after; job 2 0 before, BIF_INT_STAT 0x000d0400 and BIF_FAULT
  0x005d300f after. The gate: `BIF fault 0xd0400 at 0x5d300f (PD 0x0) stalls job 25, recovering`;
  devcd6 (manual) before, devcd7 (bif-fault, 0x005d300f) during the fill; the triangle after the
  recovery exact; health ok after the session.

**What it shows.** Bit 10 with bits 1:0 = 2 does what it does with 3 (0xc43, 0x403): the issuer's
sa12-sa27 take the started entry's pa0-pa15 and the next fill faults through the EDM's list at the
page in sa13, here M13, the word in attribute 13 **[HW]**; bits 1:0 decide the start and bit 10 the
rewrite, with no interaction seen. crumb3's V0 and V2 stood in every fourth pa from pa0 and pa2, as
with 0x002 (E1168) **[HW]**. As in M (E1180), the fault arose in job 2 **[HW]**. sa1 read
0x04400000, the word of B11, Y and LC2, not M1: either attribute 1 was rewritten between rows M and
Q, or sa1 is not attribute 1 in every case; so row M's M-SA1 supports H-BLOCK only weakly, and
H-BLOCK stays **[infer]**, with this counter-reading.

**What it does not show.** Which of the two readings of sa1 holds; where sa3-sa10 come from; which
access of job 2 faulted; that the fill faulted afresh (BIF_FAULT was latched from job 2, as in M);
one run.

**Correction 2026-11-23:** Round 43 read who writes attribute 1. Rows W and W2 (E1184, E1186) sent
M1 to attribute 1 with 0xc43 and read it in sa1 in the same row; row V (E1185) read it kept in sa1
across a stage boundary of resets, a boot, kicks and ticks with no client draw; row F (E1187), the
same boundary with one stock fill, read sa1 0x01000000 **[HW]**. So attribute 1 is rewritten by a
client draw and by nothing else seen, and sa1 reads attribute 1 in every row that planted it (M, W,
W2, V) **[HW]**. This record's sa1 0x04400000, read with no write to attribute 1, came after row M's
end draws, the next session's begin draws and row S's gate and draws: that one of those draws left
0x04400000 there is **[infer]** (one fill alone left 0x01000000). The counter-reading to H-BLOCK
then needs no other cause; H-BLOCK holds at attributes 1 and 13 **[HW]**. This record's verdict and
readings stand.
