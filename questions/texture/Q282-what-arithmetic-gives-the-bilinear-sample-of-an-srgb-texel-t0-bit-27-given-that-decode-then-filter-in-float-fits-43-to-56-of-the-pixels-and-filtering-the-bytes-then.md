+++
id = "Q282"
question = "does the bilinear sRGB sample (T0 bit 27), E982's stage rule with every stage result below 2^-14 flushed to +0 (held out offline on an-t0b27's 12 parting halves, one pixel column, E1016), flush the y stage's own subnormal result (one half parts it from a flush of the x stage's results only), where is the threshold, and does the rule hold off E723's form (other channels, negative values, other filters)"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E723", "E720", "E976", "E982", "E1004", "E1016"]
terms = ["T0.BIT27"]
+++
E723: g-bl-st-a 1147 and g-bl-st-b 876 of 2048 for decode then filter, 0 for filter then decode.
The point decode is exact (4 of 4). Candidates: the decode to float then the 1/64 weights then
half with truncation instead of rounding; the decode to half then lerp in half; a fixed-point
intermediate. To settle it: for the pixels that miss, read the half the hardware gives against the
weights and decoded corners and fit; then a held-out pair of jobs. Uses the E720 jobs' weights so
the filter weight is known.

Status: open.

Note 2026-11-13 (round 9 offline, decision X-1 a (O9-2); ranking closing9/rank/rank-round9.md
finding 3; no record, no claim settled, the question stays open). Three declared families of
bilinear sRGB arithmetic were fitted on E723's kept g-bl-st-a only, each family's best frozen by
hash before g-bl-st-b was read (closing9/rank/q282_fit.py, q282_fit2.py, q282_fit3.py; freezes
q282_rule.json 515253d3..., q282_rule2.json 5ac40e58..., q282_rule3.json b360dc66...; scored by
q282_score.py, q282_score.out). Family 1 (1404 rules: decode exact, to half or to f32; arithmetic
float, f32, lerp in half or fixed 8 to 20 bits; orders xy, yx or joint; weights 1/64 to 1/256,
truncated or rounded; half RNE, RZ or RU): best decode to half, lerp in half x then y, 1506 of 2048
pixels fit and 1189 held out (E723's frozen decode then filter: 1147 and 876). Family 2 (1728
per-stage and per-product roundings, the a + w (b - a) form): no gain (1506 and 1189). Family 3
(256 block-float forms, the corners aligned to a shared exponent of M bits): best M = 11 per pair,
1493 fit and 1340 held out. No rule is exact. The best's residuals on the fit job are +-1 half ulp
(531 below, 62 above of 4096 channels), spread over the exact value's place between halves
(q282_resid.py, q282_resid2.py): a narrower intermediate than half or float, not a rounding mode
[infer]. Weights at 1/64, 1/128 and 1/256 score the same (the fractions lie on the 1/64 grid). The
scripts import the sampler model through resgx545-data texture/p1141/recompute/lib.py, whose
texmodel.py and specs.json are byte for byte the published texture/p1141/support copies. What it
designs: a row that reads one stage at a time (v on texel centres with every x fraction, then the
other axis, then both, and equal corners as a control), the round 9 session r9-x's stage srgb.

Note 2026-11-13 (E976). r9-x ran each lerp stage alone (fy = 0, fx = 0, every 1/64 weight, known
corner pairs) and both: neither frozen rival (H-HALF2, H-BF11) is exact on any row (498 to 1009 of
2048 pixels), while a lerp of equal decoded halves returns the half. A single stage already differs
from both: the kept a and b rows are the table to fit one stage's arithmetic on, with c and E723's
g-bl-st-b held out.

Narrowed 2026-11-13 (round 10 offline, decision R10-1 a; E982; the question is not retired). One
stage that floors both halves to the larger one's ulp, lerps exactly and rounds to nearest with
ties up (A unchanged at weight 0), x then y, is exact on r9-x's single-stage rows and held out
offline on c1, c2 and E723's g-bl-st-b (and g-bl-st-a, scored after the freeze), every pixel, all
on the 1/64 weight grid. Round 10's session r10-tex then ran stage srgb2 on hardware: the rule held
on 4 of its 5 held-out rows and missed one, where none of the declared alternatives (k = round(64
f), exact weights, a floored operand at weight 0) held either; its fold records the row. Open: what
that row adds to the rule (weights off the grid, the weight-0 bypass with the smaller corner,
subnormal halves).

Note 2026-11-13 (round 10, session r10-tex, decision R10-2 a; E1004). The stage rule R10-BF11
(fitted offline on r9-x's rows) held out on hardware on four of five new rows (weights off the 1/64
grid, k = 0 with the other corner larger, two random rows) and missed the row of corners 0 to 3 on
554 of 4096 halves, each below the rule, all where a stage's result is a subnormal half; post hoc
the rule with each stage's subnormal result flushed to 0 fits every kept row [fitted]. What stays:
that flush held out (the question stays open, narrowed by E982 and E1004).

Narrowed 2026-11-13 (round 11 offline, decision R11-6 a; E1016; the question line is rewritten to
what stays, the question is not retired). It read "what arithmetic gives the bilinear sample of an
sRGB texel (T0 bit 27) given that decode-then-filter in float fits 43% to 56% of the pixels and
filtering the bytes then decoding fits none". E1004's post hoc flush, frozen by
hash with its rivals before any held-out pixel was read (closing11/plan/c2-texture/rule_b.py), held
out on p1132 tx-lod's an-t0b27, in neither E982's nor E1004's fit: 2048 of 2048 pixels and 12 of
12 on the halves where it parts from the unflushed rule (0 of 12), all in pixel column x = 4. A
flush of the x stage's results only (the final result kept) misses one of the 12, (4, 4), whose
y-stage result 5.7e-5 the hardware stores as 0: that one half is the only kept separation. sgx-sim
models the flush on the forms that ran. What stays: a row of its own for the y stage's flush and
the threshold (corners 0, 1, 0, 1 at ky 0 with kx 11 to 14,
closing11/plan/c2-texture/next_row_b.out;
the kept data put it between 5.7e-5 and 6.4e-5), and the rule off E723's form. Retire after that
row (R11-6 a).
