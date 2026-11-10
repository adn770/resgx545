+++
id = "E790"
claim = "R2-geo stages g-c3 and g-c2 (E785, E786), the frozen side table of dword 36 of the TA/3D control block against the page count of CR_DPM_GLOBAL_PAGE_STATUS (0x072c, low half) in the sample before the first abort (prediction: max(count - 2, 0)), never gating: of the 15 jobs with a first abort the register reading held in 8, unraised jobs 5 of 8 (g-c3 2 of 3, g-c2 3 of 5) and raised jobs 3 of 7 (1 of 3 and 2 of 4; the raised jobs of the two stages were held out), the misses being c3-4096-0x372 (count 3, dword 36 3), c3-2048-0x122 (4, 3), c3-2048-0xa2 (2, 2: predicted 0, read 2), k-1500-0x33e (3, 3), k-1500-0x351 (3, 3), k-1500-0x3a0 (4, 3) and k-1500-0x3de (4, 3); read after the run [infer, a check of E775's post hoc reading, not frozen], the maximum of the 0x072c count over the job less 2 equalled dword 36 in 13 of these 15 jobs and failed in two raised ones, c3-2048-0xe2 (peak 4, dword 36 1) and k-1500-0x300 (peak 4, dword 36 1), and in the 5 jobs of g-c3 that never overflowed (peak count 7, dword 36 0) it does not apply"
unit = "dpm"
method = "R2-geo stages g-c3 (11 jobs, 6 with a first abort) and g-c2 (9 jobs, all with one), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053), regtimeline reading 0x0720-0x072c in every job (the gate had passed in R1); the count is the low half of 0x072c in the timeline sample just before the first rising edge of 0x0658 bit 0, dword 36 and the raise read from the control block after the job (buf09); the side table is the frozen reader of score/score_r2.py (out/score-g-c3.txt, out/score-g-c2.txt: `D36 unraised 2/3, raised 1/3` and `D36 unraised 3/5, raised 2/4`); the peak column was computed after the run with a scratch reader over the same kept timelines (the maximum of 0x072c's low half over all samples of a job), a reading E775 made over R1's jobs and had no frozen row for; the 'raised' label is the control block's dword 38 = 0x20"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-c3/", "render-closing-r2-geo:out/g-c2/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl"]
+++
**What ran.** E775 scored the register reading of dword 36 (the 0x072c count at the first abort,
less 2) on R1's jobs and found it failing on the raised ones (0 of 14), and read afterwards that the
job's peak count less 2 fits all 23. The R2-geo stages sampled 0x072c in 15 more jobs with a first
abort (and 5 without one) and carry the same side table in the scorer, so the reading meets jobs
it was not fitted to.

**Frozen verdicts (side tables, as printed).** g-c3: `D36: unraised jobs 2 of 3; raised jobs (held
out) 1 of 3`; g-c2: `D36: unraised jobs 3 of 5; raised jobs (held out) 2 of 4`. The side table
never gated a verdict.

**Results [HW].** Per job, with a first abort: the count before it, the job's peak count, dword 36,
and the raise:

| job | count at first abort | peak | dword 36 | raise |
|---|---|---|---|---|
| c3-4096-0x372 | 3 | 5 | 3 | raised |
| c3-4096-0x374 | 3 | 3 | 1 | none |
| c3-2048-0x162 | 5 | 5 | 3 | none (void for the raise) |
| c3-2048-0x122 | 4 | 5 | 3 | none |
| c3-2048-0xe2 | 3 | 4 | 1 | raised |
| c3-2048-0xa2 | 2 | 4 | 2 | raised |
| k-tri-0x80 | 1 | 1 | 0 | raised |
| k-tri-0x100 | 1 | 1 | 0 | none |
| k-1500-0x300 | 3 | 4 | 1 | raised |
| k-1500-0x33e | 3 | 5 | 3 | raised |
| k-1500-0x351 | 3 | 5 | 3 | raised |
| k-1500-0x352 | 3 | 3 | 1 | none |
| k-1500-0x35e | 4 | 4 | 2 | none |
| k-1500-0x3a0 | 4 | 5 | 3 | none |
| k-1500-0x3de | 4 | 5 | 3 | none |

The five 2048x2048 jobs that never overflowed (c3-2048-cal and P = 0x354, 0x372, 0x374 and 0x394)
had a peak count of 7 and dword 36 = 0.

**What it shows and does not.** The register reading (count at the first abort less 2) fails again
on the raised jobs, 4 of 7 here (14 of 14 in R1; the count at the first abort is 1 to 3 in the
raised jobs here and dword 36 reads 0 to 3), and on 3 of 8 unraised ones. The reading E775 made
after R1's data, the peak less 2, holds in 13 of these 15 jobs and fails in two raised jobs where
dword 36 is one lower than the peak says (1 where it says 2): it is not a rule, and the data do not
say which quantity the firmware reads. It does not apply to jobs without an abort (peak 7, dword 36
0). Raised jobs read dword 36 = 3 in 3 of 7 (c3-4096-0x372, k-1500-0x33e and 0x351) and 0, 1 or 2 in
the rest; no function of P, the vertex count or the raised threshold is read. What steps dword 36
stays open (Q273).
