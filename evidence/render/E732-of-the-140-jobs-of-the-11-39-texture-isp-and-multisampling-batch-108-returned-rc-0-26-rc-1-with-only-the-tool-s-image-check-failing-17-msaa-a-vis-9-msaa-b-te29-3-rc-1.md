+++
id = "E732"
claim = "Of the 140 jobs of the 11.39 texture, ISP and multisampling batch, 108 returned rc 0, 26 rc 1 with only the tool's image check failing (17 msaa-a-vis, 9 msaa-b-te29), 3 rc 1 and 3 rc 3 with a faulted job (q140: 3, tex-c-addr: 3), none a usage error and none void; the kernel lines naming sgxfive in isp-a-guard (60) and isp-b-depth (105) are the 5 kpoke acknowledgements of each job, no fault"
unit = "render"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = []
+++
**Accounting.** 140 jobs in 13 scripts (the 13 cases.tsv list 140): rc 0: 108; rc 1: 29; rc 3: 3.
The run log's "exit=1" is the last `[ ] && ` test of the runner; all 13 scripts report rc 0, 0
declared mismatches and every job kept. Hash checks before reading: declared.tsv, predictions-
declared.tsv and manifest-1141tex.sha256 equal the sha256 of plan.md section 8; 27 of 28 manifest
lines verify with sha256sum -c and the 28th (the 74 staged programs) equals the sha256 of
`sha256sum stage-bins/*.bin`.

**The 26 silent rc 1.** msaa-a-vis (17) and msaa-b-te29 (9). Each printed "tri: render context for
targets up to ...", the vertices, the 0x0494 to 0x04b4 registers (vis), the image rows or dumps,
and "diff: N of M pixels, first (x, y) 0xff203040 expected 0xff00ff00": the tool's check of the
picture against its own plain-triangle expectation under --keep-going. vis: N = 12 to 156 of 4096;
te29: 3969 of 4096 and 16129 of 16384 with "0 triangle, 4096 background" and "0 of 1 renders ok",
the render completed with an empty image, and param and TA dumps of 4.6 MB and 24 KB were kept
(E728). No "usage", "unknown option" or rc 2 string occurs in any output; stderr was kept only for
the 3 q140 jobs (the tool wrote none for the 26). So they are results, not voids: the mismatch is
the thing measured (the model's images, E727; the empty image of E281, E728). The plan anticipated
the failed image check explicitly only for te29 ("--keep-going already reaches --dump-render after
a failed image check"); for vis it is implied, since the images are judged against the region
model, not against the tool's check. No rc was a frozen prediction.

**The 6 faulted jobs.** q140-288x144, -256x288, -384x384 (rc 1, "render: job faulted, context lost
(Input/output error)", BIF fault 0x90004, E729; the plan expected faults); ad-tw64x64-L2e2, -L3e3
and ad-st128x32-L3e2 (rc 3, "probe ...: failed: job faulted", BIF fault 0x90002, E722; not
expected: the plan gave tex-c-addr as low risk). Each followed by a reset and a health triangle
that drew again (0 of 6 stopped a script). These are hardware results: valid jobs whose frozen
prediction fails.

**The kernel-log lines.** The recompute's counter matches "sgxfive", "BIF fault" or "recovery":
isp-a-guard 60 = 12 jobs x 5 "sgxfive: kpoke ta:7^=0x80, rd:1, rd:11, rd:12, rd:13 applied" lines
(the tool's own render pokes), isp-b-depth 105 = 21 x 5, none an error. tex-c-addr 4 = the 3 BIF
faults and 1 devcoredump line. msaa-c-q140 15 = 8 BIF faults, 3 "SGX recovery failed: -110", 3
"render context cleanup failed, resetting" and 1 devcoredump line; the 8 faults are the 3 jobs'
own and 5 of the health triangles after them.

**What it shows and does not.** All 140 jobs are valid results; 3 of 140 are faults the plan did
not predict (tex-c-addr). One scorer defect is found (E730, the observable of isp-a-guard) and one
window defect (E729, health faults counted for the job); neither is a job defect.

**Correction 2026-11-11:** The three q140 faults are our kernel's one-array layout, not a property
of the hardware (E788, E824), so "these are hardware results" holds for the 3 tex-c-addr jobs and,
for the q140 jobs, only as the hardware's response to our layout; the counts are unchanged.
