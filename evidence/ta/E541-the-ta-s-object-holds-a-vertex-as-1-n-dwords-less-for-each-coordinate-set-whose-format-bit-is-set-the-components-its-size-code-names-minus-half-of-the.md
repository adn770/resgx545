+++
id = "E541"
claim = "The TA's object holds a vertex as 1 + N dwords less, for each coordinate set whose format bit is set, the components its size code names minus half of them rounded up (1, 2, 3, 3 and 4 components for codes 1 to 5): that rule gives the stored dwords of 12 of 12 held-out jobs, the format word's bits 15:8 are 1 + N and the four set masks follow the size and format words in 56 of 56 completed jobs; in the `alt` pattern 3 of 7 jobs did not complete (N = 2 faulted, N = 3 and 8 hung), and a set described past the outputs the vertex program writes does not decide it"
unit = "ta"
method = "script tables ta-object-format (47 jobs) and ta-object-format2 (12 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri pixpds:12` with a vertex program of N coordinate outputs (N = 2 to 11, the outputs o4 and o5 the vertex's clip x and y, the rest constants), the coordinate size word (blk:16, 3 bits a set) and the format word (blk:17, one bit a set) set per case, the TA's first object read from the dumps by recompute_p1131.py (its own decoder of doc/specs/3d.md 10.1); sets and predictions declared and hashed before the runs (analysis/plan.md sections 1 and 6, declared files); one run each"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-object-format"]
terms = ["PB_OBJ.FORMAT", "PB_OBJ.SET_MASKS", "PB_OBJ.PDS_WORDS"]
+++

**What ran.** ta-object-format: 47 jobs, 5 fit (E308's settings: N = 4, size words 1, 3, 5, 5 with
format 1, 18 with format 3) and 42 held out (N = 2, 3, 5, 6, 8, 9, 11, each with six size and format
patterns: at N = 2 and 3 the `mix` pattern has the settings of `s1`, so those N have five distinct
patterns and the 42 jobs 40 distinct settings); 44 completed and 3 did not (below).
ta-object-format2: 12 jobs, declared after the first run and before it ran (plan.md section 6), all
completed.

**The format word and the masks.** [HW] In 56 of 56 completed jobs the format word is 0x0004 in bits
31:16 and the format byte in bits 15:8 is 1 + N (the 1/w and the N coordinate outputs, iterated);
bits 31:19 and 17:16 were never other than clear and bit 18 never clear. The four set masks followed
one rule in 56 of 56 (the recompute's own formula, not a declared prediction for the
ta-object-format2 jobs): with the sets numbered from 1, mask word 0 has bit i + 1 for each set i
whose format bit is set, mask 1 for size code 1, mask 2 for codes 3 and 5, mask 3 for codes 4 and 5;
a set is counted when its size code is not 0 or its format bit is set. The declared H70-M (the same
rule) was right in 5 of 5 fit and 39 of 39 completed held-out jobs of the first run.

**The stored dwords.** [HW] The first declared rule (H70-F: a flagged set of up to four outputs
stores half of them rounded up, 1 + sum of the sets) was right in 5 of 5 fit and 34 of the 42
held-out jobs: 5 stored wrong (N = 6, 8, 9, 11 with every set at size code 2 and format bits set: 5
against 4, 7 against 5, 7 against 6, 9 against 7; N = 11 with the sizes 5, 3, 1: 10 against 9) and 3
jobs did not complete. The dumps show why: in the N = 8 job the vertex holds 1/w, one dword of two
half-precision values (x, y), one of two (the third and fourth outputs), then the remaining four
outputs raw at full precision. The sets take the outputs in order and each takes only the components
its size code names; a flagged set packs those into ceil(c / 2) dwords. The component counts of the
size codes 1 to 5, 1, 2, 3, 3 and 4, are measured for codes 1, 2 and 5 in the first run and for
codes 3 and 4 in ta-object-format2 (below); [infer] the naming (x; xy; xyz; xyw; xyzw). That rule
(H70-F2: stored = 1 + N - sum over flagged sets of c - ceil(c / 2)) was written from the first run's
42 held-out jobs and declared before the 12 jobs of ta-object-format2, whose size codes 3 and 4 it
had not seen: 12 of 12 stored and iterated dwords as declared (N = 4 with one flagged set of each
code 1 to 5: 5, 4, 4, 4, 3; N = 8 with two flagged sets of codes (3, 4), (5, 5), (1, 5) and one
flagged of (5, 2): 7, 5, 7, 8; N = 11 with (2, 3, 5), (1, 1, 1) and (2, 2, 2) with sets 0 and 2
flagged: 8, 12, 10).

**What did not complete.** [HW] Three of the seven jobs of the `alt` pattern (size codes 5, 3 and 1
over the sets, the format bits of sets 0 and 2, or of set 0 alone when there is one set: at N = 2
and 3 a single set of code 5 with its format bit): N = 2 faulted, N = 3 and N = 8 hung; at N = 5, 6,
9 and 11 they completed. A set described past the outputs does not sort them: at N = 5 and 6 the
sets describe 4 + 3 components over 5 and 6 outputs and completed, at N = 8 (4 + 3 over 8) a job
hung, and the single set of code 5 over 2 and 3 outputs without a format bit (n2-s5, n3-s5)
completed; Q165.

**What it does not show.** Size codes 6 and 7 of the 3-bit field; any format bit other than bit 18
(the vertex colour's bit 19 is not in these jobs); who reads the format word (the 3D or the ISP);
the packed block at the end of the object.
