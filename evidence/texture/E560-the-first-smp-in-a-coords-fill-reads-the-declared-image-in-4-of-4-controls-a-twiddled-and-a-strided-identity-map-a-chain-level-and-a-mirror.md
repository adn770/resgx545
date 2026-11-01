+++
id = "E560"
claim = "In a --coords --pixels fill of 2048 pixels (pa0 = (y << 16) | x, each pixel building its own coordinates and doing one smp) the four gate controls read the declared image under their hypotheses in 4 of 4 jobs (g1-tw16 a 16x16 twiddled identity map, g2-st64x32 a 64x32 strided one, g3-tw16-lod2 LOD 2 of a chain, g4-tw16-u-mirror a mirror), 4 of 4 again in the second run of the gate that run-all-1132.sh made (the dumps of the first run kept apart), the health triangle exact after each; this is the first smp of ours that ran in a --coords fill"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). tx-gate run twice: alone (texture/p1132-gate-first) and as the first script of run-all-1132.sh"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1132-gate-first", "texture-p1132-tx-gate", "texture-p1132-run"]
terms = ["T0.BITS26_21"]
+++

**Results.** [HW] The pixel sha256 of g1 2b49c848..., g2 ca07c5b2..., g3 9ac52e7e... and g4
3d143b0f... equal the declared ones (MATCH 4 of 4, both runs). g2 reads 2048 distinct names, g1 256,
g3 16 and g4 256.

**Not shown.** That the tri host fallback of the plan works (not built, not needed).
