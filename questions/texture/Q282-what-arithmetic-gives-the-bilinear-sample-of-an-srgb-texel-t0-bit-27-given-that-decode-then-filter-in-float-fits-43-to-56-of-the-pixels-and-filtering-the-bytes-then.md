+++
id = "Q282"
question = "what arithmetic gives the bilinear sample of an sRGB texel (T0 bit 27) given that decode-then-filter in float fits 43% to 56% of the pixels and filtering the bytes then decoding fits none"
unit = "texture"
kind = "hw"
value = "low"
phase = 11
evidence = ["E723", "E720"]
terms = ["T0.BIT27"]
+++
E723: g-bl-st-a 1147 and g-bl-st-b 876 of 2048 for decode then filter, 0 for filter then decode.
The point decode is exact (4 of 4). Candidates: the decode to float then the 1/64 weights then
half with truncation instead of rounding; the decode to half then lerp in half; a fixed-point
intermediate. To settle it: for the pixels that miss, read the half the hardware gives against the
weights and decoded corners and fit; then a held-out pair of jobs. Uses the E720 jobs' weights so
the filter weight is known.

Status: open.
