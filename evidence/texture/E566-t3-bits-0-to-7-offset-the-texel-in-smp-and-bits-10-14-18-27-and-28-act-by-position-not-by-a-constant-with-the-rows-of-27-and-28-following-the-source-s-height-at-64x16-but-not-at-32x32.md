+++
id = "E566"
claim = "In smp on a strided 64x32 texture T3 bits 0 to 3 offset the row (+1, +2, +4, -8) and bits 4 to 7 the column (+1, +2, +4, -8) at every value tried (single bits, 22 flip jobs and the control, 30 single-nibble values and 16 combinations: 46 of 46 fit values exact under both declared t3off hypotheses, pre and post), T3 bits 8, 9, 11, 12, 20, 21 and 22 change nothing on that texture (2048 of 2048 pixels equal the control in each; on the twiddled 64x64 chain texture of E564 bits 11 and 12 change every pixel), and bits 10, 14, 18, 27 and 28 give images in which the decoded column and row offsets are not one constant but change with the pixel position (D6: bit 10 column 0, -1, -2 ... every 32 pixels and row 0, -1, -2 ...; bit 14 +32 and -32 over 1024 pixels each; bit 18 column 0, 1, 2 ... and row 1, 2, 3 ...; bit 27 column -1, -2, -3 and row 31, 30, 29 ...; bit 28 column -3, -6, -9 and row 37, 34, 31 ...); the rows of bits 27 and 28 follow the source's height (t3rows=after) at 64x16 (2048 of 2048 pixels each under pre/after and post/after, 0 under pre/fixed) and at 64x32 (all three agree), but at 32x32 strided bits 27 and 28 are exact under none of the three (0 of 2048); on a twiddled 32x32 bit 10 and bit 27 read as the control (2048 of 2048), bit 28 under none (0), bit 18 on 4 pixels, bits 0 and 4 offset it (1024 of 1024 under pre, 992 under post); held out, t3bits 8 of 15 (pre/after and post/after) and 6 of 15 (pre/fixed), t3vals 6 of 24 under pre and 1 of 24 under post; the declared t3off=pre and t3off=post, t3rows=after and fixed were falsified as complete models; T3 bit 13 faulted the job (r-b13: job faulted, context lost, 1 of 5 risky jobs) and so did bit 14 on a twiddled 32x32 (tw32-t3b14), the health triangle drew exactly after each"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). Script tx-t3 (111 jobs: groups t3bits and t3vals, one faulted) and tx-t3-risky (5 jobs, one faulted, run one at a time with a health check after each)"
tiers = ["HW"]
date = "2026-11-09"
data = ["texture-p1132-tx-t3", "texture-p1132-tx-t3-risky"]
terms = ["T3.BITS7_0", "T3.BIT10", "T3.BIT14", "T3.BITS19_18", "T3.BITS28_27", "T0.BIT27"]
+++

**Results.** [HW] D6 per job: the decoded (column, row) offsets and their counts; for T0 bits 27 and
30 on the strided texture the dword read is not a name of the buffer ("B", 2048 of 2048 pixels).
The fit set could not separate pre from post or after from fixed (the three hypotheses agree on 20
of 22 and 46 of 46); the held-out geometry does: rows follow the height at 64x16 and the offset
order (t3off) favours pre on the twiddled values (6 of 24 against 1 of 24), neither complete.

**Predictions.** Falsified: both offset hypotheses and both row hypotheses as complete rules (held
out 8 of 15, 6 of 15, 6 of 24, 1 of 24).

**Not shown.** The formula behind the position-dependent offsets of bits 10, 14, 18, 27 and 28; T3
bit 19 alone ran (r-b19: exact 2048 of 2048 under the table's model, no fault in this run, unlike
E274's copy). Bits 11 and 12 change nothing here and change every pixel on a twiddled chain texture
(E564): what they select is not known.
