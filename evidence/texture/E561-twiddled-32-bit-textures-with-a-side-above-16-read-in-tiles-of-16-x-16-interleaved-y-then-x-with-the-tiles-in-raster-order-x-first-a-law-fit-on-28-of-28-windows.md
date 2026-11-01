+++
id = "E561"
claim = "In 28 windows of 64 by 32 texels over twiddled level-0 textures of 32-bit texels, 16x16, 32x32, 64x32, 64x16, 64x64, 128x16, 128x32, 32x128, 128x128, 16x64 and 8x128, the index of texel (X, Y) is the plain interleave (Y in bit 0, X in bit 1, and so on) only up to 16 on each side: 32x32, 64x32, 64x64, 128x32, 32x128 and 128x128 do not read plain Morton (D1: 512 of 1024 texels plain at 32x32, 512 of 2048 at 64x32, 512 of 4096 at 64x64, 512 of 4096 at 128x32, 2048 of 4096 at 32x128, 1024 of 16384 at 128x128) while 16x16, 16x64, 64x16, 128x16 and 8x128 do (all texels); one law fits every size, fit on all 28 windows after the run: tiles of up to 16x16 texels interleaved as before (the whole texture when it is smaller) and the tiles in raster order with x first (32x32: i8 = x4, i9 = y4; 64x32: i8 = x4, i9 = x5, i10 = y4; 128x128: i8 to i10 = x4 to x6, i11 to i13 = y4 to y6), exact on 28 of 28 jobs (the 16384 texels of 128x128 included), and it gives the dwords of E441's levels 0 to 2 (the texel (28, 84) at 128 wide, (14, 42) at 64 and (7, 21) at 32 read 0x29b0, 0x8ec and 0x23b, the plain indices of E441's decoded pairs (20, 108), (10, 46) and (5, 23), 3 of 3; E441's data were not used in the fit); the declared prediction (plain Morton at every size) held for the 16x16 control, 1 of 3 fit sizes (64x16; 32x32 and 64x32 failed) and 8 of 24 held-out jobs, and the 32x32 control of the shapes group (shp-32x32-l0) failed under all three declared hypotheses for the same reason"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Group twiddle, 28 jobs, windows of up to 8 jobs a size; the tile law was found from D1's GF(2) fit of each index bit on the 28 dumps after the run and then checked against the same 28, so for the 28 windows it is a fit, not a held-out test; E441's three levels are a check outside the fit, made after the law was found"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-p1132-tx-twiddle", "texture-p1132-tx-shapes", "texture-p1132-recomp", "vectors-texture-p1132"]
terms = ["T0.BITS26_21"]
+++

**Results.** [HW] Per size D1 (texels seen, plain Morton, affine fit): 8x128 1024/1024; 16x16
256/256; 16x64 1024/1024; 64x16 1024/1024; 128x16 2048/2048; 32x32 1024/512 (i0..i7 as plain, i8 =
x4, i9 = y4); 32x128 4096/2048; 64x32 2048/512; 64x64 4096/512; 128x32 4096/512; 128x128 16384/1024.
Every index bit is an exclusive-or of one coordinate bit (no dependence on two). E441's levels 0 to
2 of its 128x128 chain did not read where plain twiddling puts the texel; its decoded pairs are (v,
u) for the texels (28, 84), (14, 42) and (7, 21), and the tile law puts those texels at the dwords
the plain interleave gives for the pairs read as (x, y) = (108, 20), (46, 10) and (23, 5): 3 of 3;
its levels 3 to 7 (16 on a side and below) are plain, as the law says.

**Predictions.** The declared hypothesis (plain Morton at every size) was falsified at 32x32, 64x32,
64x64, 128x32, 32x128 and 128x128.

**What the simulator adds.** It replays the 28 windows' vectors exactly with the law. Of the 64
shapes and 44 fields vectors only one job, shp-32x32-l0 (level 0 of the 32x32 control), has a
geometry on which the law and plain Morton differ (every other level has a side of 16 or less,
where both agree), so those vectors add no test of the law.

**Inference.** [infer] That the index is a function of tiles, and not another function that agrees
on these 28 windows, rests on the fit: every index bit is a function of one coordinate bit (D1) and
the tile law is such a function.

**Not shown.** Sizes with a side of 8 or less against a long other side beyond 8x128, 256 or more
on a side, and texels of other sizes than 32 bits (not run). The simulator refuses all of them.
