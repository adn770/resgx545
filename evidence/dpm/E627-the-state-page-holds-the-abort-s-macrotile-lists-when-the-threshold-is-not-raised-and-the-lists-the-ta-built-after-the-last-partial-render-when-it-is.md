+++
id = "E627"
claim = "The TA data's state page after a job's partial renders holds two different things, split by whether the first abort's threshold was raised (E625; TA3DCtl dwords 37 and 38 non-zero): in 28 of 28 jobs (8 distinct cells) that were not raised (1024x768 in 0x2d to 0x34 pages, 4096x4096 in 0xb8, 0xc0 and 0x100, among them the 0x30 job after a reset, without one and in the other tables) the sum of the 16 macrotile lists' counts is exactly thr0 - 1 (the pages taken at the abort less one: E310's 13 and 221) and the macrotiles missing from the page are the last ones the TA tiled (7 and 10 at 0x30 for the default triangle); in 38 raised jobs (about 12 distinct cells) the sum is, approximately, the pages the TA took after the last partial render, (U + k - thr0) - (n - 1) * (thr0 + 0x1f) with n the count of E625 and k = 2, differing by -2 to +2 in 35 jobs and by +4 in the 3 jobs at 4096x4096 in 0x23 pages (a loose fit, not an exact law), and the macrotiles missing are the earliest ones (0, 4, 8 at 0x28), so E464's 18 dwords at 0x28 (9 lists, pages 9 to 0x14) and E310's 0x30 and 0x100 rows are two regimes of one page, not a disagreement; entry 16 (the global list) is one page, page 1, in 9 of 9 scored jobs; the lists' end pages are distinct in 9 of 9; in 24 of 26 jobs that held lists the lists name only macrotiles the triangle covers on the 4 x 4 grid by an 8 x 8 sampling of each macrotile (the author's test, not in a declared file; the 2 others, the triangle moved by (-128, 96), list macrotile 13, which that sampling does not cover, were not checked at a finer grid); the macrotile set follows a move of the triangle (0x30: 9, 9, 9, 7 lists for the moves (0,0), (256,0), (0,192), (-128,96); the (384,288) move completes at 0x30 with no list and has 3 lists at 0x28)"
unit = "dpm"
method = "the TA data dumped after each render (--dump-each) in the jobs of table state (26 jobs) and the fr, trig, dp-z05 and follow-up a jobs, on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B, stock firmware, tool sgxfive-test-1135 (sha256 7732b945...): the default triangle at 1024x768 and 4096x4096, moved and doubled in table state; the state page read at TA data offset 0x6000 (1024x768) or 0x42000 (4096x4096) as 17 pairs by the dataset's analysis/an_state.py"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["dpm-partial-model-batch"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_STATE_BASE0", "ta3d_ctl"]
+++

**What ran.** Table `state` (26 jobs) and the `fr`, `trig`, `dp-z05` and follow-up a jobs that
dump the TA data (`--dump-each`): the default triangle at 1024x768 in 0x28, 0x2a, 0x2c, 0x30,
0x34, 0x36 pages, moved by (256,0), (0,192), (-128,96), (384,288) at 0x30 and 0x28; 4096x4096 in
0x40 and 0x23; two triangles (`--geometry 1 --move 2:-96,0`, and `-n` forms) at 0x38, 0x3c, 0x40,
0x48; the 0x30 job repeated after a reset and without one. Decoders: the state page at TA data
offset 0x6000 (1024x768) or 0x42000 (4096x4096) as 17 pairs (count << 16 | head, tail),
`analysis/an_state.py` (macrotiles numbered down then across, covered when a sample of an 8 x 8
grid of the macrotile lies inside the triangle; this coverage check is mine, not in the declared
files).

**Results [HW].** Declared: H-state-abort (the page holds the lists at the last abort: sum
thr_last - 1), H-state-end (the lists of the TA's end: sum about U - thr_last), H-state-last (only
the last partial's lists remain), H-global, H-state. Scores: H-global 9 of 9 scored (fit 2, held
out 7, one no data), the lists' disjointness 9 of 9 scored, H-state-abort fit 1 of 2 and held out
4 of 12 scored (the misses are the raised jobs), H-state-end fit 1 of 1 and held out 6 of 7
scored, H-state-last 0 of 2 (the 4096x4096 jobs, 5 and 10 partial renders: the sum is 17 and 4,
not the 61 and 32 of the abort). Split by the raise: not raised, the sum is thr0 - 1 in 28 of 28
jobs (10 at 0x2d, 11 at 0x2e, 12 at 0x2f, 13 at 0x30, 17 at 0x34, 149 at 0xb8, 157 at 0xc0, 221 at
0x100, repeats included); raised (38 jobs), the sum is within 2 of (U + 2 - thr0) - (n - 1) *
(thr0 + 0x1f) in 35 (differences -2 in 7, -1 in 19, 0 in 6, +2 in 3) and 4 above it in the 3 jobs
at 4096x4096 in 0x23 pages (4 against 0). The remainder uses the U + 2 = 21 and 289 of E625 (k =
2). The 28 and 38 are jobs: the not-raised sums are 8 distinct values, the raised jobs about 12
cells, and only the not-raised rule is exact. The macrotiles missing from the page: raised, the
earliest ones (0, 4, 8 at 0x28 and 0x2a, 0, 1, 4, 8 at 0x2c; for the moves 4, 8, 12 / 1, 5, 9 /
10); not raised, the last ones (7 and 10 at 0x30, 7 at 0x34, 3 and 7 for the (-128,96) move). The
repeat of the 0x30 job without a reset holds the same lists on the same pages (H-repeat 2 of 2;
the pages-differ statement missed, E626). The two-triangle jobs overflow at 0x38 (21 pages in the
lists, dword 35 0x14) and complete at 0x3c, 0x40 and 0x48 (6 jobs; the tool prints the image check
failing there, `wrong 50330 outside`, since the second triangle is not what it checks), so the
second triangle needs 23 to 26 pages at 1024x768.

**Reading [infer].** The store of the lists is made at the abort (sum thr0 - 1 when no raise) and
again, with the macrotiles tiled since, when the TA continues at the raised threshold: the page at
the end holds the second set. Whether the second store is made at the TA's end, at the final
render's start or at each later abort is not separated (the 4096x4096 jobs with 5 partial renders
hold the last set only, 17 pages). The differences of the raised sums from the remainder (-2 to +4
pages) may be pages the global list takes [infer: a guess, not tested].

**Not shown.** The lists' pages beyond the end pages (the page links are in the pool walk, E626);
what a load task does with them (E631's junk-in-the-page jobs: nothing changed, and the next
render stores the first 34 dwords again).
