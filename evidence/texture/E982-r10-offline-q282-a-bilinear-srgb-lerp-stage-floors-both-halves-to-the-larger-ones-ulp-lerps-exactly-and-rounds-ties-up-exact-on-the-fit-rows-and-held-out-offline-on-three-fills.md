+++
id = "E982"
claim = "Round 10 offline (Q282; no run): one lerp stage of a bilinear sRGB sample (T0 bit 27) on two decoded halves A (weight 64 - k) and B (weight k) returns A unchanged at k = 0 and otherwise floors both to the grid 2^(e - 11), e the larger frexp exponent of the two (an 11-bit mantissa shared at the larger one's exponent: the larger half's ulp), lerps exactly and rounds to a half to nearest with ties up (R10-BF11); fitted on r9-x's single-stage rows a1, a2, b1 and b2 (16384 of 16384 halves) and frozen by hash with both stage orders declared, it holds out offline with x first then y on r9-x's two-stage c1 and c2 and E723's g-bl-st-b, 2048 of 2048 pixels each (y first: 536 to 773) [HW, held out offline]; E723's g-bl-st-a, scored only after the freeze by sgx-sim, is exact too (2048 of 2048); weights off the 1/64 grid, k = 0 with the smaller corner as B and subnormal halves never ran"
unit = "texture"
method = "Offline, no run (round 10, decision R10-1 a of the seeds plan closing10/seeds/exp-seeds-r10.md, finding 1 and section 1). Data: r9-x stage srgb's kept rows (render-closing-r9-x out/20261113-081821/srgb/: a1, a2 the x stage alone, b1, b2 the y stage alone, c1, c2 both, corners and weights from the session's gen/srgb.py) and E723's kept fills g-bl-st-a and g-bl-st-b (texture/p1141, read through closing9/rank/q282_fit.py). The planner's scripts in closing10/seeds/q282/ (numpy, the repository's .venv): q282_r10_data.py and q282_r10_tab.py build the per-channel table (bytes, weight k of 64, the hardware's half) of the four single-stage rows; q282_r10_rules.py declares the families and q282_r10_fit.py, q282_r10_fit2.py and q282_r10_fit3.py score 95512, 5940 and 43740 rules on the fit set (block-float on a shared exponent, fixed point, per-step mantissas, weighted-term and difference alignments), best 16287 of 16384 halves (a shared 11-bit mantissa at the larger exponent, floor, round half up); look1.py to look5.py read the misses, all 97 at k = 0, where the hardware returns A; q282_r10_frozen.py is the rule with that bypass and q282_r10_fitscore.py scores it 16384 of 16384 on the fit set; q282_r10_rule.json (sha256 e9623e35...) freezes it with the XY and YX two-stage forms declared (file times: frozen.py 09:25:09, rule 09:25:27, held-out output 09:25:39); q282_r10_heldout.py checks the hash and scores c1, c2 and g-bl-st-b; q282_r10_ablate.py varies one part at a time on the fit set. Caveat: the table builder's smoke test (q282_r10_data.py run as a script) printed six entries of c1's table before the fit; nothing was fitted or scored on them. This fold re-ran q282_r10_fitscore.py, q282_r10_heldout.py and q282_r10_ablate.py with python -I -B and got byte-identical outputs, then modelled the rule in sgx-sim (tex.rs srgb_stage, srgb_bilinear) and replayed both of E723's bilinear fills in crates/sgx-pipe/tests/texture_p1141.rs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/srgb/", "texture-isp-msaa-verification-1141", "cited-scratch:closing10/seeds/q282/"]
terms = ["T0.BIT27"]
+++
**What was done.** E976 ran each lerp stage of a bilinear sRGB sample alone (fy = 0 with every 1/64
x weight, fx = 0 with every y weight, known corner pairs) and both together, and neither frozen
rival held on any row. The round 10 seeds planner fitted one stage's arithmetic on E976's four
single-stage rows only, froze the one exact rule by hash with both orders of the two stages
declared, and then scored the two-stage rows c1 and c2 and E723's g-bl-st-b. This fold re-ran the
scoring scripts (byte-identical outputs), put the rule into sgx-sim and replayed E723's two
bilinear fills through it.

**The rule (R10-BF11).** Each corner byte is decoded to a half as E723's point sample does (the
sRGB curve in double, rounded to nearest even). A stage on two halves A (weight 64 - k) and B
(weight k), k from 0 to 63:
- k = 0: A, unchanged;
- otherwise g = 2^(e - 11), e the frexp exponent of the larger of A and B (g is the larger
  half's ulp); A' = floor(A / g) g and B' = floor(B / g) g; the result A' + (k / 64)(B' - A'),
  exact,
  rounded to a half to nearest, ties up.

The sample filters bytes 0 and 1 of the four texels: x on both rows, then y on the two results.

**Results [HW].** Fit (16384 halves of 8192 pixels): the rule 16384 of 16384. The best of the
145192 declared rules without the bypass was 16287; its 97 misses were all at k = 0 (read post hoc
on the fit set, which formed the bypass). One part changed at a time (q282_r10_ablate.out): no
bypass 16287, rounding to nearest even 15817, toward zero 8859, a 10-bit grid 6932, a 12-bit grid
13504, the inputs rounded instead of floored 13256. Held out (q282_r10_heldout.out, the hash
checked first): x then y on c1 and c2, 4096 of 4096 halves and 2048 of 2048 pixels each, and on
E723's g-bl-st-b 4096 of 4096 halves and 2048 of 2048 pixels; y then x 585, 536 and 773 pixels.
After the freeze, E723's g-bl-st-a, which this rule's fit never saw (round 9's families were fitted
on it), is exact as well through sgx-sim: `bilinear_srgb_equals_e723s_fills_by_e982s_stage_rule`
in crates/sgx-pipe/tests/texture_p1141.rs samples every pixel of both fills, 2048 of 2048 each.

**What it shows.** [HW, held out offline] The first register of a bilinear sRGB sample on the 1/64
weight grid is two such stages, x first, on halves of the decoded bytes, on three fills that the
fit did not use (and a fourth scored after the freeze). It is round 9's best family (an 11-bit
mantissa shared at the larger exponent) with the operands floored, the result rounded half up and
the bypass at weight 0. [infer] The data path is a half lerp unit that aligns both operands to the
larger exponent with one guard bit and truncates; nothing here says how it is built.

**What it does not show.** Every held-out weight lay on the 1/64 grid, so a weight between grid
points (k = floor(64 f) against rounding, or finer weights) is untested; k = 0 with B the smaller
corner, subnormal halves (corner bytes 1 to 3) and random corner pairs did not run (the seeds
plan's stage srgb2 lists rows for each). Only bytes 0 and 1, the first register, 8 x 8 strided
textures of E723's state words and r9-x's are covered; the second register (E723's r11) and other
formats, sizes and texture types stay unmodelled. sgx-sim models the rule on E723's bilinear state
words only and refuses the rest.
