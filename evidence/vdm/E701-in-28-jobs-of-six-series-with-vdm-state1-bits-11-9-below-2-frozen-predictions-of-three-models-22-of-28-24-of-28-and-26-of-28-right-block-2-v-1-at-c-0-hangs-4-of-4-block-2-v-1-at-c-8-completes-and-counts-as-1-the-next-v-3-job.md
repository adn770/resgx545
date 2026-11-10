+++
id = "E701"
claim = "In 28 jobs of six series with VDM_STATE1 bits 11:9 below 2 (frozen predictions of three models, 22 of 28, 24 of 28 and 26 of 28 right), block-2 v = 1 at c = 0 hangs (4 of 4), block-2 v = 1 at c = 8 completes and counts as -1 (the next v = 3 job completes, the one after hangs), v = 0 at c = 8 in block 1 and in block 2 leaves c at 8 (the next v = 3 job hangs, 2 of 2 sequences: the model in which v = 0 resets c is refuted twice), and block-1 v = 1 at c = 0 completes (3 of 3); a post hoc variant of the counter of E700 fits all 80 jobs of the two tables"
unit = "vdm"
method = "tables vdm-series-b (28 jobs, declared as exploration, risky: 8 hangs, each followed by a reset and a health triangle that drew), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["VDM_STATE1.BITS11_9"]
+++
**What ran.** Six series of the stream of E700, 28 jobs, with v below 2: B1 (2, 1) four times
(block-2 v = 1 at c = 0), B2 (6,2) (6,2) (2,1) (3,2) (3,2) (block-2 v = 1 at c = 8), B3 (6,2) (6,2)
(2,0) (3,2) (3,2) (block-2 v = 0 at c = 8), B4 (6,2) (1,2) (1,2) (1,2) (6,2) (6,2) (block-1 v = 1 at
c = 4), B5 (1,2) three times (block-1 v = 1 at c = 0), B6 (6,2) (6,2) (0,2) (3,2) (3,2) (block-1 v =
0 at c = 8). The first job of a series follows a reset. Three models were frozen: M0 (a v below 2
adds 0), M1 (v = 1 adds -1, c not below 0) and M2 (M1, v = 0 sets c to 0, and a v = 1 in block 2
hangs iff c = 0). M1 and M2 were formed on earlier jobs with v below 2 (E413's late sets), so the
series are prospective for the frozen models, not held out of the choice of their clauses, and the
set is declared as exploration.

**Results.** [HW] Hangs: B1 jobs 1 to 4, B2 job 5, B3 job 4, B4 job 6, B6 job 4, B5 none. M0 22 of
28 (B1 0 of 4, B2 3 of 5), M1 24 of 28 (B1 0 of 4), M2 26 of 28 (B3 and B6 4 of 5 each: job 4 of
each, predicted to complete, hung). By series: B1 only M2 right; B2 M1 and M2 right (M0 predicted a
hang at job 4); B3 and B6 M0 and M1 right, M2 wrong; B4 and B5 all three right (B4 does not separate
them: v = 1 at c = 4 changes nothing the next jobs can see).

**What the pairs fix.** [HW] B2: the v = 1 job at c = 8 completes, the next job adds 1 and
completes, the one after hangs, so c after the v = 1 job was 7, g(1) = -1 (on a linear counter a
completion needs c + g(1) <= 8, the next one c + g(1) + 1 <= 8 and the third c + g(1) + 2 > 8: from
c = 8 only g(1) = -1 fits). B3 and B6: the v = 0 job completes at c = 8 and the next job (adding 1)
hangs, so c stayed at 8 and g(0) = 0. B1: a block-2 v = 1 hangs from c = 0 in 4 of 4 jobs, B5: a
block-1 v = 1 does not (3 of 3).

**Fitted, not confirmed.** [infer] M3 = M2 without the v = 0 reset (g(0) = 0, g(1) = -1 with a
block-2 v = 1 hanging at c = 0, g(v) = v - 2 above) fits all 80 jobs of E700 and this one. It was
formed from the 28 jobs it fits: it is fitted, and needs a held-out run (series with v = 0 and v = 1
at other counts, block-2 v = 1 at c = 1, and at c = 0 after a reset that follows no hang). Whether
g(1) = -1 is a decrement that the hardware clamps at 0, and why block 2 hangs at c = 0, is not
shown: the sign of c below 0 is not observable in block 1 (B5).

**Not shown.** One sequence each for the c = 8 pairs (B2, B3, B6); the shape dependence of E700's
Not-shown paragraph applies (Q163).
