+++
id = "E565"
claim = "On a 16x16 twiddled texture with u swept over 64 positions (-1.5 + (x + 1/2) / 16, a pitch of one texel) or v swept over 32 positions (-1.5 + (y + 1/2) / 8, a pitch of two texels) the modes 0 to 3 reproduce E033 in 12 of 12 control jobs (every declared mode47 hypothesis agrees on them); for modes 4 to 7 on the v axis (u inside) mode 6 and mode 7 read exactly the clamp image (bd-v6, bd-v7: 2048 of 2048 pixels each) and mode 4 and mode 5 read the repeat image, the same as mode 0 (bd-v4, bd-v5: 576 of 2048 pixels equal the clamp model, and D5's row and column decode are those of bd-v0), while on the u axis (v inside) and on both modes 4 to 7 read other texels, some of them indices past the 256 of the texture (+324 to +366 in the row of y = 8 in every one of modes 4 to 7; in modes 5 to 7 the first columns read texels inside the texture), no u-sweep job exact under clamp or border (0 of 4 each) and under nomask at most 4 of 2048 pixels, and the held-out jobs on another base address and a 32x8 texture read no hypothesis exactly (the 8 jobs: at most 4 of 2048 pixels under any; the 5 of 13 held-out jobs exact under each hypothesis are the strided texture's, where modes 4 to 7 read the clamp image of mode 0: bd-st-u0, u4, u5, u6, u7, 2048 of 2048 pixels equal for every hypothesis); the declared hypotheses mode47=clamp, nomask and border were falsified for the u axis"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Group border (37 jobs: the control 12, explore 12, held out 13); the v axis has half the positions of the u axis and a pitch of two texels, which could hide an effect of odd rows"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1132-tx-border"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++

**Results.** [HW] D5 prints the decoded (x, y) along row 8 and column 8 for each job; the v axis in
modes 6 and 7 is the clamp of mode 2 (column x = 8: 2,0 ... 2,15), in 4 and 5 the repeat of mode 0.
The u axis in modes 4 to 7 repeats a pattern of period 16 or 6 positions with values outside the
texture in part of the row.

**Predictions.** Control 12 of 12 held; the explore and held-out jobs were not predicted by any
declared mode47 rule (explore: clamp 2 of 12, the two v-axis jobs of modes 6 and 7; held out 5 of
13, all five the strided texture).

**Not shown.** What the indices past the texture are (a layout of memory past the buffer, 24 pages
here); the mode bits read other than T0 8:6 and 5:3 for the second axis; the v axis at a pitch of
one texel.
