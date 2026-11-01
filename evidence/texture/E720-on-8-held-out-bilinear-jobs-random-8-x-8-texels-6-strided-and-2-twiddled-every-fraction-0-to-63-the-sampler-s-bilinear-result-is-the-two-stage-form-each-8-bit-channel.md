+++
id = "E720"
claim = "On 8 held-out bilinear jobs (random 8 x 8 texels, 6 strided and 2 twiddled, every fraction 0 to 63) the sampler's bilinear result is the two-stage form, each 8-bit channel lerped in x then in y, with +32 and a 6-bit shift at each stage (weights on the 1/64 grid of these jobs; weight precision is not tested here): 8 of 8 jobs exact over their 2048 pixels (16384 of 16384), against 0 of 8 for the joint (sum + 2048) >> 12 form, the y-then-x order and the rounded-down variant (and 0 of 8 for stage roundings +32/+0, +0/+32, +31, +33 and mixed)"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["T0.MINFILTER"]
+++
**What ran.** tex-b-bilin: 8 fills of 64 x 32 pixels (bl-st11-lo, bl-st11-hi, bl-st12-lo, bl-
st12-hi, bl-st13-lo, bl-st13-hi on a strided 8 x 8 texture, bl-tw14-lo and bl-tw15-lo on a
twiddled one), the texel dwords injected from random seeds 11 to 15, u = 0.125 (1 + p / 64) + 0.25
over the 64 columns so every x weight 0 to 63 occurs, v on a row band per job (the "lo" and "hi"
bands, half the y weights each); T0 bits 12 and 10 set (bilinear). All 8 are rc 0, all 2048 pixels
read. The 8 jobs were declared held-out (set "heldout" in declared.tsv); nothing in them was used
to choose the form.

**Hypotheses, frozen by sha256 in predictions-declared.tsv.** joint: per channel (sum of the four
texels times the products of the weights in 1/64, + 2048) >> 12. two-stage xy: fx and fy =
trunc(64 frac); top = (a (64 - fx) + b fx + 32) >> 6 and bot likewise, then (top (64 - fy) + bot
fy + 32) >> 6, per 8-bit channel. two-stage yx: y first. xy floor: as xy without the + 32.

**Results.** [HW] pixels exact (of 2048) per job: two-stage xy 2048 on all 8 jobs. joint 804 to
935 (39% to 46%), yx 609 to 800, xy floor 1 to 7. Criterion of plan.md (two-stage xy or yx on at
least 7 of 8 and joint on 0): passed, 8 of 8 and 0 of 8.

**Population.** The two-stage form was fitted by a search over 45 forms on 6 jobs of the earlier
11.32 data (an-ctl, an-r1 to an-r5, in sample; plan.md section 1.2). Those 6 never distinguished
it from the joint form on a population in which they differ, and the 21 landed smp-bilinear
vectors (16 x 32 strided, F32 output) are 21 of 21 under both forms (offline, plan.md section
1.3). These 8 jobs are the first data in which the forms differ: the fit is now confirmed held
out.

**Weight precision.** The jobs do not test it. The pixel fractions are exact multiples of 1/64
in x (u steps of 2^-6 of a texel) and of 1/16 in y (5/64 steps in the hi band), so weights of
precision 64, 128 and 256 give identical images (2048 of 2048 on 6 of 6 strided jobs under each).
The truncation of the weight to 1/64 rests on the 21 landed vectors (finer weights fail 8 and 15
of them, per the review) and the 11.32 jobs, not on these 8. The y weights occupy half of 0 to 63
per job. Order
and rounding are separated cleanly (a reviewer's own sampler: joint 804 to 935, yx 609 to 800, xy
floor 1 to 7, +32/+0 130 to 187, +0/+32 68 to 183, +31/+31 1351 to 1631, +33/+33 1906 to 1972,
+32/+33 1975 to 1999 of 2048).

**What it shows.** [HW] On 8-bit four-channel texels with weights on the 1/64 grid the bilinear
result is two rounded lerps (+32, >> 6 at each stage), x first. [infer] The weight is the
fraction truncated to 1/64 per axis, as the landed vectors and 11.32 established; these jobs
are consistent with it and do not test it. [infer] The landed vectors could not tell
the joint form from this one (both predict the same words on all 21); these jobs can, and the
simulator's joint form (tex.rs filtered) is the one they refute.

**What it does not show.** Texels of other formats (only 8-bit channels were injected), twiddled
textures beyond 8 x 8, a bilinear sample across mip levels (the trilinear mix is E563's),
anisotropy (Q115), the sRGB bit (E723: neither order of decode and filter fits).
