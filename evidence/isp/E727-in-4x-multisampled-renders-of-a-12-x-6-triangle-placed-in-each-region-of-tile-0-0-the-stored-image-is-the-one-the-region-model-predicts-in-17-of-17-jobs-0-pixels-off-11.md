+++
id = "E727"
claim = "In 4x multisampled renders of a 12 x 6 triangle placed in each region of tile (0, 0), the stored image is the one the region model predicts in 17 of 17 jobs (0 pixels off, 11 of 17 images empty), and the visibility counter 0x0498 is non-zero in the 7 non-control jobs whose stored image is empty (6 distinct jobs and a repeat, TE 0xe0, 0xa0, 0x60) but reads 0 with the same empty image in the 4 controls at TE 0x20, so the counter does not show that every region is walked [infer]"
unit = "isp"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
**What ran.** msaa-a-vis: 17 jobs (rc 1 on all, see below), a 64 x 64 render with a triangle of 12
x 6 pixels (vertices at 1/256 pixel) at the origin of one region of the first tile, CR_TE_AA
0xe0000000, 0xa0000000, 0x60000000 at mode 2 and 0xa0000000 at mode 1 (10 jobs, held out; 4
positions for 0xe0), the same triangle at TE 0x20000000 (6 controls), and one repeat of
v-m2-tee-x0y0. blk:2^=0x8 and --regs 0x0494 to 0x04b4 on every job.

**Hypotheses (frozen).** The region model, written from the words of the earlier report with integer
geometry (recompute/msaa_model.py): the set of pixels the stored image differs from the background
in. A decision rule frozen with it: a count at 0x0498 above 0 in an even region means W (the ISP
walks every region and the last overwrites), a count of 0 means S (skipped). The rule is a reading
of the counter, not a measurement of the walk (see What it shows).

**Results.** [HW] Stored pixels differing from the background against the model: 17 of 17 jobs
equal (0 off). Stored pixels: te2 controls 108, 0, 0, 0 (mode 2) and 57, 0 (mode 1); 0xe0: 0, 0,
0, 144; 0xa0 mode 2: 0, 144; 0x60: 0, 108; mode 1 0xa0: 0, 78; repeat 0. Counter 0x0498: 144 on
the four 0xe0 jobs and the repeat, 144 and 144 on 0xa0, 108 and 108 on 0x60, 78 and 78 on mode 1
0xa0, and in the controls 108, 0, 0, 0, 57, 0. The counter equals the stored pixel count in every
control and wherever the image is not empty. The 7 non-control jobs whose image is empty (the
triangle is not in the last region visited) read a non-zero counter: by the frozen rule W 7 of 7,
but the 7 are 6 distinct jobs plus the repeat of one of them (the repeat, count 144, image empty,
agrees with its twin). The controls at TE 0x20 with the triangle in a region that is not visited
(v-m2-te2-x16y0, -x0y8, -x16y8 and v-m1-te2-x16y0) read counter 0 with an empty image, S by the
same rule; the same geometry at 0xe0 reads 144 with an empty image.

**Return code.** All 17 are rc 1 with "diff: N of 4096 pixels" (12 to 156): the tool's own image
check against a plain triangle, run under --keep-going. Not a usage error (see E732).

**Population.** The model was fitted on A-m1-te60 tile (1, 2) of the msaa-ident set (E415) and
scored 108 of 108 on E415's data held out; these 17 are new triangles (12 x 6 at four region
origins, three TE settings, two modes) and confirm it (the image result stands). The decision rule
was declared before the run; its W reading is not confirmed by the data (see below).

**What it shows.** [HW] The model's images hold on a triangle small enough to sit in one region:
where the last region visited does not contain it the image is empty, and the counter reads 144,
108, 78 or 57 at TE 0xe0, 0xa0 and 0x60 but 0 at TE 0x20 for the same empty image. [infer] The
frozen W (every region is walked and the last overwrites) is one reading; it is not forced. The
counter's value depends on the TE bits (0 at 0x20, non-zero at 0x60 and above for an empty image),
so "count above 0 means walked" is a property of the counter in those settings, not of the walk.
144 = 4 x 36 (the 12 x 6 triangle is 36 pixels, mode 2 stores 2 x 2) and 108 = 3 x 36, 78 and 57
match the stored-sample count of the image the model predicts, so the counter may count samples
the TA stream produces for the 4x tile before the store window drops them (an alternative: a
stored-sample count), or be incremented before the store; these are not separated.

**What it does not show.** Whether every region is walked; the meaning of the counter's absolute
values (144 and 108 are not derived, see above), larger triangles that straddle regions, mode 0, the
128 x 128 target, E070's counter under 1x. The register read after a multisampled job returned
values, which the plan had listed as unvalidated.
