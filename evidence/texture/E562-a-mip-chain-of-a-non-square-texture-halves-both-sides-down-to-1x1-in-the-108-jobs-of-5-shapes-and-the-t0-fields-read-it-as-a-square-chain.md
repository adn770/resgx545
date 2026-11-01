+++
id = "E562"
claim = "On non-square twiddled textures (32x16, 128x16, 16x32, 64x4, 8x64; 32x32 as the square) the level read at a whole LOD is level l of a chain whose sides halve to 1 each (levels of max(1, w >> l) by max(1, h >> l) texels back to back, the last level 1x1, LOD above it clamping there), hypothesis chain=A: 8 of 8 fit jobs and 49 of 49 held-out jobs exact (7 control jobs: 6 exact under all three, the 32x32 window failed for E561's reason) (chain=B, the chain stopping at the short side's 1: 5 of 8 and 26 of 49; chain=D, square-padded levels: 1 of 8 and 6 of 49); the T0 fields on 32x16 and 128x16 (maximum 8 values, bias 7, MIPFILTER 7 fractions, 44 jobs) read it under chain=A as they read a square chain, 22 of 22 fit and 22 of 22 held-out exact (B 18 and 14, D 5 and 3); the 32x32 control failed under all three because of the tile law of E561"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Groups shapes (64 jobs: T0 0x07fc0000, smp2dreplace at LOD 0 to 7 or 8, window the whole of level 0, two jobs for 128 wide or 64 high) and fields (44 jobs)"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1132-tx-shapes", "texture-p1132-tx-fields"]
terms = ["T0.MAX_LEVEL", "T0.BITS26_21", "T0.MIPFILTER"]
+++

**Results.** [HW] D2, dword range read per LOD, equal to chain A in every shape: 32x16 0..511,
512..639, 640..671, 672..679, 680..681, 682 (LOD 5, 6 and 7 all 682); 128x16 to 2734 (LOD 7 and 8);
16x32 to 682 (LOD 5 and 6); 64x4 to 350 (LOD 6 and 7); 8x64 to 686 (LOD 6 and 7); 32x32 to 1364
(LOD 5 and 6).

**Predictions.** The declared chain=A held 8 of 8 fit, 49 of 49 held out, 22 of 22 and 22 of 22 for
the fields; chain=B and chain=D were falsified. The held-out jobs are held out (A was declared and
only 32x16 was fit), but 23 of the 49 are jobs on which B differs from A (B 26 of 49), and every
shape has a short side of 16 or less (4 to 16; the 32x32 control, whose window failed for E561's
reason, is the one with 32): the chain rule is measured on short sides of 4 to 16, on 32-bit
twiddled textures, at whole LODs by smp2dreplace and, in the fields, on 32x16 and 128x16 only.

**Not shown.** 1D textures (no case), a texture with a side of 1 at level 0, other formats than 32
bits in a chain, chains of 64x64 and above in a non-square shape. The simulator reads a non-square
chain at these five sizes only.
