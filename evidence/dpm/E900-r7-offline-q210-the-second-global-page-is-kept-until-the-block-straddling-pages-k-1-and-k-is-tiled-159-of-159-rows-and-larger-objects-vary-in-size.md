+++
id = "E900"
claim = "Round 7 offline stage G3 and G5 to G7 (Q210; no run): for the tool's 1500-vertex triangle the first partial render leaves 2 global pages iff S_k < thr0 < A_k, else 1, A_k being the page count of E874's frozen replay once object b_k = floor(1024 (k - 1) / 67), the object block that straddles global pages k - 1 and k, is tiled (H-SPAN; E874's B_k took the first object from b_k - 3 on whose index is divisible by 15, the same object for k up to 4): frozen verdict HELD, 159 of 159 scored rows at eight targets (fit R6-dpm r-m's 15 rows at 2048x2048 bands 5 to 7, where E874's B gives 10; SEMI the other 144, all of which B gives too, so no row outside the fit separates the two), A_k being 0x178, 0x1c3 and 0x20d at bands 5 to 7 there, the observed first one-page cells; the frozen rule left out R6-dpm's four --vtx-coords rows and five rows at the threshold clamp; read from R6-dpm r-v's two calibration dumps, the object blocks are 127 dwords for all 100 objects with --vtx-coords 4, and with 8 the stream names 97 objects whose blocks are 79 to 198 dwords (187 in 66 of 96, 196 in 9, 189 in 10), the entry with the base dword is that of the object whose block holds global dword 1024 (k - 1) on the read sizes (12 of 12 at N 4; 17 of 17 at N 8, post hoc after a fix of the test), and E874's replay with those objects places 9 of 12 steps at N 4 and 1 of 17 at N 8, so H-CUM is not frozen; the kept 2048x4096 dumps (all overflowed) do not read the S3 miss, and the end-state dumps do not read the lag"
unit = "dpm"
method = "Offline, no run (round 7, area dpm, decision R7-1 a; plan closing7/b/exp-dpm-r7.md section 3, steps G3 and G5 to G7; no lead stop). The scripts in closing7/b/offline/ (standard library only; olib.py, the round 6 library from its published twin cited/closing6/dpm/offline/ (f5lib.py, f4_phase.py, f3_streams.py, r6lib.py, all unchanged), pbdump.py and dpm_words.py of this tree) read resgx545-data render/closing-* read-only. g3_span.py: the rows of f4_phase.rows_and_refs (every kept job of the 1500-vertex scene with 0x0724, 0x072c, 0x0658 and 0x0624 sampled; thr0 from 0x0624 at the first partial render, the pages left from 0x072c at its end), grow cells (thr0 = S_k) not scored, and two exclusions fixed before scoring: rows of --vtx-coords jobs and rows at the clamp (thr0 >= 0x400, E753). g5_blocks.py: the two calibration dumps (P 0x422, one TA run): every region's stream through f3_streams.chain, the global pages ordered by the order the streams name them, each object's ISP address placed on that order, block sizes as the differences, the base-dword and block-opening objects by region count, the steps from the job's own timeline by F1's bracket rule; then H-CUM (b_k the object whose block holds global dword 1024 (k - 1)) tested by (a) the base-dword objects and (b) f5lib's replay logic with those b_k against the brackets, frozen for the session only if both held at both N. g6_s3miss.py and g7_lag.py: exploratory readings, no verdict. Freeze order (FREEZE-LOG.txt, sha256 in FREEZE-g<n>.sha256 before the first run that opened held-out data): g3_span.py (no dry run); g5_blocks.py after a dry run on the N 4 dump (its steps 9 of 12 already made H-CUM unfreezable; a smoke run had processed the N 8 dump with its lines cut unseen); g6_s3miss.py; g7_lag.py. Fixed after their first runs (as-run copies kept): g5_blocks.py, whose test (a) counted only objects carried by more than half of all regions with a stream (FIX-g5.md; the N 8 line moves from NO to yes, post hoc), and g6_s3miss.py, which stopped on a stream link into a reused page (FIX-g6.md). Each re-run from the published copy (resgx545-data cited/closing7/b/offline/, Python 3.15.2) gave output byte-identical to the kept one, the as-run g6 apart, whose traceback names the copy's paths. The planner's tallies (closing7/b/q210_phase2.out, closing7/b/q210_n8blocks.out) are why the G3 rows and the N 8 dump are SEMI"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r1-pixgeo:out/", "render-closing-r2-geo:out/", "render-closing-r3-geo:out/", "render-closing-r5-dpm:out/a2/", "render-closing-r6-dpm:out/a2/", "render-closing-s1:out/g-e1/", "render-closing-s1b:out/g-e1/", "cited-scratch:cited/closing7/b/"]
terms = ["Dynamic Parameter Management (DPM)", "CR_DPM_GLOBAL_PAGE_STATUS", "CR_DPM_PAGE_STATUS", "CR_DPM_TA_GLOBAL_LIST", "CSTREAM.PRIM_TILES", "CSTREAM.OBJ_ISP_ADDR"]
+++
**What was done.** E874 put the end of the margin in which the first partial render keeps a
second global page at B_k, the page count once the first object with an index divisible by 15 is
tiled; R6-dpm found one page left only from B_k + 2, + 2 and + 1 at bands 5 to 7 (E881). Reading
E874's replay object by object around each burst, the round 7 planner noticed that b_k is 15, 30
and 45 for k = 2 to 4, where B_k's object is b_k itself, and 61, 76 and 91 after, where it is not,
and named H-SPAN: the margin ends at A_k, the page count once b_k, the block that straddles global
pages k - 1 and k, is tiled. G3 scores it under a freeze on every kept row. With larger vertices
(E882) the blocks stop being one size; G5 reads the two r-v calibration dumps for the block sizes
and the objects at which stream blocks open and global pages start. G6 and G7 read the dumps for
the 2048x4096 S3 miss and E874's lag of 3 objects.

