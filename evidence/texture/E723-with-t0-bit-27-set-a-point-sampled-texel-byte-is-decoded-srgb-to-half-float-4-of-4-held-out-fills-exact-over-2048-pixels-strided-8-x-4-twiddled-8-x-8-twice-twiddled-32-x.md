+++
id = "E723"
claim = "With T0 bit 27 set a point-sampled texel byte is decoded sRGB to half float: 4 of 4 held-out fills exact over 2048 pixels (strided 8 x 4, twiddled 8 x 8 twice, twiddled 32 x 32); on 2 held-out bilinear fills neither frozen order fits, filter then decode 0 and 0 of 2048 pixels and decode then filter 1147 and 876"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["T0.BIT27"]
+++
**What ran.** tex-d-t0b27: 8 fills. g-st8x4, g-tw8x8, g-tw8x8-s2 and g-tw32x32 with T0 bit 27 set
and the texel bytes injected (stratified over 0 to 255 for 3 of them; the 32 x 32 the default
data), point sampling; g-bl-st-a and g-bl-st-b the same on a strided 8 x 8 texture with bilinear
filtering and random injected bytes (the two jobs of the plan that "decide between the two or
refute both"); g-st8x4-r11 and g-tw8x8-r11 explorations that read the second output dword
(tx_map_r11.s, a new template), declared without a prediction. All 8 rc 0, 2048 pixels each.

**Hypotheses (frozen).** srgb to half: the dword for a texel is half(s2l(byte 1)) in the upper
half and half(s2l(byte 0)) in the lower half, s2l the sRGB transfer function, nearest-even half.
Bilinear: filter then decode = the two-stage lerp of E720 on bytes, then decode; decode then
filter = decode each texel to float, filter with the 1/64 weights, then convert to half.

**Results.** [HW] srgb to half: 4 of 4 jobs, every pixel (8192 of 8192). Filter then decode: 0 of
2048 on both bilinear jobs. Decode then filter: 1147 of 2048 on g-bl-st-a, 876 on g-bl-st-b.
Neither is exact, so the pair refutes both frozen orders (the plan's own outcome, "or refutes
both"). The two r11 jobs read 32 and 64 distinct values (1653 of 2048 pixels equal in the first);
no model, not interpreted.

**Population.** T0 bit 27 as sRGB to half was fitted on s64x32 and ab-t43 (2 jobs, in sample);
these 4 point-sampled jobs are held out and confirm it. The bilinear question is new (an-t0b27 was
25 pixels off for either order in the 11.32 data).

**What it shows.** [HW] For a point sample, T0 bit 27 decodes the texel bytes to half floats by
the sRGB curve, on strided and twiddled textures. [HW] The filter of an sRGB texel is not "filter
the bytes, decode" (0 pixels) and not exactly "decode, filter in float, convert": the second fits
43% to 56% of the pixels, so the order is probably decode first but the filter's arithmetic (the
weight, the rounding, a fixed-point intermediate) is not that of E720's lerp on floats (Q282).

**What it does not show.** The bilinear arithmetic after the decode; the r11 reads; any format
other than the one these jobs read (two 8-bit channels per texel).
