+++
id = "E563"
claim = "In 45 gradient and quad-derivative jobs of 64x64 chains read at a LOD between levels, the LOD read per pixel is a logarithm of a footprint (pwl_max4 and pwl_euc, exponent plus linear mantissa: 0 of 14 fit and 0 of 7 held-out gradient jobs exact, against 2016 to 2048 of 2048 pixels for max4 (a logarithm) on the diagonal cases at k = 2 to 5), but the footprint is neither declared rule on every case: with the gradients given as dudx, dvdx, dudy, dvdy, on these cases max4 (largest component) is exact on 2016 to 2048 of 2048 pixels where only dudx and dvdx are set (gr-vx-k2 2016, gr-vx-k4 2048; euc 8 and 0), euc (the larger of the two vectors' lengths) is exact where all four are set (gr-all-k2 2024, gr-all-k4 2048, gr-neg-k2 2024; max4 8, 0 and 8) and for the quad's own derivatives with a v component (au-vx 2048, au-vy 2048, au-vx4 2048; max4 0, 0 and 128), and no declared rule is exact on the two-u-term, two-v-term and u-with-dudy jobs (gr-uu-k2, gr-vv-k2 at most 8 of 2048, gr-uvy-k2 52); this partition was read from the vectors after the run and was not declared or held out (held-out exacts: euc 1 of 7); the declared hypotheses scored: gradients fit euc 2 of 14, max4 2 of 14, min 1 of 14, pwl 0 of 14, held out 1 of 7 for euc, max4 and min, 0 of 7 for pwl; automatic LOD fit euc 5 of 7, max4, min, pwl_max4 and pwl_euc 4 of 7, held out euc 13 of 17, max4 11 of 17, pwl 11 of 17, min 4 of 17; on the diagonal ladder the fraction of the logarithm in 1/64 is truncated everywhere the columns tell (gr-diag-k2 2036, k3 2016, k4 2032 and k5 2048 of 2048 exact under truncation, against 1524, 1520, 1856 and 2048 when rounding to nearest), the one exception being the column x = 5 of k2, k3 and k4 (12, 32 and 16 pixels differ from truncation), where the footprint is 4.3125, 8.625 and 17.25 texels, the fraction 6.946/64 and the hardware reads 7/64"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Groups lod-grad (21 jobs) and lod-auto (24 jobs); T0 0x07fc0200 (MIPFILTER, point filters), a 64x64 chain; every pixel's gradient (1 + x / 64) 2^(k - 6); D3 inverts each pixel to (level, fraction); the nearest-to-neighbour choice among equal blends makes the first pixels of a row unreliable"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-p1132-tx-lod"]
terms = ["T0.MIPFILTER"]
+++

**Results.** [HW] See the claim for the counts; D3 prints the 45 jobs. Unresolved pixels (no level
and fraction gives the value) 1573 of gr-diag-k0 and 220 of gr-diag-k1: the LOD there is at or below
0. In the column x = 5 of gr-diag-k3 all 32 rows differ from truncation and the fraction is uniquely
7 on every one; in k2 and k4 the interval the blend allows holds 7 and not 6 on the 16 and 16 rows
where the interval is narrow.

**Resolution.** The per-pixel fraction is identified only where the level names differ enough
(many columns allow an interval of ten or more values), so "truncated" is a statement about the
discriminating columns: rounding to nearest fails on 22 of 64 columns at k2, and 14 columns near an
integer (x = 12, 18, 38, 39, 46, 47, 52, 56, 57, 61) read the truncated value, so the exception at
x = 5 is real; it is still one column of one footprint ladder.

**Predictions.** No declared hypothesis was exact on both the fit and the held-out sets. The
held-out off-diagonal cases (which were to test the choice, not make it) split max4 from euc as the
plan expected, and show a third behaviour (the u-term pairs).

**Inference.** [infer] That the LOD per pixel is the logarithm of a footprint is partly inference:
the diagonal cases give the logarithm directly; the other fits are by pixel counts under the model
blends, so the footprint of those cases is read through the model.

**Not shown.** The rule for gr-uu, gr-vv and gr-uvy; the rounding behind the column x = 5; whether
the footprint is a function of the two vectors' components that max4 and euc both approximate; the
minification filter at a LOD fraction under 1/2 (not run).
