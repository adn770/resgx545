+++
id = "E535"
claim = "With a different marker in every job, E519's two-phase fill (started with 8 temporaries, phas #T, r123 written with the job's own marker and read back as o0) read the job's own marker in 2048 of 2048 pixels for the 6 requests T = 260, 264, 300, 316, 376 and 448 in both runs (12 of 12 jobs) and for the 6 controls that write inside the request (T = 124, 128 and 192 with r123, T = 8, 32 and 64 with r3, r31 and r63: 12 of 12 jobs), and did not read it in any pixel the report lists, for the 6 requests T = 4, 8, 16, 32, 64 and 100 that write r123 (0 of 12 jobs: run a lists all 2048 pixels of each of its six jobs, run b only its top four values, 1656 to 2040 of 2048 pixels per job), where the pixels read other values (0x403, 0, 0xa4a5a6a7, E519's marker 0x7e57007b, 0x7e570003 and, in the run in reverse order, the markers of earlier jobs of that run: 17 of the 24 values its report lists for those six cases); so a write to r123 is not seen by the read of r123 in the same job when the request is 100 or less, the read-back of r123 at 260 to 448 in E519 was a write that landed, and [infer] five of those requests (260, 264, 300, 316 and 376, which the modulo-256 rule makes 4, 8, 44, 60 and 120 registers) allocated at least 124"
unit = "usse"
method = "on the laptop (direct cable), linux fork tip d614af574cc6 (6ee9501832af plus the three debug-only own-task commits, not armed), module srcversion 7ED723C25D78D7FCB3C08C1, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, as E519), template probes/usse/templates/temps_phas.s (E519's, unchanged), tables probes/usse/q147-a.toml (sha256 70aa30e885e7...d1210, markers from seed 1130, in the order 6 requests of 4 to 100, 6 of 260 to 448, 6 controls) and q147-b.toml (sha256 090e64fd8f32...dfef, seed 11301, the same 18 cases in the reverse order with fresh markers); one process per case, one fill per job, no fault, no recovery, the baseline fill and triangle diff 0 of 4096 before and after each run; 18 markers per run of the form 0x7nnnnnnn, 36 in all, all different from each other and from 0x7e57007b. Runs p1130-q147-a and p1130-q147-b (one each; the kernel log of both holds no entry). Both tables' hypotheses came out NONE, as table errors and findings: 'every write landed' fits 12 of 18 cases in each run (not the six requests of 100 or less) and 'a write past the allocation is dropped, a write inside lands' fits 6 of 18 (the controls only: its form o0_not cannot be true of mixed pixels, and it is false for the six requests of 260 to 448, which landed). Client pixel jobs, not firmware tasks"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-q147-a", "usse-q147-b", "vectors-usse-q147"]
terms = []
+++

**What ran.** E519's job with a marker of its own in every case, so that a write that landed is
told from a stale read of an earlier job (E484). 18 cases a run, two runs, 36 jobs: 6 requests of
100 or less (T = 4, 8, 16, 32, 64, 100) that write r123, 6 requests of 260 to 448 that write r123,
and 6 controls whose write is inside the request. Run a took the 6 requests of 100 or less first,
then those of 260 to 448, then the controls; run b the reverse, with new markers.

**Results.** [HW] Run a: the 12 jobs of T = 260 to 448 and of the controls read the job's own
marker in 2048 of 2048 pixels. The six jobs of T <= 100 read mixed pixels: 0x403 (all six, 904 to
1890 pixels), 0 (T = 4, 8 and 100: 1024, 512 and 1022 pixels), 0xa4a5a6a7 (T = 8 and 16: 512 and
856), 0x7e57007b (T = 16, 32 and 64: 288, 226 and 158) and 0x7e570003 (T = 100: 2); the own
marker in none. Run b: the same split. Its six jobs of T <= 100, which now come after the large
requests, read those jobs' markers: the marker of the T = 260 job, the job just before, in 512 to
1422 pixels of each of the six, and in some also those of T = 264, T = 300 and of the controls
T = 8 and T = 32 (17 of the 24 values listed are the marker of another job of the run), besides
0x403, 0, 0xa4a5a6a7 and 0x7e57007b. The own marker did not appear in run a's six jobs of T <= 100
(all 2048 pixels of each are listed) nor among the pixels run b's report lists. That report lists
only the top four values of each job (1656 pixels for T = 4, 1856 for T = 8, 1689 for T = 16, 1856
for T = 32, 1886 for T = 64 and 2040 for T = 100 of 2048) and the rest as "other" (392, 192, 359,
192, 162 and 8 pixels), so 0 of 12 jobs is complete for run a and, for run b, for the listed
pixels.

**What it shows.** [HW] In a client fill, a write to r123 under a request of 100 or less is not seen
by the read of r123 in the same job: 0 of 12 jobs (all pixels of run a's six, the listed pixels of
run b's six), the values read being what earlier jobs left (E484). A write to r123 under a request
of 124, 128, 192, 260, 264, 300, 316, 376 or 448, or a write inside the request, lands: 24 of 24
jobs. The read-back of r123 in E519's `phas-high-b` and `phas-high-c` (T = 260 to 376) was therefore
a write that landed and not a stale read of the earlier job's marker, and E486 (a write past the
allocation is not seen) and E519 do not disagree: E486's drop is the T <= 100 row here. [infer] The
rule that fits which requests run and hang (E519: T mod 256 is 4 to 192) does not give what they
allocate: under it the requests 260, 264, 300, 316 and 376 would hold 4, 8, 44, 60 and 120
registers, and a write to r123 would have been dropped as at T <= 100; it landed in 10 of 10 jobs.
The request of 448 (192 registers under the rule) is no test of the rule. A request above 255
therefore allocates at least 124 registers for these five values; what it allocates is open (Q144).

**Against Q147.** Q147's three runs were: E519 with a marker per job, E486's probe with the marker
written to r(n) only, and E519's probe with a marker first written to r(n mod T). Only the first
ran, as these two runs (the same table in two orders). The question's title is answered in part
(E486 and E519 do not disagree), its open parts about where a write goes and about the 88 to 99.6
percent of E486 are not.

**Not shown.** Where a write past the allocation goes (it is not in r123 of the next job: the
values read are leftovers of earlier jobs, E484), T between 101 and 123, a write to r(n) only or to
r(n mod T) first, the 8 to 392 pixels per job that run b's report does not list, what any request
above 255 allocates, a firmware task (E540), and any case with a request above 448 or below 4.
