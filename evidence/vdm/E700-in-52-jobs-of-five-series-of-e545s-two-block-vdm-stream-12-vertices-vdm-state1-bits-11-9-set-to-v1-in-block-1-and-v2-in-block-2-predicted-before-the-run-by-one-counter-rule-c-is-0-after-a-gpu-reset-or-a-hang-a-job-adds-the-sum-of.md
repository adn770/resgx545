+++
id = "E700"
claim = "In 52 jobs of five series of E545's two-block VDM stream (12 vertices, VDM_STATE1 bits 11:9 set to v1 in block 1 and v2 in block 2), predicted before the run by one counter rule (c is 0 after a GPU reset or a hang, which in these jobs are one observation, the harness resetting the GPU after every hang; a job adds the sum of v - 2 over its blocks and hangs iff c + add > 8; a completed job keeps c), 52 of 52 outcomes follow the rule (15 hangs), among them 16 of 16 (7 hangs) on a seeded random walk (seed 1141, v from 2 to 7 in both blocks), the only series not built from the rule's own boundaries; a GPU reset clears c in the one job that could show it (c would have been 6)"
unit = "vdm"
method = "tables vdm-series-a (52 jobs, safe: the first job of each series after a debugfs reset, the others without one, a hang followed by the harness's reset and a health triangle that always drew), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded, equal in the ten scripts), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-1140 (sha256 bd55ffe69cf310f574f019ac3cbe3cccf0464d2e2addf0e47f940570440ffa76), debugfs reset, kpoke, hold_recovery and render_pb_pages only (no kreg, no kregnow, no clock-gate register written), run-all-1141ta.sh: 157 jobs in ten tables run in one pass (ten scripts, rc 0 each; the exit=1 at the end of the log is the runner's last test, not a failure), one process per job, a marker per job in the kernel log (157 of 157, in case order), every raw output and dump gzipped with its raw sha256 (741 files, every one equal to the sha256 printed at the run); predictions-declared.tsv (sha256 0641f37b18588b3da43d5cca8a6465221b0d634f23b636e495b10e6426d12b12) and the 82-file manifest (sha256 0817d98ea3d381aea4cf0e8135a09dfbe80da150a765ef762a6c06d100d6bc84) frozen before the first job (freeze1141ta.sh verify: files verified after the run); scored by analysis/post_1141ta.py (standard library, written after the run, not frozen) because the frozen recompute_1141ta.py cannot read the capacity dumps (it looks for NAME.param.bin.gz, the tool wrote NAME.<program>.param.bin.gz) nor the o4 rows (it reads `row N:` at line start, the tool prints `probe pix_pa0: row N:`); the frozen scorer also scored the two dpm-oom jobs that did not run (oom-1400-0x422 and oom-1300-0x422, refused by the tool, rc 2) as passes, which post_1141ta.py counts as void, and the reader of the eot-store table was replaced as well (a text regex became the job's rc; it gives the same 6, 8 and 4 of 10); the frozen predictions and scripts are unchanged (freeze1141ta.sh verify); plan.md is not in the 82-file manifest and was written (14:07:55) after it (14:06:18), so its criteria are attested by file times only, as is the freeze as a whole (local file times and the run log's clock, no external stamp); the output of post_1141ta.py is kept beside it"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["vdm-verification-1141ta"]
terms = ["VDM_STATE1.BITS11_9"]
+++
**What ran.** 52 jobs of the stream of E545 (probe --tri pixel, --temps 32, 64x64, --vertices 12, an
object of 6 vertices from the second block, programs p1131-green and p1131-blue) with bits 11:9 of
VDM_STATE1 xored to v1 in block 1 (word 1) and v2 in block 2 (word 9); v = 2 is the plain job.
Series: A1 (v1, v2) = (4, 2) 12 times, A2 (3, 2) 12 times, A3 (7, 2) 6 times, A4 a random walk of 16
jobs with v1 and v2 drawn from {2, 2, 3, 4, 5, 6, 7} by random.Random(1141) ((4,2), (2,4), (2,4),
(2,6), (7,7), (5,4), (5,6), (7,2), (6,7), (5,7), (4,3), (5,5), (5,3), (5,7), (6,4), (6,4)), A5 (5,
3) 6 times.

