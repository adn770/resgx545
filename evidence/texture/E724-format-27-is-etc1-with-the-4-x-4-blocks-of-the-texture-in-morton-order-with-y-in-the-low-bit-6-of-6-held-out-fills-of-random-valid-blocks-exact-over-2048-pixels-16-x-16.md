+++
id = "E724"
claim = "Format 27 is ETC1 with the 4 x 4 blocks of the texture in Morton order with y in the low bit: 6 of 6 held-out fills of random valid blocks exact over 2048 pixels (16 x 16 twice, 32 x 16, 16 x 32, 8 x 16, 8 x 8), against 0 of 6 for raster block order and 0 of 6 for Morton with x low"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["TEXFORMAT"]
+++
**What ran.** tex-e-etc1: 6 fills (e16a, e16b, e32x16, e16x32, e8x16, e8x8), random block pairs of
dwords (seeds 31 to 36; gen/cat1141.py etc_blocks keeps the differential blocks inside the colour
range), format 27, repeat addressing; declared held-out. All 6 rc 0, 2048 pixels each.

**Hypotheses (frozen).** The decode of the model (recompute/tex2.py etc1_block): the pixel of
block bit i at (i div 4, i mod 4) as E568 found, the modifier table of ETC1, flip and diff bits;
the order of the blocks of a texture: Morton with y in the low bit, raster, Morton with x in the
low bit. On 32 x 16 and 16 x 32 the three orders differ in at least 1024 pixels; on 8 x 16 and 8 x
8 raster and x-low agree on 1024 of 2048 pixels each.

**Results.** [HW] Morton y-low exact (all 2048 pixels) on 6 of 6. Raster: 256, 256, 256, 264,
1024, 1024 of 2048. Morton x-low: 512, 512, 512, 520, 1024, 1024.

**Population.** The order was fitted on fb-27-base, ordA, ordB (3 jobs); these 6 are held out with
new block data and new sizes and confirm it.

**What it shows.** [HW] Texture format 27 decodes as ETC1 (Q179's question for 27 is answered:
yes), the blocks of a 16 x 16 or 32 x 16 texture in the Morton order of the block grid with y in
the low bit. The output is colour in the order the model uses (the images are exact, so the
channel order and the 4 x 4 pixel map are those of the model).

**What it does not show.** Textures above 32 wide or tall (whether the tile law of E561 rewrites
the block order there), ETC1 with mip levels, filtering, alpha; formats 23 to 26 (PVRTC, not run:
Q179 stays open for them).