**Results [HW; fit, SEMI and post hoc as labelled].** G3, `g3_span.out`: frozen verdict
`VERDICT H-SPAN: HELD (0 rows off; fit 15 r-m rows, the rest SEMI)`, 159 of 159 rows. By label and
target (H-SPAN, E874's B, rows): fit 2048x2048 bands 5 to 7, 15, 10, 15; SEMI 2048x2048 bands 1
to 4 53, 53, 53 and bands 5 to 7 6, 6, 6; 4096x4096 35; 2048x4096 12; 3072x3072 10; 4096x2048 10;
2048x1024, 1024x2048 and 1536x1536 6 each, B holding every SEMI row as H-SPAN does. B's five
misses are the r-m cells `0x176`, `0x177` (band 5), `0x1c1`, `0x1c2` (band 6) and `0x20c` (band 7),
all 2 pages left. A_k at 2048x2048 is `0x97`, `0xe3`, `0x12e`, `0x178`, `0x1c3`, `0x20d` for k = 2
to 7. Not scored by the frozen rule: the four `--vtx-coords` rows at band 2 (2 pages left at thr0
`0x99` and `0x9a`, which H-SPAN at the 67-dword scene would give 1) and five rows at thr0 `0x400`;
the planner's tally had placed four of those five.

G5, `g5_blocks.out` (N 4 fit, N 8 SEMI):

| | N 4 | N 8 |
|---|---|---|
| regions with a stream | 2450 | 4689 |
| objects named | 100 | 97 |
| block sizes (dwords) | 127 (99 of 99) | 187 (66), 189 (10), 196 (9), 198 (3), 7 others |
| global pages, run peak | 13, `0x21a` | 18, `0x2b3` |
| objects with the base dword | 8, 16, ..., 96 | 5, 10, 16, 21, 27, 32, ..., 87, 92 |
| H-CUM b_k equal to them | 12 of 12 | 17 of 17 (post hoc) |
| block opens (1800+ regions) | 0, 15, 29, 43, 57, 72, 86 | 0, 3, 12, 25, 38, 50, 63, 76, 88 |
| steps of E874's replay with those b_k | 9 of 12 (S4, S9, S10 off by 3, 2, 2) | 1 of 17 |

The other N 8 sizes are 178 (twice), 79, 171, 175, 184, 191 and 193. The replay's need at N 4
is the run peak, `0x21a`; at N 8 it gives `0x262` against `0x2b3`. The as-run test (a) read NO
at N 8 (FIX-g5.md). Output: `H-CUM: NOT frozen`.

G6, `g6_s3miss.out` (exploratory): the eleven kept 2048x4096 dumps are all of jobs that took a
partial render (the calibration too, at the clamp, thr0 `0x400` below the need `0x40d`), so their
streams name only the objects since the last one, with indices relative to it; three of the eleven
streams link into a page the TA reused and are not read. G7, `g7_lag.out` (exploratory): of 183
kept 1500-vertex dumps whose state page names a global list, 148 are read; in 113 no object block
follows the last object any stream names, in the others 1 to 11 do.

**What it shows.** At the 67-dword scene the margin's end is the straddling block, not a multiple
of 15: H-SPAN gives every scored row, including the five r-m cells E874's B_k missed [HW, fit and
SEMI]. [infer] The partial render keeps the global pages that the objects written and not yet
tiled span: two while the straddling block is among them, else one. With larger vertices the base
dword still marks the object whose block holds dword 1024 (k - 1) of the global list, from the
sizes read in the dump [HW, fit at N 4, post hoc at N 8], and the stream blocks then open where
those extra dwords make the 31 entry dwords run out (29, 43, 57, ... at N 4, every 14 or 15
objects). At N 8 the objects are not one size and fewer (97 for 1500 vertices) and the scene covers
nearly twice the regions, so the five-triangle object model under E874's replay does not describe
that scene [HW, reading].

**What it does not show.** H-SPAN is not held out: the only rows where it and E874's B differ are
the 15 it was written after, and the 144 others had been tallied by the planner; the plan's s-m
stage holds the discriminating cells. Its value at the `--vtx-coords` scenes and at the clamp is
not scored. What sets an object's size at N 8 (which vertices a block holds) and why the N 8 scene
covers 4689 regions are not read, so H-CUM is not frozen and Q210 keeps "what opens the bursts for
larger objects". The N 4 step misses (S4, S9, S10) stay as E882 left them. The 2048x4096 S3 miss
and the lag are not read: no kept 2048x4096 dump is of a single TA run, and the kept dumps are end
states, not the abort.
