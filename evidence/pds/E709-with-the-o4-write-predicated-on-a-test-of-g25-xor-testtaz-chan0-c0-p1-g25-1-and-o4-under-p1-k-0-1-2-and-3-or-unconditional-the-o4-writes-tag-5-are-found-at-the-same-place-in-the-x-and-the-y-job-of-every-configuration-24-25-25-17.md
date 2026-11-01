+++
id = "E709"
claim = "With the o4 write predicated on a test of g25 (`xor.testtaz.chan0 !c0, p1, g25, #1` and o4 under p1, k = 0, 1, 2 and 3) or unconditional (5 configurations, each an x job and a y job, none repeated), the o4 writes (tag 5) are found at the same destination pixels in the x and the y job in 24, 25, 25, 17 and 29 pairs, 120 in all, every one from an even source x and an even source y: pairs exist for every k, so the predicate has no visible effect on whether o4 is written; the number of pairs (17 at k = 3 against 24 to 29) and of tag-5 pixels (25 to 48 a job) varies between configurations and no repeat says whether that is noise; the frozen lane-0-only model was right in 4 of 10 jobs (two configurations) and the any-lane model in 10 of 10 only by predicting nothing the predicate could change; no job with a predicate that cannot hold was run, so the table does not say what g25 selects"
unit = "pds"
method = "table o4-g25 (10 jobs, risky as declared, none failed: probe --tri pixel --temps 32 --pixels --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001 (PDS_SIZE 3 with one data row, the setup of E406) --slot pixpds=pds_iter_xy.bin:12 with the pixel program o4g-K-x or o4g-K-y), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["PDS_SIZE.BITS17_16"]
+++
**What ran.** The output-room shader of E570 (o0 to o7 each written with a tag in the low nibble 1
to 8 and a job marker) with the write of o4 guarded: `xor.testtaz.chan0 !c0, p1, g25, #1` before it
and `p1` on the o4 instruction, the xor operand k = 0, 1, 2, 3 (o4g-k), or no guard (o4g-u), an x
and a y job each (the pixel's own coordinates are read back from the high half, as in E570). The
frozen models: HL0 (lane 0 only: o4's tag-5 pairs for k = 0 and the unconditional job, none for k =
1 to 3), HAny (any lane: pairs in all five) and HNot (g25 is no lane id: no prediction).

**Results.** [HW] Tag-5 pixels (o4) per job: 37 and 40 (k = 0, x and y), 25 and 32 (k = 1), 25 and
36 (k = 2), 43 and 36 (k = 3), 33 and 48 (unconditional). Pairs (the same destination pixel in the x
and the y job, both tag 5 with the job's own marker, source decoded from the coordinate half): 24,
25, 25, 17 and 29, all 120 from the source parity (even x, even y), as E570's rule says, and as the
2007 pairs of tags 5 to 7 of the output-room tables (o23-order 887, o23-size 66, o23-tiles 1054)
which the recompute of this session pairs with no exception (plan.md section 1.4 and the merges
list 2393 for those three tables: that is the count of the Opus report's pairing, which finds more
pairs by a rule not rechecked here, also with no exception; this record uses the one count of this
session's pairing, 2007). The pairs do not vanish for k = 1 to 3: 25, 25 and 17 against 24 for k =
0 and 29 for the unconditional job. The count at k = 3 is the lowest, a difference that the data
cannot call noise or effect, since no configuration was repeated; the tag-5 pixel counts alone run
from 25 to 43 in the x jobs and 32 to 48 in the y jobs. The tag-5 pixels without a pair (the tag-5
count of a job minus the pairs, x and y) are 13 and 16 (k = 0), 0 and 7 (k = 1), 0 and 11 (k = 2),
26 and 19 (k = 3) and 4 and 19 (unconditional); they were not examined. The 10 jobs are 5
configurations scored twice, x and y. HL0 4 of 10 (right for k = 0 and the unconditional job, 6
jobs wrong), HAny 10 of 10.

**What it shows.** [HW] o4 reaches even-even pixels in pairs whatever k of g25, with or without the
guard: the conclusion is about the presence of pairs (more than 0), not about how many. Two
readings, not separated: the instance test is true for every k (impossible if g25 is a lane id that
differs between instances, unless the `testtaz.chan0` predicate is the channel 0's alone and applies
to all), or the predicate does not gate the write in this program. A guard that cannot hold (k = 7)
was not run, so whether the predicate acts at all is not known; no reading of g25 as a lane number
follows. [HW] The rule of E570 that o4 to o6 land from the even-even pixels holds on these 120
pairs; the shader and the tables are the family it was found on, so they are not independent of it.

**Not shown.** The effect of the predicate (a k that cannot hold as control, a guard on another
register); the lane reading of Q023.