**The rule, frozen.** c = 0 after a GPU reset or a hang; each job adds g(v1) + g(v2) with g(v) = v -
2 (g(2) = 0); it hangs iff c + add > 8 (T = 8); a completed job keeps c. This is the rule read from
E413's 130 jobs (g and T are in sample there). The three models M0, M1 and M2 of the declared
predictions differ only for v below 2 and agree on every job of these 52.

**Results.** [HW] 15 of the 52 jobs hung (rc 3, `job hung, context lost`, one `*ERROR* sgxfive: job
N hung, recovering` line in the job's marker section each, none elsewhere): A1 at jobs 5 and 10, A2
at 9, A3 at 2, 4 and 6, A5 at 3 and 6, A4 at 4, 5, 7, 9, 11, 13 and 15 (counted from 1). All 52
equal the prediction. The nulls on the same 52 jobs: never hang 37 of 52; the best stateless
threshold on the job's own sum of v - 2 (hang iff the sum is at least T') 39 of 52 (T' = 9). On A4
alone: never hang 9 of 16, best threshold 11 of 16, the counter 16 of 16. Of A4's 7 hangs, 2 (jobs 5
and 9) exceed 8 by their own sum and 5 (jobs 4, 7, 11, 13 and 15) need the history.

**Reset.** [HW] A4 ended with a completed job of (6, 4) at c = 6; A5's first job, (5, 3), would have
hung from c = 6 (6 + 4 = 10) and completed: the debugfs reset the harness issues before the first
job of a series cleared c (one job; no other job at a series start separates a kept c from a cleared
one; recomputed from the jobs' own arguments and the kernel's hung lines). That is the single
observation about clearing: the harness resets the GPU and runs a health triangle after every hang,
so 'a hang clears c' and 'a reset clears c' cannot be told apart by any job here, and the only job
that shows a reset clearing c is this one.

**Held out and in sample.** A4 is the only held-out set: 16 jobs, drawn without reference to the
rule or to any earlier data (seed 1141, written into the generator before the run). A1, A2, A3 and
A5 (36 jobs, 8 hangs) were predicted before the run but built from the rule's boundaries (periods 5,
9, 2 and 3 of the counter), so they confirm its arithmetic and are not held out; the frozen
declared.tsv labels all 52 jobs of the five series 'heldout', and the downgrade of these 36 is made
here, in the record, not in the frozen file. g(v) = v - 2 and T
= 8 were fitted on E413 and stay fitted; they now hold on the 16 held-out jobs for v from 2 to 7 and
on 36 designed ones, with no miss.

**What it shows.** [HW] Whether a job with v from 3 to 7 completes is decided by the sum of v - 2 of
the completed jobs since the last reset or hang, plus its own: the word is not the whole input
(Q163), and the alternation of E413 at v = 7 is the period 2 of this counter (A3: .H.H.H, a job of 5
against a threshold of 8). The win over the nulls is not as large against a short memory: a rule
with the memory of one job (hang iff the job's own sum of v - 2 plus the previous completed job's
sum, zero after a hang, is at least 10) gets 15 of 16 on A4, with its threshold fitted on those same
16 jobs (optimistic), against 16 of 16 for the counter, 11 of 16 for the best stateless threshold
and 9 of 16 for never hang: on the walk the counter beats a window of one job by one job and the
stateless rules by five. A memory longer than one job rests on A1, A2 and A5 (periods 5, 9 and 3),
which were designed from the rule. [infer] That c is a count of something the jobs leave in the
VDM, the TA or the USE is not shown; the rule is a description.

**Not shown.** Every job here has one shape (12 vertices, two objects, 32 temporaries, 64x64):
whether g and T depend on the shape is untested (Q163). The jobs ran seconds apart (the 52 in about
3 minutes), so nothing here says whether time clears c. Whether a reset that follows no hang clears
c rests on one job.
