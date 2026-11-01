+++
id = "E725"
claim = "Textures of type 3 and type 1 are read with a stride of the texture's width and the window wrapping at its size (8 of 8 held-out fills exact over 2048 pixels, 8 x 8 to 32 x 32), not the fixed 16 of E567's reading (0 of 8); type 4 is read with a fixed stride of 32 (4 of 4 sizes exact after the fact), which none of the three frozen hypotheses gives"
unit = "texture"
method = "on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed and loaded), firmware /lib/firmware/sgx545_ukernel.fw sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-1138b sha256 ba6baa62fe33a5aa510c05ea1aa9a04c25798c60c4954655882682f05a5b8291, the 13 scripts of p1141/tex run in one pass by run-all-1141tex.sh on 2026-11-09 (14:25 to 14:31; 140 jobs, one process per job, a marker per job in the kernel log, every raw output gzipped and kept); declared.tsv, predictions-declared.tsv (380 rows) and manifest-1141tex.sha256 written before the first job (file times 14:16 to 14:20, first job 14:25:01) and verified here by sha256 (5dae7939..., f4187d25..., 144da32e...; 27 of 28 manifest lines by sha256sum -c, the 28th, the 74 staged programs, by the sha256 of sha256sum stage-bins/*.bin); recompute/recompute_p1141tex.py (numpy, scratch, shares no code with the run scripts) run on the dumps, its output in recompute-output.txt. Post hoc and not frozen: post/post_1141tex.py with post-output.txt"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-isp-msaa-verification-1141"]
terms = ["TEXTYPE"]
+++
**What ran.** tex-f-types: type 3 at 8 x 8, 32 x 32, 32 x 16 and 16 x 32 (4 jobs, plan: low risk).
tex-g-types-risky: type 1 and type 4 at the same four sizes (8 jobs). Each a 64 x 32 fill of the
map texture (a tag 0xD0000000 plus the dword index in every texel), repeat addressing, a window of
w x h cycling over the 64 columns and 32 rows; declared held-out. All 12 rc 0. The run order put
the 8 risky jobs last; none faulted.

**Hypotheses (frozen).** "fixed 16": a 16 x 16 window of stride 16 (32 for type 4), wrapping at 16
(the reading of E567 at 16 x 16); "raster w": index y w + x on the w x h window, stride 2 w for
type 4; "raster 16 wrap": index ((y mod h) mod 16) w + ((x mod w) mod 16), stride w (2 w for type
4) with the wrap at 16. Pass criterion: one hypothesis exact on each type's four sizes; "fixed 16"
expected.

**Results.** [HW] Exact pixels of 2048, type 3 (8 x 8, 32 x 32, 32 x 16, 16 x 32): fixed 16 256,
32, 64, 1024; raster w 2048 on all four; raster 16 wrap 2048 on 8 x 8 only. Type 1: the same
numbers. Type 4: fixed 16 2048 on 8 x 8 only and 512, 1024, 1024 on the others; raster w 256, 64,
128, 2048 (16 x 32 only). Criterion: type 3 and type 1 pass with "raster w" (4 of 4 each), type 4
passes with none; the expected "fixed 16" is 0 of 8 on types 3 and 1 and 1 of 4 on type 4.

**Post hoc, not frozen (post/post_1141tex.py, section types).** [fitted] On all 12 jobs the tag is
(y mod h) S + (x mod w) with S = w for types 1 and 3 and S = 32 for type 4, 2048 of 2048 on each:
for type 4 the stride in dwords is 32 at 8, 16 and 32 wide, not 2 w (64 at 32 wide). The first
row's x step is 1 and the y step is S in every job.

**Population.** Type 1 and 3 "stride w": held out, confirmed on 8 of 8 (4 sizes each). Type 4
"stride 32": fitted on the 4 jobs that show it, plus E567's 16 x 16 case, where 32 and 2 w
coincide; it is not held out and stays [fitted] until another size (a width of 64 or 128, or 4)
runs.

**What it shows.** [HW] Types 3 and 1 index a texture as a raster of w dwords per row at 8 to 32
wide; the "fixed 16" of E567 was the 16 x 16 case of this. [fitted] Type 4's row is 32 dwords
whatever the width at 8 to 32 wide.

**What it does not show.** Widths above 32 or below 8, heights other than 8 to 32, non-power-of-
two widths, type 5, and whether type 4's 32 is a property of the type or of the 64-column window.
