+++
id = "E721"
claim = "On 8 held-out gradient jobs with independent operands the footprint of E563's smp2dgrad is, to within 0.1% and fitted with a residual, the larger of the two Euclidean lengths of the vectors (op0, op2) and (op1, op3) scaled by the level size (the best of six declared footprints): it has the highest count on 8 of 8 jobs with 1992 to 2048 of 2048 pixels (4 jobs exact, residuals 19 to 56 pixels on the others, whole columns or rows) against at most 256 for the five other footprints, and the LOD fraction is truncated to 1/64: 2016 to 2048 of 2048 on 8 of 8 ladders against 1160 to 1840 for rounding"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["T0.MIPFILTER"]
+++
**What ran.** tex-a-lod: 16 fills. Eight gradient jobs: lg-sq1 to lg-sq4 on a 64 x 64 twiddled
chain and lg-ns1 to lg-ns4 on 128 x 32 (so the u and v scales differ), the four gradient operands
op0 to op3 each a different ramp (xj = 2^-j (1 + p / 64) along x, yj along y, cj = 2^-j constant,
j = 6 to 9; the sets in gen/cat1141.py), no two operands of a job equal. Eight ladders lf-r2, r3,
r4, r6, r8, r12, r16, r24: one operand ramped from rho = r to 1.0615 r over the 64 columns, so the
fraction changes where truncation and rounding place it differently. All 16 rc 0, 2048 pixels
each. All 16 were declared held-out.

**Hypotheses (frozen).** Footprints, each with the log2 and the 1/64 truncated fraction of the
E563 model: P = max(hypot(op0 W, op2 H), hypot(op1 W, op3 H)), the vectors being the pairs (0,2)
and (1,3) of the program's operands; O = the pairs of E563's order, (0,1) and (2,3); Mp and Mo =
the largest scaled component under the two pairings; F = sqrt((sum of the four scaled squares) /
2); S = the larger of |op0| W + |op2| H and |op1| W + |op3| H. Any two footprints differ in at
least 1972 pixels on the 64 x 64 jobs and 1792 on the 128 x 32 jobs (Mp = Mo on the squares). The
ladders: frac=trunc against frac=round on footprint P.

**Results.** [HW] Pixels exact of 2048, footprint P: lg-sq1 2002, lg-sq2 1992, lg-sq3 2048, lg-sq4
2048, lg-ns1 2029, lg-ns2 1995, lg-ns3 2048, lg-ns4 2048. Best of the five others per job: O 51, O
8, O 44, O/Mp/Mo 8, O 61, 0, Mp 136, Mp 256. Criterion of plan.md (P has the highest count and at
least 1980 on every job): passed 8 of 8. The frozen sha256 (all 2048 pixels equal) holds on 4 of 8
jobs; the other 4 miss by 46, 56, 19 and 53 pixels (the residual of the in-sample 11.32 jobs was 8
to 65). Ladders, frac=trunc: 2032, 2016, 2016, 2028, 2040, 2024, 2032, 2048; frac=round: 1298,
1258, 1388, 1296, 1448, 1160, 1664, 1840. Criterion (one of the two at least 1980 on 7 of 8 and
the other not): trunc 8 of 8, rounding 0 of 8. The sha256 of trunc holds on 1 of 8 (lf-r24).

**Population.** The pairing (0,2), (1,3) and the Euclidean length came from E563's jobs after the
partition was read from the vectors (gr-uu, gr-vv, gr-uvy, gr-all, gr-vx, ...: in sample); these
16 jobs are held out and confirm the pairing and the truncation at the criterion of the plan. The
rule is not exact: 4 of 8 gradient jobs and 1 of 8 ladders reproduce every pixel, and the residual
is of the same size (up to 56 pixels, 2.7%) as in sample, so the footprint stays a fitted rule
with an unexplained residual (Q280), not a closed one.

**Residual (reviewer's re-render of P against the raw jobs).** The misses are whole columns or
rows, not scattered pixels: lg-sq1 46 pixels = columns 9 and 36 (rows 0 to 31), lg-sq2 56 = row 23,
lg-ns2 53 = columns 41 and 53, lg-ns1 19 scattered. A scale epsilon on the footprint (0.02% to
0.8%) improves one job and breaks others; at 0.1% the counts fall to 1830 to 2016. So the rule is
right to better than 0.1% but not exact: the error is a boundary shift of one column or row where
the LOD fraction crosses a 1/64 step. Length approximations (max + k min) and an approximate log2
were not among the declared alternatives, so "Euclidean" is the best of six, not established
against them; the 1980 criterion separates the six (next best 256) but is lenient against
exactness.

**What it shows.** [HW] The operand order matters as the pairs (0,2) and (1,3): E563's order (O)
scores at most 61 pixels on four independent sets. The fraction of the LOD is truncated, not
rounded, to 1/64 (ladders). The maximum-component, root-mean-square and sum footprints are refuted
(at most 256 pixels).

**What it does not show.** Why up to 56 pixels per job miss (a rounding of the length, of the
log2, or a footprint that is not exactly Euclidean near a tie); anisotropy; quads whose own
derivatives are used (lod-auto, E563's au jobs); non-power-of-two level sizes.
