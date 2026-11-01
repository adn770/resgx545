+++
id = "E729"
claim = "At CR_TE_AA 0xe0000000 mode 2, 256 x 160 and 320 x 128 complete and 288 x 144, 256 x 288 and 384 x 384 fault the job at pages 0x20006, 0x20006 and 0x20008; with E507's 12 sizes this leaves the number f of region-header arrays the TA writes at 4 or 5 (f = 3 refuted; f >= 6 refuted post hoc; both under the layout formula as transcribed and integer f)"
unit = "ta"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
**What ran.** msaa-c-q140: 5 jobs, one per size, `tri` at CR_TE_AA 0xe0000000 mode 2 with the
closed driver's sample words (E507's setup), each in its own process, "risky", last of the batch;
all held out. The kernel layout formula of Q140 (rgn + f * rgn_size <= td.size completes, else a
BIF fault at page td.size >> 12) was frozen as the model; predictions per f in predictions-
declared.tsv.

**Results.** [HW] 256 x 160: diff 0 of 40960, rc 0. 320 x 128: diff 0 of 40960, rc 0. 288 x 144,
256 x 288 and 384 x 384: rc 1 "job faulted, context lost", 0 renders, the image left at the
0xdeadbeef fill. Kernel log (15 lines naming sgxfive, a BIF fault or a recovery): 8 BIF faults
(0x90004), 3 "SGX recovery failed: -110", 3 "render context cleanup failed, resetting", 1
devcoredump line. The first fault after each job's marker: 0x20006062 (job 8302, 288 x 144),
0x20006062 (job 8305, 256 x 288), 0x20008062 (job 8309, 384 x 384). The other 5 faults are the
health triangles after each failed job (job ids 8303; 8306, 8307; 8310, 8311; the tool's "health:
ok after a reset" for 288 x 144 = one failed health run, "recovered on the retry" for the other
two = two): 0x20006061, 0x20006061, 0x20006061, 0x20008061 and 0x20007061.

**Scores.** Frozen recompute as run (the fault pages of every fault between a job's marker and the
next one; consistent f of {3,4,5,6}): 256 x 160 {3,4,5}, 320 x 128 {3,4,5}, 288 x 144 {3,4,5,6},
256 x 288 {4,5,6}, 384 x 384 none (it sees pages {0x20007, 0x20008}). Plan's predictions
(completes or fails, f = 3 against f >= 4): 5 of 5 completion classes right for f >= 4 and 3 of 5
for f = 3 (256 x 288 and 384 x 384 are the sizes that decide). Pages: 288 x 144 and 256 x 288 as
predicted, 384 x 384 as predicted for the first fault (0x20008) and failed by the frozen scorer
through the page set. [infer] Taking each job's own first fault, f is {4,5,6} for 256 x 288 and
384 x 384, f in {3,4,5} for the two completed sizes, so f in {4, 5}; with E507's 12 sizes (f >= 4:
12 of 12) the same.

**Scorer note (not part of the claim).** The frozen scorer fails the page of the 384 x 384 job
only because its window takes the faults of the health triangles after it. The per-job first
faults, by the job ids of the kernel log, are those above (health triangles: jobs 8303, 8306,
8307, 8310, 8311). Under the layout formula as transcribed, f = 3 is refuted (256 x 288 and 384 x
384 fault, f = 3 completes them); f = 4 and 5 give 5 of 5; f = 6 to 10 give 3 of 5 (256 x 160 and
320 x 128 would fault). The frozen predictions listed only f = 3 and f = 4 or 5, so the f >= 6
refutation is post hoc use of the two completions.

**Contamination.** After each faulted 4x job the health triangle faulted at the same page region 5
times in all, and 3 of 8 recoveries failed (no INIT_COMPLETE, -110): state leaks into following
jobs until a reset. No reported result is affected: later jobs ran only after a health pass, q140
is last of the run, and the three tex-c-addr faults were followed by "health: ok" at the first
try (the 13 later A4 fits are unaffected).

**Population.** The 12 sizes of E507 fitted f >= 4; these 5 are held out and refute f = 3 (two
sizes) and, post hoc, f >= 6 (two sizes) and agree with f in {4, 5}. Fault behaviour cannot separate
f = 4 from 5 at any size to 1024 x 1024 (plan.md section 1.5).

**What it shows.** [HW] The multisampled layout runs out of memory at pages 0x20006 and 0x20008 as
the formula with f >= 4 says, and completes at 256 x 160 and 320 x 128. A failed 4x job leaves the
GPU needing a reset: the next health triangle faulted once or twice more before a plain triangle
drew (3 jobs, 3 recoveries, 0 stops of the script).

**What it does not show.** f = 4 against 5 (needs the size of the TA's header arrays: Q286); the
kernel fix; why the recovery reports -110 and still needs a reset.
