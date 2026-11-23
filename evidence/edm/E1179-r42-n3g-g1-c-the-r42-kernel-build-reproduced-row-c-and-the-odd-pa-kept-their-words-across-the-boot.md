+++
id = "E1179"
claim = "r42-n3g-g1 stage c (row C, the build control, module 079DD0D1, fork ec6511d5de87, emitsb14s, image crumb3 at fw14, form=fw14, sideband 0x843, s2 0, flagged, user present): E1173's two jobs on the new build, first after its boot: job 2's after-read equal to job 1's pre in all 32, the gate's fill and triangle exact, BIF_FAULT 0 before and after each job, every control passed, 'Q128-N3G-C RULE: C-GATE, C-SAME' as predicted; printed: job 1's post odd pa (pa1 0x00043000, pa3, ..., pa15) the words of the nine kept rows of rounds 40 and 41, 8 of 8, through the module change and the reboot"
unit = "edm"
method = "r42-n3g-g1 (render/closing-r42-n3g-g1), stage c of the question-closing pass (round 42: row C, closing29/n3g/design.md section 3.1; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-21), dataset render-closing-r42-n3g-g1; attempt out/20261122-160857 (16:08:57; stage c ended rc 0 and the driver scored it, score-c.txt; stage m followed; the session's first try, 20261122-154515, failed staging (ssh timed out) and ran nothing); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest, closing29/r42-n3g-logs/cachix-wait.log), the one-shot boot of 2026-11-22; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 c0e2dc36, branch r42-n3g, its fwtask_run.py byte for byte): our task owntask/emitsb14s.blob (asm/fwtask/emitsb14s.s, sha256 c3f9ce90c2ea24208d6b8bcafef3a1f77e105c03bc8c51b4bee5fbcd04e7fb39, asm/fwtask/fwtask.map at c0e2dc36; emitsb14d with a cmd 6 branch in entry 0 that stores sa0-sa31 into dwords 224-255, writes M6 and the run id into slot 6 and emits nothing; entry 1 and cmd 1's path as emitsb14d's, emit word 0xfb20b10800c08184, sideband 0x843) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (kick miscinfo); the results page, the registers (snap0, snap9), the record and the gate (fill, then triangle) kept; the round's blobs and arm lines accepted by the module's verifier unchanged: the fork's KUnit suite at ec6511d5de87 on the Mac shim with a suite of their own, 48 of 48 (closing29/r42-n3g-logs/shim-r42.log; r42-red 46 of 48, shim-r42-red.log; a wrong form fails, shim-r42-neg.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 06cfa6bc6691dcd1890da3c1d91d91f520fc50a7656986a242031b90e734d47a (86 files), PREDICTIONS.sha256 20b5b99ba57b65eaef7b682917008a60525a393aae9bc9ca92f80c1869b0cd3f (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at c0e2dc36; r35-sa's and round 41's kept files at data 5e9c84b2; t30's source 42c4de7); the frozen predictions predictions/c.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-c-20261122-160857.out, the same bytes as score-c.txt); the SURVEY, JOB, BIF, GATE and RBOOT lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-22"
data = ["render-closing-r42-n3g-g1:out/20261122-160857/c/", "render-closing-r42-n3g-g1:fold/"]
terms = []
+++
**What ran.** Row C of E1173 byte for byte (emitsb14s, crumb3 at fw14, sideband 0x843; job 1 the
emit, job 2 command 6 on a GETMISCINFO kick, then the gate's fill and triangle), as the first stage
after the one-shot boot of the r42-kernel module: the build control of round 42. Printed with it,
R-BOOT: job 1's post pa0-pa15 against the words the nine kept rows of rounds 40 and 41 read (design
section 0.1).

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: c: controls: every control passed
Q128-N3G-C RULE: C-GATE, C-SAME
```

**Results [HW].**

- Controls PG, E0, T0, B, J1 and J2 passed. Job 1: X0 0x5a5a3303, S1 and M4 with run id 1, state 2,
  T 0x005a3305, 9 ticks.
- Job 2 done on the kick (GETMISCINFO answered after 200 us), slot 6 0x5a5a3306 and run id 2; its
  after-read of sa0-sa31 equal to job 1's pre in all 32 (sa0 0x32004000, sa1 0x32005000, sa2
  0x32002000, sa22 0x32000000, sa23 0x05366000, the rest 0); job 1's post equal to the pre too.
- K5: BIF_INT_STAT 0x00080000 and BIF_FAULT 0 before and after each job. The gate: fill exact,
  triangle exact, no devcoredump.

**Readings [HW], printed, not scored (R-BOOT).** Job 1's post odd pa: pa1 0x00043000, pa3
0x01555620, pa5 0, pa7 0x03c3cdac, pa9 0xdc531a54, pa11 0x5d50716f, pa13 0x82e151b5, pa15
0x11b5d77a, the words of all nine kept rows from 2026-11-19 to 2026-11-21, 8 of 8. Even pa: pa0 3,
pa2 0x32002000, pa4 0x32411000, pa6 0x32002000, pa8 0x32004000, pa10 0x32002000, pa12 0x5a5a3a18 and
pa14 0x5a5a3a1a (land's markers, written in round 41, E1176, E1178).

**What it shows.** The new build, booted once, reproduces E1173: with #14's sideband the EDM's own
sa0-sa31 stay as they were and the next fill and triangle run **[HW]**, so the round's other rows
read the new image and form words, not a changed build. The words the started entry reads in its pa,
odd and even, came through the module change and the laptop's reboot as they were **[HW]**.

**What it does not show.** Who wrote the odd pa words first (0x00043000 in pa1 included); whether a
cold power-off clears them (the boot was a reboot); the sa past sa31.
