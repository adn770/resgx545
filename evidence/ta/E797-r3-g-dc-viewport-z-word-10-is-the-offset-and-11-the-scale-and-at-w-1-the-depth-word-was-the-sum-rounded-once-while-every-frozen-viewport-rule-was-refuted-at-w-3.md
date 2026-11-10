+++
id = "E797"
claim = "R3-geo stage g-dc (10 jobs: the viewport z words of the state block written by --blk 10 and --blk 11 on the triangle of g-da; 1 control and 9 held out): the control (blk 10 = blk 11 = 0.5 written explicitly, z = -0.5, w = 1) stored 0x3e800000 as measured before; VS (blk 10 the scale and blk 11 the offset) was refuted 9 of 9, and at w = 1 the words were 0x3dc00000 for blk 10 = 0.25, blk 11 = 0.5, z = -0.3125 and 0x3ed80000 for 0.5, 0.25 at the same z (blk 10 + blk 11 z, as VF, VT and VZ give), and 0x3eb3a2f3 for blk 10 = 0.6, blk 11 = 0.3, z = -0.830491483, which only VF gives (offset + scale z rounded once; VT, the product rounded first, gives 0x3eb3a2f2 [arithmetic]); at w = 3 with blk 10 = 0.6, blk 11 = 0.3 and z / w from -0.995 to -0.827 the six words were 0x3ea8587b (VZ only), 0x3eb42c3e (VT, VZ) and four that VF, VT and VZ all give, so VF (2 of 9), VT (2 of 9) and VZ (1 of 9) were refuted; the objects were unclipped in 9 of 9"
unit = "ta"
method = "R3-geo stage g-dc of the question-closing pass, round 3 (session L1, decision R3-G1; third of nine stages, 10 jobs, template vtx_wzclip.s), dataset render-closing-r3-geo, on the laptop (host cedar, direct cable), 2026-11-10, stage started 15:49:42 Mac time (out-l1.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 32 --pixels --tri vtxuse --width 64 --height 64 --dump-render with --blk 10 and --blk 11 setting the state block's viewport z words, all 10 of class ok (rc 0), a debugfs reset before each job; scored by the frozen score/score_r3.py g-dc (out/score-g-dc.txt); the candidates VF, VT, VZ and VS come from gen/r3models.py and, at w other than 1, all round the product z RZ(1/w) to nearest (PREFLIGHT deviation 8, before g-da decided it); the word VT gives at dc-w1-s3o6 was computed after the run (float32 arithmetic, not in the dataset)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo:out/g-dc/"]
terms = ["VIEWPORT.Z_OFFSET", "VIEWPORT.Z_SCALE", "PB_OBJ.ISP_WORDS"]
+++
**What ran.** The library writes 0.5 to both viewport z words of the MTE state block, so the depth
0.5 + 0.5 z at w = 1 (E777) does not say which word is the offset, nor how the sum rounds. G-dc
writes other values through the tool's `--blk 10` and `--blk 11`, three cells at w = 1 and six at
w = 3, against four candidates: VF (blk 10 + blk 11 x the product, rounded once), VT (the scale
product rounded first, then the sum), VZ ((z x scale) rounded, times RZ(1/w) rounded, then the sum)
and VS (the two words swapped, blk 10 the scale).

**Frozen verdict (as printed).** `controls pass; held out: consistent ['in band (x, y scaled by
w): no clip (9)'], refuted ['VF (offset (blk 10) + scale (blk 11) x ((z RZ(1/w)) to nearest), one
rounding of the sum) (2 of 9)', 'VT (the same with the scale product rounded first, then the sum)
(2 of 9)', 'VZ ((z x scale) rounded, times RZ(1/w) rounded, then the sum) (1 of 9)', 'VS (blk 10
is the scale and blk 11 the offset (order swapped), one rounding of the sum) (9 of 9)']`. The counts
are misses.

**Results [HW].** The stored depth word (the same at the three vertices) and the candidates giving
it:

| job | blk 10, blk 11 | z, w | word | candidates |
|---|---|---|---|---|
| dc-ctl-default (control) | 0.5, 0.5 | -0.5, 1 | 0x3e800000 | measured |
| dc-w1-o25s5 | 0.25, 0.5 | -0.3125, 1 | 0x3dc00000 | VF, VT, VZ |
| dc-w1-o5s25 | 0.5, 0.25 | -0.3125, 1 | 0x3ed80000 | VF, VT, VZ |
| dc-w1-s3o6 | 0.6, 0.3 | -0.830491483, 1 | 0x3eb3a2f3 | VF |
| dc-wn1 | 0.6, 0.3 | -2.712, 3 | 0x3ea8587b | VZ |
| dc-wn2 | 0.6, 0.3 | -2.481, 3 | 0x3eb42c3e | VT, VZ |
| dc-wn3 | 0.6, 0.3 | -2.985, 3 | 0x3e9a5e37 | VF, VT, VZ |
| dc-wn4 | 0.6, 0.3 | -2.964, 3 | 0x3e9b7177 | VF, VT, VZ |
| dc-wn5 | 0.6, 0.3 | -2.943, 3 | 0x3e9c84b7 | VF, VT, VZ |
| dc-wn6 | 0.6, 0.3 | -2.922, 3 | 0x3e9d97f7 | VF, VT, VZ |

The 1/w at w = 3 was 0x3eaaaaaa (RZ of 1/3) in the six jobs. At dc-w1-s3o6 the two roundings of
VT give 0x3eb3a2f2, one unit below the stored word [arithmetic after the run].

**What it shows and does not.** Word 10 of the state block is the viewport's z offset and word 11
its z scale: the swap gave none of the nine words (held out). At w = 1 the three words are offset
+ scale x z, and the one cell that separates the roundings (dc-w1-s3o6) took the sum rounded once,
not the product rounded first; one cell, so a single rounding at w = 1 is what was seen, not a rule
tested across many cells. At w = 3 no candidate fits all six; all of them used the product to
nearest, the rule g-da refuted (E795), so their misses there do not separate the viewport's
rounding from the depth's. The depth at w other than 1 stays without a formula (Q230).
