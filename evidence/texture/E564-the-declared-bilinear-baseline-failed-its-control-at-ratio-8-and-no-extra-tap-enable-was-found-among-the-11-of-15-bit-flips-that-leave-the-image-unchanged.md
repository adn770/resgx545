+++
id = "E564"
claim = "With bilinear filters and explicit gradients of five ratios (an-r1 to an-r5, ratios 2 to 32) none of the 2048-pixel images is exactly any declared single-level bilinear formula (lodf = euc, max4 and min: 0 of 5 jobs each; pixels equal to max4 and euc 1279, 1540, 1528, 1580 and 1792, to min 391, 0, 0, 0 and 0); the declared control an-ctl (ratio 8) did not match either (1528 of 2048 pixels under max4 and euc, 0 under min; the script printed MISMATCH against the declared hash b80690ea...), so the baseline, one bilinear tap at the level the footprint picks, is not established and the five ratios and the flips have no reference to be compared with; of the 15 bit flips at ratio 8 eleven give the control's image exactly (T0 bits 14, 15, 16, 28, 29 and T3 bits 8, 9, 15, 20, 21, 22), so those 11 bits do not change this image, and four change every pixel (2048 of 2048 pixels differ from the control, 0 of 2048 equal any declared formula): T3 bit 11 (cleared from the control's 0x00800800) reads 2048 distinct names from the start of level 0 (0xd0000000, 0xd0000002, 0xd0000008, ...), T3 bit 12 (set) reads the constant 0xd0001554, and T0 bits 27 and 30 read values that are no name of the buffer (935 and 90 distinct values, the first 0x1fae245d and 0x7f9c0000); no anisotropic filtering was identified, and none could be told from the failed baseline, so nothing is claimed about whether the core has it"
unit = "texture"
method = "probes/texture/tx-*.toml of phase 11.32 (probes/texture/templates/tx_map.s: one program, 2048 pixels a fill, pa0 = (y << 16) | x, each pixel one smp, the scratch buffer the texture, dword i = 0xD0000000 | i) run by probes/texture/templates/run-all-1132.sh on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 5AD04F33F6BCDA7B880E238 (installed and loaded alike), tool sgxfive-test-1126 sha256 751f7223...f82e, stock firmware; tools/texture/p1132/declared.tsv sha256 9395f6dd...7b2a and predictions-declared.tsv sha256 4ee35db3...84beb hashed before the first run (the runs began at 02:36:08, the hashes were written at 00:38) and unchanged; no register written, only debugfs reset and /dev/kmsg; raw dumps gzipped under resgx545-data/texture/p1132/<script>/ with the case tables, the stdout of each script in texture/p1132/stdout/ and the kernel logs; recomputed by tools/texture/p1132/recompute/recompute_p1132.py (declared predictions the model no longer renders: 0). The anisotropy group (21 jobs: five ratios, the control, 15 flips; an-r3 is the same image as an-ctl); the control failed its declared prediction, which per the plan's own rule makes the baseline model failed"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["texture-p1132-tx-lod"]
terms = ["T0.MAGFILTER", "T0.MINFILTER"]
+++

**Results.** [HW] D4 lists, per job, exact pixels under max4, euc and min and the pixels that differ
from the control. The 1528 to 1792 agreement is partial for every ratio, including the control, so
the single-level bilinear formula of the plan is not what the hardware reads at these gradients (the
part that disagrees is not analysed here: [infer] the rounding of E563 acts first).

**T3 bits 11 and 12.** On the strided 64x32 texture of E566 these two bits change nothing (2048 of
2048 pixels equal the control in each); on the twiddled 64x64 chain texture here they change every
pixel, bit 11 cleared to the identity-looking names of level 0 and bit 12 set to one constant. They
act on a twiddled chain texture, which bears on Q078 (the unexplained T3 bits) and is not an
anisotropy result.

**Predictions.** The declared anisotropy hypotheses (one bilinear level under each footprint
formula) were falsified on all five fit jobs (0 of 5) and on the control (0 of 1).

**Not shown.** Anything about a closed-driver anisotropy request (a capture), bits other than those
listed, and an image that is a mean of taps: none of the images was tested for it beyond D4. With
the control failed there is no baseline against which to call an image "one tap" or "more".

**Correction 2026-11-13:** Round 11 offline (closing11/plan/rank-round11.md finding 8, decision
R11-8 a; closing11/plan/c8-q078/, a decode written after reading these images: post hoc, no
held-out job). Under the counting fill every dword of the 64 x 64 chain names itself, and E561's
tile law with E722's offset chain (levels at dwords 0, 4096, 5120, 5376, 5440, 5456, 5460) maps
the 5461 names one to one. With T3 bit 11 cleared every pixel reads level 0's texel (x, y), 2048
of 2048 distinct names (the control reads levels 3 and 4); with bit 12 set every pixel reads
dword 5460, the 1 x 1 level 6, so the claim's "constant 0xd0001554" is the last level of the
chain. A forced level, mips off and a LOD bias of -3.5 or less (bit 11) or +2.5 or more (bit 12)
give the same images here, and so do the last level and a constant dword; nearest and bilinear are
not told apart. The T0 bit 27 job an-t0b27 decodes as E982's bilinear sRGB rule with subnormal
stage results flushed to +0, 2048 of 2048 (E1016). The measurements are unchanged.
