+++
id = "E500"
claim = "In three more runs of the 15 jobs of E475's usse-pclink-pixels (a, b and c: 30 reader jobs, 40 with E475's own run), the pixels that read another value than the writer's are 0xeb3 in 48 to 80 pixels of a job (exactly 64, 16 aligned 2 x 2 quads, in 29 of the 40 reader jobs: 6, 8, 7 and 8 in the four runs) and 0x98 in 16 to 64 pixels of 12 of the 40 jobs (2, 3, 2 and 5 in the four runs), no other value in any job, and their positions repeat in part and not whole: the minority pixels of one reader job in two of the four runs share 4 to 52 pixels over the six pairs of runs (1 to 13 quads, 3 to 13 in the runs a and b, where two random sets of 16 of the 512 quads would share about 0.5), and all four runs share 0 to 16 pixels of a job; two different reader jobs of the same run also share quads, 1 to 12, 1 to 12, 2 to 13 and 1 to 16 over the 45 pairs of each of the four runs"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/pclink-repeat.toml (dump.s, 3 probes a, b and c of 15 jobs each in the order of E475's usse-pclink-pixels: a writer and two readers, five times, `pixels = true`, 45 jobs, every pixel kept); the campaign runner once for the table, each probe one run; compared with the one run of usse-pclink-pixels (dataset usse-pclink, E475). The counts were computed from the raw.txt pixel grids (each job a 64 x 32 grid) by a script written after the runs (not kept in the tree); in every run of every reader job each deviant pixel has its x^1, y^1 and diagonal neighbours deviant as well (0 exceptions), as E475 found for its own run"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-pclink-repeat", "usse-pclink"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The 15 jobs of E475's pclink pixel probe three more times: `mov pclink, r1; mov r10,
pclink` with r1 = 0x12345, 0x2abcd, 0x155, 0x3ffff and 0xabcd, each followed by two jobs `mov r10,
pclink`, o0 = r10, every pixel kept (the writer's job is uniform; the readers' pixels are counted
against the writer's value).

**Results.** Per run, over its ten reader jobs: 0xeb3 in exactly 64 pixels in 6 jobs (E475's run), 8
(a), 7 (b) and 8 (c), in 48 to 80 pixels in all jobs (48 to 68 in E475's run, 64 to 80 in a, 48 to
68 in b, 64 to 68 in c); 0x98 in 2, 3, 2 and 5 jobs, in 16 to 64 pixels; no job has a third value.
The pixels shared by the same reader job in two runs (the minority pixels, 0xeb3 and 0x98 together):
a and b 12 to 52, a and c 8 to 44, b and c 8 to 52, E475's run and a 4 to 44, E475's run and b 8 to
40, E475's run and c 4 to 40, over the ten jobs. In common to the four runs: 8, 4, 4, 12, 0, 12, 4,
16, 4 and 0 pixels over the ten reader jobs in order. The quads shared by the runs a and b: 5, 7, 6,
7, 9, 9, 3, 10, 13 and 5 over the ten jobs; by a and c 2 to 11, by b and c 2 to 13, by E475's run
and a 1 to 11, and b 2 to 10, and c 1 to 10. Within a run, over the 45 pairs of its ten reader jobs:
two jobs share 1 to 12 quads in E475's run, 1 to 12 in a, 2 to 13 in b and 1 to 16 in c (the jobs
have 12 to 32 quads each; recounted from the raw.txt grids for the review, the script not kept in
the tree).

**What it shows.** [HW] The 0xeb3 count is 64 (16 quads) in most jobs but not all (29 of 40), the
0x98 pixels appear in some jobs and some runs only, and the positions are neither fixed nor
independent across runs or across jobs: they repeat in part from run to run, and two jobs of one run
share as many quads as one job shares between runs. [infer] The partial repeat suggests a dependence
on the instance's place in the tile and on the job before it, which this table does not separate: no
table here controls for the job before, and a job-to-job dependence is not shown.

**What it does not show.** The cause, the values' origin, and whether the counts depend on the
writer's value (the five writers' jobs are not separated by run here). Narrows Q125 (the run-to-run
part: counts mostly 64, positions partly kept); the cause stays open.
